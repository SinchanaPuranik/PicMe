from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Event, Photo, FaceEmbedding, PerformanceMetric
from app.routes import admin_bp

from app.services.face_detection import (
    detect_faces_in_image,
    get_available_detectors
)

from app.services.facenet_service import FaceNetService
from app.services.arcface_service import ArcFaceService

from datetime import datetime, timedelta

import os
import qrcode


# ============================================================
# ADMIN ACCESS
# ============================================================

def admin_required(f):

    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated or not current_user.is_admin:

            flash(
                'Admin access required',
                'danger'
            )

            return redirect(
                url_for('auth.login')
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(filename):

    return (
        '.' in filename
        and
        filename.rsplit('.', 1)[1].lower()
        in current_app.config['ALLOWED_EXTENSIONS']
    )


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():

    events = Event.query.order_by(
        Event.created_at.desc()
    ).all()

    total_photos = Photo.query.count()

    total_faces = FaceEmbedding.query.count()

    return render_template(
        'admin/dashboard.html',
        events=events,
        total_photos=total_photos,
        total_faces=total_faces
    )


# ============================================================
# CREATE EVENT
# ============================================================

@admin_bp.route(
    '/events/create',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def create_event():

    if request.method == 'POST':

        name = request.form.get('name')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')

        try:

            event_date = datetime.strptime(
                event_date,
                '%Y-%m-%d'
            )

        except (ValueError, TypeError):

            flash(
                'Invalid date format',
                'danger'
            )

            return render_template(
                'admin/create_event.html'
            )

        event = Event(
            name=name,
            description=description,
            event_date=event_date,
            location=location,
            creator_id=current_user.id
        )

        db.session.add(event)

        db.session.commit()

        # ----------------------------------------------------
        # Generate QR code
        # ----------------------------------------------------

        qr_data = url_for(
            'user.select_event',
            event_id=event.id,
            _external=True
        )

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )

        qr.add_data(qr_data)

        qr.make(
            fit=True
        )

        qr_img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        events_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'events'
        )

        os.makedirs(
            events_dir,
            exist_ok=True
        )

        qr_filename = (
            f"event_{event.id}_qr.png"
        )

        qr_path = os.path.join(
            events_dir,
            qr_filename
        )

        qr_img.save(qr_path)

        event.qr_code_path = qr_filename

        db.session.commit()

        flash(
            f'Event "{name}" created successfully!',
            'success'
        )

        return redirect(
            url_for(
                'admin.view_event',
                event_id=event.id
            )
        )

    return render_template(
        'admin/create_event.html'
    )


# ============================================================
# VIEW EVENT
# ============================================================

