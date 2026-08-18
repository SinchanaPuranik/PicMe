from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Event, Photo, FaceEmbedding, PerformanceMetric
from app.routes import admin_bp
from app.services.face_detection import detect_faces_in_image
from app.services.facenet_service import FaceNetService
from app.services.arcface_service import ArcFaceService
from datetime import datetime
import os
import qrcode


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    events = Event.query.order_by(Event.created_at.desc()).all()
    total_photos = Photo.query.count()
    total_faces = FaceEmbedding.query.count()
    return render_template('admin/dashboard.html', 
                         events=events, 
                         total_photos=total_photos,
                         total_faces=total_faces)


@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        
        # Parse date
        try:
            event_date = datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'danger')
            return render_template('admin/create_event.html')
        
        # Create event
        event = Event(
            name=name,
            description=description,
            event_date=event_date,
            location=location,
            creator_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Generate QR code
        qr_data = url_for('user.select_event', event_id=event.id, _external=True)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_filename = f"event_{event.id}_qr.png"
        qr_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events', qr_filename)
        qr_img.save(qr_path)
        
        event.qr_code_path = qr_filename
        db.session.commit()
        
        flash(f'Event "{name}" created successfully!', 'success')
        return redirect(url_for('admin.view_event', event_id=event.id))
    
    return render_template('admin/create_event.html')


@admin_bp.route('/events/<int:event_id>')
@login_required
@admin_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    photos = Photo.query.filter_by(event_id=event_id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('admin/view_event.html', event=event, photos=photos)


@admin_bp.route('/events/<int:event_id>/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_photos(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        if 'photos' not in request.files:
            flash('No photos selected', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        uploaded_count = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{event_id}_{timestamp}_{filename}"
                
                # Create event directory if not exists
                event_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events', str(event_id))
                os.makedirs(event_dir, exist_ok=True)
                
                filepath = os.path.join(event_dir, filename)
                file.save(filepath)
                
                # Save photo record
                photo = Photo(
                    filename=filename,
                    filepath=filepath,
                    event_id=event_id
                )
                db.session.add(photo)
                uploaded_count += 1
        
        db.session.commit()
        flash(f'{uploaded_count} photos uploaded successfully!', 'success')
        return redirect(url_for('admin.upload_photos', event_id=event_id))
    
    return render_template('admin/upload_photos.html', event=event)


@admin_bp.route('/events/<int:event_id>/process', methods=['GET', 'POST'])
@login_required
@admin_required
def process_photos(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Reset the event embedding set before a fresh scan so only current
        # photos remain in the database for this event.
        event.reset_event_embeddings()
        db.session.commit()

        photos = Photo.query.filter_by(event_id=event_id).all()
        
        if not photos:
            flash('No photos found to process', 'info')
            return redirect(url_for('admin.view_event', event_id=event_id))
        
        # Initialize face recognition services
        facenet_service = FaceNetService()
        arcface_service = ArcFaceService()
        
        processed_count = 0
        total_faces = 0
        
        for photo in photos:
            try:
                # Detect faces
                faces = detect_faces_in_image(photo.filepath)
                photo.num_faces = len(faces)
                
                for face_img, box in faces:
                    # Generate FaceNet embedding
                    facenet_embedding = facenet_service.generate_embedding(face_img)
                    if facenet_embedding is not None:
                        fe = FaceEmbedding(photo_id=photo.id, model_type='facenet')
                        fe.set_embedding(facenet_embedding)
                        fe.set_face_box(box)
                        db.session.add(fe)
                    
                    # Generate ArcFace embedding
                    arcface_embedding = arcface_service.generate_embedding(face_img)
                    if arcface_embedding is not None:
                        fe = FaceEmbedding(photo_id=photo.id, model_type='arcface')
                        fe.set_embedding(arcface_embedding)
                        fe.set_face_box(box)
                        db.session.add(fe)
                    
                    total_faces += 1
                
                photo.processed = True
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing photo {photo.id}: {str(e)}")
                continue
        
        db.session.commit()
        
        flash(f'Processed {processed_count} photos with {total_faces} faces detected!', 'success')
        return redirect(url_for('admin.view_event', event_id=event_id))
    
    unprocessed_photos = Photo.query.filter_by(event_id=event_id, processed=False).all()
    return render_template('admin/process_photos.html', event=event, photos=unprocessed_photos)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete event photos from filesystem
    event_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events', str(event_id))
    if os.path.exists(event_dir):
        import shutil
        shutil.rmtree(event_dir)
    
    # Delete QR code
    if event.qr_code_path:
        qr_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events', event.qr_code_path)
        if os.path.exists(qr_path):
            os.remove(qr_path)
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/metrics')
@login_required
@admin_required
def view_metrics():
    metrics = PerformanceMetric.query.order_by(PerformanceMetric.timestamp.desc()).all()
    return render_template('admin/metrics.html', metrics=metrics)


@admin_bp.route('/photos/<int:photo_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_photo(photo_id):
    """Delete a photo and its associated embeddings
    
    Returns:
        JSON response with success/error status
    """
    try:
        # Fetch photo record
        photo = Photo.query.get_or_404(photo_id)
        
        # Validate filepath to prevent path traversal
        filepath_abs = os.path.abspath(photo.filepath)
        upload_folder_abs = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        
        if not filepath_abs.startswith(upload_folder_abs):
            current_app.logger.warning(
                f"[SECURITY] Path traversal attempt: user={current_user.id} "
                f"photo={photo_id} filepath={photo.filepath}"
            )
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 400
        
        # Attempt file deletion (non-critical)
        if os.path.exists(filepath_abs):
            try:
                os.remove(filepath_abs)
                current_app.logger.info(
                    f"[PHOTO_DELETE] user={current_user.id} photo={photo_id} "
                    f"file_deleted=success filepath={filepath_abs}"
                )
            except OSError as e:
                current_app.logger.error(
                    f"[PHOTO_DELETE] user={current_user.id} photo={photo_id} "
                    f"file_deleted=error error='{str(e)}' filepath={filepath_abs}"
                )
                # Continue with database deletion even if file deletion fails
        else:
            current_app.logger.warning(
                f"[PHOTO_DELETE] user={current_user.id} photo={photo_id} "
                f"file_deleted=not_found filepath={filepath_abs}"
            )
        
        # Delete from database (triggers cascade delete of embeddings)
        db.session.delete(photo)
        db.session.commit()
        
        current_app.logger.info(
            f"[PHOTO_DELETE] user={current_user.id} photo={photo_id} status=success"
        )
        
        return jsonify({
            'success': True,
            'message': 'Photo deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"[PHOTO_DELETE] user={current_user.id} photo={photo_id} "
            f"status=error error='{str(e)}'"
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