@admin_bp.route(
    '/events/<int:event_id>'
)
@login_required
@admin_required
def view_event(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    photos = (
        Photo.query
        .filter_by(event_id=event_id)
        .order_by(
            Photo.uploaded_at.desc()
        )
        .all()
    )

    return render_template(
        'admin/view_event.html',
        event=event,
        photos=photos
    )


# ============================================================
# UPLOAD PHOTOS
# ============================================================

@admin_bp.route(
    '/events/<int:event_id>/upload',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def upload_photos(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    if request.method == 'POST':

        if 'photos' not in request.files:

            flash(
                'No photos selected',
                'danger'
            )

            return redirect(
                request.url
            )

        files = request.files.getlist(
            'photos'
        )

        uploaded_count = 0

        event_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'events',
            str(event_id)
        )

        os.makedirs(
            event_dir,
            exist_ok=True
        )

        for file in files:

            if file and allowed_file(
                file.filename
            ):

                filename = secure_filename(
                    file.filename
                )

                timestamp = datetime.now().strftime(
                    '%Y%m%d_%H%M%S_%f'
                )

                filename = (
                    f"{event_id}_"
                    f"{timestamp}_"
                    f"{filename}"
                )

                filepath = os.path.join(
                    event_dir,
                    filename
                )

                file.save(
                    filepath
                )

                photo = Photo(
                    filename=filename,
                    filepath=filepath,
                    event_id=event_id
                )

                db.session.add(
                    photo
                )

                uploaded_count += 1

        db.session.commit()

        flash(
            f'{uploaded_count} photos uploaded successfully!',
            'success'
        )

        return redirect(
            url_for(
                'admin.upload_photos',
                event_id=event_id
            )
        )

    return render_template(
        'admin/upload_photos.html',
        event=event
    )


# ============================================================
# PROCESS PHOTOS
# ============================================================

@admin_bp.route(
    '/events/<int:event_id>/process',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def process_photos(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    if request.method == 'POST':

        detector = request.form.get(
            'detector',
            'mtcnn'
        )

        try:

            min_confidence = float(
                request.form.get(
                    'min_confidence',
                    0.7
                )
            )

        except (ValueError, TypeError):

            min_confidence = 0.7

        # ----------------------------------------------------
        # Reset embeddings for fresh processing
        # ----------------------------------------------------

        event.reset_event_embeddings()

        db.session.commit()

        photos = (
            Photo.query
            .filter_by(event_id=event_id)
            .all()
        )

        if not photos:

            flash(
                'No photos found to process',
                'info'
            )

            return redirect(
                url_for(
                    'admin.view_event',
                    event_id=event_id
                )
            )

        # ----------------------------------------------------
        # Recognition services
        # ----------------------------------------------------

        facenet_service = FaceNetService()
        arcface_service = ArcFaceService()

        processed_count = 0
        total_faces = 0

        for photo in photos:

            try:

                faces = detect_faces_in_image(
                    photo.filepath,
                    detector=detector,
                    min_confidence=min_confidence
                )

                photo.num_faces = len(
                    faces
                )

                for face_data in faces:

                    if len(face_data) == 2:

                        face_img, box = face_data

                    else:

                        face_img, box, landmarks = face_data

                    # ------------------------------------------------
                    # FaceNet
                    # ------------------------------------------------

                    try:

                        facenet_embedding = (
                            facenet_service.generate_embedding(
                                face_img
                            )
                        )

                        if facenet_embedding is not None:

                            fe = FaceEmbedding(
                                photo_id=photo.id,
                                model_type='facenet'
                            )

                            fe.set_embedding(
                                facenet_embedding
                            )

                            fe.set_face_box(
                                box
                            )

                            db.session.add(
                                fe
                            )

                    except Exception as e:

                        current_app.logger.error(
                            f"FaceNet error for photo "
                            f"{photo.id}: {str(e)}"
                        )

                    # ------------------------------------------------
                    # ArcFace
                    # ------------------------------------------------

                    try:

                        arcface_embedding = (
                            arcface_service.generate_embedding(
                                face_img
                            )
                        )

                        if arcface_embedding is not None:

                            fe = FaceEmbedding(
                                photo_id=photo.id,
                                model_type='arcface'
                            )

                            fe.set_embedding(
                                arcface_embedding
                            )

                            fe.set_face_box(
                                box
                            )

                            db.session.add(
                                fe
                            )

                    except Exception as e:

                        current_app.logger.error(
                            f"ArcFace error for photo "
                            f"{photo.id}: {str(e)}"
                        )

                    total_faces += 1

                photo.processed = True

                processed_count += 1

            except Exception as e:

                current_app.logger.exception(
                    f"Error processing photo "
                    f"{photo.id}: {str(e)}"
                )

                continue

        db.session.commit()

        flash(
            f'Processed {processed_count} photos '
            f'with {total_faces} faces detected '
            f'using {detector.upper()} detector!',
            'success'
        )

        return redirect(
            url_for(
                'admin.view_event',
                event_id=event_id
            )
        )

    unprocessed_photos = (
        Photo.query
        .filter_by(
            event_id=event_id,
            processed=False
        )
        .all()
    )

    available_detectors = (
        get_available_detectors()
    )

    return render_template(
        'admin/process_photos.html',
        event=event,
        photos=unprocessed_photos,
        available_detectors=available_detectors
    )


# ============================================================
# DELETE EVENT
# ============================================================

@admin_bp.route(
    '/events/<int:event_id>/delete',
    methods=['POST']
)
@login_required
@admin_required
def delete_event(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    event_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'events',
        str(event_id)
    )

    if os.path.exists(event_dir):

        import shutil

        shutil.rmtree(
            event_dir
        )

    db.session.delete(
        event
    )

    db.session.commit()

    flash(
        'Event deleted successfully',
        'success'
    )

    return redirect(
        url_for('admin.dashboard')
    )


# ============================================================
# METRICS
# ============================================================

@admin_bp.route('/metrics')
@login_required
@admin_required
def view_metrics():

    from app.models import (
        SearchRetrieval,
        DetectorEvaluation,
        TestImage
    )

    from app.services.detector_evaluator import (
        DetectorEvaluator
    )

    searches = (
        SearchRetrieval.query
        .all()
    )

    total_searches = len(
        searches
    )

    if searches:

        avg_matches = (
            sum(
                s.num_matches
                for s in searches
            )
            /
            total_searches
        )

        processing_times = [
            s.processing_time_ms
            for s in searches
            if s.processing_time_ms is not None
        ]

        avg_time = (
            sum(processing_times)
            /
            len(processing_times)
            if processing_times
            else 0
        )

    else:

        avg_matches = 0
        avg_time = 0

    detector_results = (
        DetectorEvaluator
        .get_latest_evaluation_results()
    )

    has_evaluation_data = any(
        detector_results.values()
    )

    if has_evaluation_data:

        valid_detector_data = [
            (name, data)
            for name, data
            in detector_results.items()
            if data
        ]

        best_detector = max(
            valid_detector_data,
            key=lambda x: x[1].get(
                'f1_score',
                0
            )
        )

        best_detector_name = (
            best_detector[0]
        )

        best_f1_score = (
            best_detector[1].get(
                'f1_score',
                0
            )
        )

        valid_data = [
            data
            for data
            in detector_results.values()
            if data
        ]

        speed_values = [
            data.get(
                'avg_speed',
                0
            )
            for data in valid_data
        ]

        avg_processing = (
            sum(speed_values)
            /
            len(speed_values)
            if speed_values
            else 0
        )

        num_test_images = (
            TestImage.query
            .filter_by(
                is_annotated=True
            )
            .count()
        )

    else:

        best_detector_name = None

        best_f1_score = 0

        avg_processing = 0

        num_test_images = 0

    # NOTE:
    # These are still your existing placeholder
    # recognition metrics.
    # They are NOT used for detector evaluation.

    model_accuracy = {

        'facenet': {
            'f1_score': 88.0,
            'precision': 91.0,
            'recall': 85.0
        },

        'arcface': {
            'f1_score': 93.0,
            'precision': 94.0,
            'recall': 92.0
        }

    }

    return render_template(
        'admin/metrics.html',

        searches=searches,

        total_searches=total_searches,

        avg_matches=round(
            avg_matches,
            1
        ),

        avg_time=round(
            avg_time,
            1
        ),

        detector_results=detector_results,

        has_evaluation_data=has_evaluation_data,

        best_detector_name=best_detector_name,

        best_f1_score=round(
            best_f1_score,
            1
        ) if best_f1_score else 0,

        avg_processing=round(
            avg_processing,
            3
        ),

        num_test_images=num_test_images,

        model_accuracy=model_accuracy
    )


# ============================================================
# DELETE PHOTO
# ============================================================

@admin_bp.route(
    '/photos/<int:photo_id>/delete',
    methods=['DELETE']
)
@login_required
@admin_required
def delete_photo(photo_id):

    try:

        photo = Photo.query.get_or_404(
            photo_id
        )

        filepath_abs = os.path.abspath(
            photo.filepath
        )

        upload_folder_abs = os.path.abspath(
            current_app.config['UPLOAD_FOLDER']
        )

        # ----------------------------------------------------
        # Security check
        # ----------------------------------------------------

        if not (
            filepath_abs == upload_folder_abs
            or
            filepath_abs.startswith(
                upload_folder_abs + os.sep
            )
        ):

            current_app.logger.warning(
                f"[SECURITY] Invalid path "
                f"user={current_user.id} "
                f"photo={photo_id}"
            )

            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 400

        # ----------------------------------------------------
        # Delete physical file
        # ----------------------------------------------------

        if os.path.exists(
            filepath_abs
        ):

            try:

                os.remove(
                    filepath_abs
                )

            except OSError as e:

                current_app.logger.error(
                    f"Photo file deletion error: "
                    f"{str(e)}"
                )

        # ----------------------------------------------------
        # Delete DB record
        # ----------------------------------------------------

        db.session.delete(
            photo
        )

        db.session.commit()

        return jsonify({
            'success': True,
            'message':
                'Photo deleted successfully'
        }), 200

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            "Photo deletion failed"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# BENCHMARK API
# ============================================================

@admin_bp.route(
    '/api/detectors/benchmark',
    methods=['POST']
)
@login_required
@admin_required
def api_benchmark_detectors():

    from app.services.face_detection import (
        benchmark_detectors
    )

    data = request.get_json(
        silent=True
    ) or {}

    photo_id = data.get(
        'photo_id'
    )

    try:

        min_confidence = float(
            data.get(
                'min_confidence',
                0.9
            )
        )

    except (ValueError, TypeError):

        min_confidence = 0.9

    if not photo_id:

        return jsonify({
            'success': False,
            'error': 'photo_id required'
        }), 400

    photo = Photo.query.get_or_404(
        photo_id
    )

    if not os.path.exists(
        photo.filepath
    ):

        return jsonify({
            'success': False,
            'error':
                'Photo file not found'
        }), 404

    try:

        results = benchmark_detectors(
            photo.filepath,
            min_confidence=min_confidence
        )

        return jsonify({
            'success': True,
            'results': results,
            'photo_id': photo_id,
            'filename': photo.filename
        }), 200

    except Exception as e:

        current_app.logger.exception(
            "Detector benchmark failed"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# RUN EVALUATION
# ============================================================

@admin_bp.route(
    '/evaluation/run',
    methods=['POST']
)
@login_required
@admin_required
def run_evaluation():

    from app.services.detector_evaluator import (
        DetectorEvaluator
    )

    from app.models import TestImage

    test_image_count = (
        TestImage.query
        .filter_by(
            is_annotated=True
        )
        .count()
    )

    if test_image_count == 0:

        return jsonify({
            'success': False,
            'error':
                'No annotated test images found',
            'message':
                'Please upload and annotate test images first'
        }), 400

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    detector_name = data.get(
        'detector',
        'all'
    )

    try:

        iou_threshold = float(
            data.get(
                'iou_threshold',
                0.3
            )
        )

        confidence_threshold = float(
            data.get(
                'confidence_threshold',
                0.3
            )
        )

    except (ValueError, TypeError):

        return jsonify({
            'success': False,
            'error':
                'Invalid threshold value'
        }), 400

    dataset_name = data.get(
        'dataset_name',
        'default'
    )

    # --------------------------------------------------------
    # Validate thresholds
    # --------------------------------------------------------

    if not 0 <= iou_threshold <= 1:

        return jsonify({
            'success': False,
            'error':
                'IoU threshold must be between 0 and 1'
        }), 400

    if not 0 <= confidence_threshold <= 1:

        return jsonify({
            'success': False,
            'error':
                'Confidence threshold must be between 0 and 1'
        }), 400

    try:

        results = (
            DetectorEvaluator.run_evaluation(
                detector_name=detector_name,
                iou_threshold=iou_threshold,
                confidence_threshold=confidence_threshold,
                dataset_name=dataset_name
            )
        )

        if (
            isinstance(results, dict)
            and
            'error' in results
        ):

            return jsonify(
                results
            ), 400

        return jsonify(
            results
        ), 200

    except Exception as e:

        current_app.logger.exception(
            "Detector evaluation failed"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# TEST DATASET
# ============================================================

@admin_bp.route(
    '/test-dataset'
)
@login_required
@admin_required
def test_dataset():

    from app.models import (
        TestImage,
        GroundTruthAnnotation
    )

    test_images = (
        TestImage.query
        .order_by(
            TestImage.uploaded_at.desc()
        )
        .all()
    )

    annotated_count = (
        TestImage.query
        .filter_by(
            is_annotated=True
        )
        .count()
    )

    total_annotations = (
        GroundTruthAnnotation.query
        .count()
    )

    return render_template(
        'admin/test_dataset.html',
        test_images=test_images,
        annotated_count=annotated_count,
        total_annotations=total_annotations
    )


# ============================================================
# UPLOAD TEST IMAGES
# ============================================================

@admin_bp.route(
    '/test-dataset/upload',
    methods=['POST']
)
@login_required
@admin_required
def upload_test_images():

    from app.models import TestImage

    if 'images' not in request.files:

        flash(
            'No images selected',
            'danger'
        )

        return redirect(
            url_for(
                'admin.test_dataset'
            )
        )

    files = request.files.getlist(
        'images'
    )

    uploaded_count = 0

    test_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'test_dataset'
    )

    os.makedirs(
        test_dir,
        exist_ok=True
    )

    for file in files:

        if file and allowed_file(
            file.filename
        ):

            filename = secure_filename(
                file.filename
            )

            timestamp = datetime.now().strftime(
                '%Y%m%d_%H%M%S_%f'
            )

            filename = (
                f"test_"
                f"{timestamp}_"
                f"{filename}"
            )

            filepath = os.path.join(
                test_dir,
                filename
            )

            file.save(
                filepath
            )

            test_img = TestImage(
                filename=filename,
                filepath=filepath
            )

            db.session.add(
                test_img
            )

            uploaded_count += 1

    db.session.commit()

    flash(
        f'{uploaded_count} test images uploaded successfully!',
        'success'
    )

    return redirect(
        url_for(
            'admin.test_dataset'
        )
    )


# ============================================================
# ANNOTATE TEST IMAGE
#
# FIXED:
# The POST request ALWAYS returns JSON.
# This prevents:
#
# Unexpected token '<', "<!doctype..." is not valid JSON
# ============================================================

@admin_bp.route(
    '/test-dataset/<int:image_id>/annotate',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def annotate_test_image(image_id):

    from app.models import (
        TestImage,
        GroundTruthAnnotation
    )

    try:

        test_img = (
            TestImage.query
            .get_or_404(image_id)
        )

        # ====================================================
        # POST = SAVE ANNOTATIONS
        # ====================================================

        if request.method == 'POST':

            current_app.logger.info(
                f"[ANNOTATION_SAVE] "
                f"image_id={image_id}"
            )

            # ------------------------------------------------
            # Read JSON safely
            # ------------------------------------------------

            data = request.get_json(
                silent=True
            )

            if data is None:

                current_app.logger.error(
                    "[ANNOTATION_SAVE] "
                    "Invalid JSON request"
                )

                return jsonify({
                    'success': False,
                    'error':
                        'Request did not contain valid JSON'
                }), 400

            boxes = data.get(
                'boxes',
                []
            )

            if not isinstance(
                boxes,
                list
            ):

                return jsonify({
                    'success': False,
                    'error':
                        'boxes must be a list'
                }), 400

            current_app.logger.info(
                f"[ANNOTATION_SAVE] "
                f"Received {len(boxes)} boxes"
            )

            # ------------------------------------------------
            # Validate ALL boxes first
            # ------------------------------------------------

            validated_boxes = []

            for index, box in enumerate(
                boxes
            ):

                if not isinstance(
                    box,
                    dict
                ):

                    return jsonify({
                        'success': False,
                        'error':
                            f'Invalid annotation '
                            f'at index {index}'
                    }), 400

                required_fields = [
                    'x',
                    'y',
                    'width',
                    'height'
                ]

                for field in required_fields:

                    if field not in box:

                        return jsonify({
                            'success': False,
                            'error':
                                f'Missing "{field}" '
                                f'in annotation '
                                f'{index + 1}'
                        }), 400

                try:

                    x = int(
                        float(
                            box['x']
                        )
                    )

                    y = int(
                        float(
                            box['y']
                        )
                    )

                    width = int(
                        float(
                            box['width']
                        )
                    )

                    height = int(
                        float(
                            box['height']
                        )
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    return jsonify({
                        'success': False,
                        'error':
                            f'Invalid coordinates '
                            f'for annotation '
                            f'{index + 1}'
                    }), 400

                # ------------------------------------------------
                # Validate dimensions
                # ------------------------------------------------

                if width <= 0:

                    return jsonify({
                        'success': False,
                        'error':
                            f'Width must be greater '
                            f'than zero for '
                            f'annotation {index + 1}'
                    }), 400

                if height <= 0:

                    return jsonify({
                        'success': False,
                        'error':
                            f'Height must be greater '
                            f'than zero for '
                            f'annotation {index + 1}'
                    }), 400

                validated_boxes.append({
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'notes': str(
                        box.get(
                            'notes',
                            ''
                        )
                    )
                })

            # ------------------------------------------------
            # Delete old annotations
            # ------------------------------------------------

            GroundTruthAnnotation.query.filter_by(
                test_image_id=image_id
            ).delete(
                synchronize_session=False
            )

            # ------------------------------------------------
            # Create new annotations
            # ------------------------------------------------

            for box in validated_boxes:

                annotation = (
                    GroundTruthAnnotation(
                        test_image_id=image_id,
                        x=box['x'],
                        y=box['y'],
                        width=box['width'],
                        height=box['height'],
                        notes=box['notes']
                    )
                )

                db.session.add(
                    annotation
                )

            # ------------------------------------------------
            # Mark image as annotated
            # ------------------------------------------------

            test_img.is_annotated = (
                len(validated_boxes) > 0
            )

            # ------------------------------------------------
            # Commit
            # ------------------------------------------------

            db.session.commit()

            current_app.logger.info(
                f"[ANNOTATION_SAVE] SUCCESS "
                f"image_id={image_id} "
                f"annotations="
                f"{len(validated_boxes)}"
            )

            # ------------------------------------------------
            # ALWAYS RETURN JSON
            # ------------------------------------------------

            return jsonify({
                'success': True,
                'message':
                    f'Saved '
                    f'{len(validated_boxes)} '
                    f'ground-truth face annotations',
                'count':
                    len(validated_boxes)
            }), 200

        # ====================================================
        # GET = SHOW ANNOTATION PAGE
        # ====================================================

        annotations = []

        for ann in test_img.annotations:

            annotations.append({

                'x': int(
                    ann.x
                ),

                'y': int(
                    ann.y
                ),

                'width': int(
                    ann.width
                ),

                'height': int(
                    ann.height
                ),

                'notes': (
                    ann.notes
                    or
                    ''
                )

            })

        return render_template(
            'admin/annotate_image.html',
            test_img=test_img,
            annotations=annotations
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            f"[ANNOTATION] Error for "
            f"image_id={image_id}: {str(e)}"
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # POST MUST RETURN JSON.
        # Never return an HTML error page to fetch().
        # ----------------------------------------------------

        if request.method == 'POST':

            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        flash(
            f'Error loading annotation page: {str(e)}',
            'danger'
        )

        return redirect(
            url_for(
                'admin.test_dataset'
            )
        )


# ============================================================
# AUTO ANNOTATE TEST IMAGE
# ============================================================

@admin_bp.route(
    '/test-dataset/<int:image_id>/auto-annotate',
    methods=['POST']
)
@login_required
@admin_required
def auto_annotate_test_image(image_id):

    from app.models import TestImage

    try:

        test_img = (
            TestImage.query
            .get_or_404(image_id)
        )

        # ----------------------------------------------------
        # Check file
        # ----------------------------------------------------

        if not os.path.exists(
            test_img.filepath
        ):

            return jsonify({
                'success': False,
                'error':
                    'Test image file not found'
            }), 404

        # ----------------------------------------------------
        # AUTO ANNOTATION SETTINGS
        #
        # RetinaFace is used here.
        #
        # This is ONLY for creating initial
        # annotation boxes.
        # ----------------------------------------------------

        detector = 'retinaface'

        confidence = 0.3

        current_app.logger.info(
            f"[AUTO_ANNOTATE] "
            f"image={test_img.filename} "
            f"detector={detector} "
            f"confidence={confidence}"
        )

        # ----------------------------------------------------
        # Run detector
        # ----------------------------------------------------

        detected_faces = (
            detect_faces_in_image(
                test_img.filepath,
                detector=detector,
                min_confidence=confidence
            )
        )

        boxes = []

        # ----------------------------------------------------
        # Convert detector output
        #
        # Expected:
        # [x, y, width, height]
        # ----------------------------------------------------

        for face_data in (
            detected_faces or []
        ):

            try:

                if len(face_data) == 2:

                    face_img, box = face_data

                else:

                    face_img, box, landmarks = (
                        face_data
                    )

                if box is None:

                    continue

                # ------------------------------------------------
                # Convert NumPy array
                # ------------------------------------------------

                if hasattr(
                    box,
                    'tolist'
                ):

                    box = box.tolist()

                if len(box) < 4:

                    continue

                x = int(
                    float(
                        box[0]
                    )
                )

                y = int(
                    float(
                        box[1]
                    )
                )

                w = int(
                    float(
                        box[2]
                    )
                )

                h = int(
                    float(
                        box[3]
                    )
                )

                # ------------------------------------------------
                # Ignore invalid boxes
                # ------------------------------------------------

                if w <= 0 or h <= 0:

                    continue

                boxes.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

            except Exception as e:

                current_app.logger.warning(
                    f"[AUTO_ANNOTATE] "
                    f"Invalid detection: {str(e)}"
                )

                continue

        # ====================================================
        # REMOVE DUPLICATES
        # ====================================================

        filtered_boxes = []

        for box in boxes:

            duplicate = False

            for existing in filtered_boxes:

                x1 = max(
                    box['x'],
                    existing['x']
                )

                y1 = max(
                    box['y'],
                    existing['y']
                )

                x2 = min(
                    box['x'] + box['width'],
                    existing['x'] + existing['width']
                )

                y2 = min(
                    box['y'] + box['height'],
                    existing['y'] + existing['height']
                )

                intersection_w = max(
                    0,
                    x2 - x1
                )

                intersection_h = max(
                    0,
                    y2 - y1
                )

                intersection = (
                    intersection_w
                    *
                    intersection_h
                )

                area1 = (
                    box['width']
                    *
                    box['height']
                )

                area2 = (
                    existing['width']
                    *
                    existing['height']
                )

                union = (
                    area1
                    +
                    area2
                    -
                    intersection
                )

                if union > 0:

                    overlap = (
                        intersection
                        /
                        union
                    )

                    if overlap >= 0.5:

                        duplicate = True

                        break

            if not duplicate:

                filtered_boxes.append(
                    box
                )

        boxes = filtered_boxes

        # ====================================================
        # SORT
        # ====================================================

        boxes.sort(
            key=lambda b: (
                b['y'],
                b['x']
            )
        )

        current_app.logger.info(
            f"[AUTO_ANNOTATE] "
            f"detected={len(boxes)}"
        )

        # ----------------------------------------------------
        # Return JSON
        # ----------------------------------------------------

        return jsonify({

            'success': True,

            'boxes': boxes,

            'count': len(boxes),

            'detector': detector,

            'confidence': confidence

        }), 200

    except Exception as e:

        current_app.logger.exception(
            "[AUTO_ANNOTATE] Detection failed"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# DELETE TEST IMAGE
# ============================================================

@admin_bp.route(
    '/test-dataset/<int:image_id>/delete',
    methods=['POST']
)
@login_required
@admin_required
def delete_test_image(image_id):

    from app.models import TestImage

    try:

        test_img = (
            TestImage.query
            .get_or_404(image_id)
        )

        # ----------------------------------------------------
        # Delete physical file
        # ----------------------------------------------------

        if os.path.exists(
            test_img.filepath
        ):

            os.remove(
                test_img.filepath
            )

        # ----------------------------------------------------
        # Delete database record
        # ----------------------------------------------------

        db.session.delete(
            test_img
        )

        db.session.commit()

        flash(
            'Test image deleted successfully',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error deleting test image: {str(e)}',
            'danger'
        )

    return redirect(
        url_for(
            'admin.test_dataset'
        )
    )


# ============================================================
# EVALUATION HISTORY
# ============================================================

@admin_bp.route(
    '/evaluation/history'
)
@login_required
@admin_required
def evaluation_history():

    from app.models import (
        EvaluationRun,
        DetectorEvaluation
    )

    runs = (
        EvaluationRun.query
        .order_by(
            EvaluationRun.timestamp.desc()
        )
        .all()
    )

    run_details = []

    for run in runs:

        evaluations = (
            DetectorEvaluation.query
            .filter(
                DetectorEvaluation.timestamp
                >=
                run.timestamp,

                DetectorEvaluation.timestamp
                <=
                run.timestamp
                +
                timedelta(
                    minutes=5
                )
            )
            .all()
        )

        run_details.append({

            'run': run,

            'evaluations': evaluations

        })

    return render_template(
        'admin/evaluation_history.html',
        run_details=run_details
    )