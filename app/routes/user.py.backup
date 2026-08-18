from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Event, Photo, FaceEmbedding
from app.routes import user_bp
from app.services.face_detection import detect_faces_in_image
from app.services.arcface_service import ArcFaceService
from app.services.matching import find_matching_photos
from app.services.search_evaluation import SearchEvaluator
import os
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import time


@user_bp.route('/events')
def select_event():
    events = Event.query.filter_by(is_active=True).order_by(Event.event_date.desc()).all()
    return render_template('user/select_event.html', events=events)


@user_bp.route('/events/<int:event_id>/capture')
def capture_selfie(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('user/capture_selfie.html', event=event)


@user_bp.route('/events/<int:event_id>/search', methods=['POST'])
def search_photos(event_id):
    event = Event.query.get_or_404(event_id)
    
    try:
        # Track overall timing
        total_start = time.time()
        
        # Get image data from request
        data = request.get_json()
        image_data = data.get('image')
        detector_type = data.get('detector', 'mtcnn')  # 'mtcnn' or 'retinaface'
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Convert PIL to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Save temporary image
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_selfie.jpg')
        cv2.imwrite(temp_path, image_cv)
        
        # Face Detection - Time this (with selected detector)
        fd_start = time.time()
        faces = detect_faces_in_image(temp_path, detector=detector_type)
        face_detection_time = (time.time() - fd_start) * 1000  # Convert to ms
        
        if not faces:
            os.remove(temp_path)
            return jsonify({'error': 'No face detected in image'}), 400
        
        # Use the first detected face
        face_img, _ = faces[0]
        
        # Embedding Generation - Time this (ArcFace only)
        emb_start = time.time()
        service = ArcFaceService()
        query_embedding = service.generate_embedding(face_img)
        embedding_generation_time = (time.time() - emb_start) * 1000  # Convert to ms
        
        if query_embedding is None:
            os.remove(temp_path)
            return jsonify({'error': 'Failed to generate face embedding'}), 500
        
        # Matching - Time this (ArcFace only)
        match_start = time.time()
        matching_photos = find_matching_photos(
            query_embedding, 
            event_id, 
            'arcface',  # Always use ArcFace
            threshold=current_app.config.get('FACE_MATCH_THRESHOLD_ARCFACE', 0.4)
        )
        matching_time = (time.time() - match_start) * 1000  # Convert to ms
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Calculate total time
        total_time = (time.time() - total_start) * 1000  # Convert to ms
        
        # ✨ EVALUATE MODEL PERFORMANCE ✨
        search_record = SearchEvaluator.evaluate_retrieval(
            event_id=event_id,
            model_type='arcface',
            matching_photos=matching_photos,
            face_detection_time=face_detection_time,
            embedding_generation_time=embedding_generation_time,
            matching_time=matching_time,
            total_time=total_time
        )
        
        # Separate individual and group photos
        individual_photos = []
        group_photos = []
        
        for photo, similarity in matching_photos:
            photo_data = {
                'id': photo.id,
                'filename': photo.filename,
                'url': url_for('static', filename=f'uploads/events/{event_id}/{photo.filename}'),
                'similarity': float(similarity),
                'num_faces': photo.num_faces,
                'uploaded_at': photo.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Classify as individual (1 face) or group (2+ faces)
            if photo.num_faces == 1:
                individual_photos.append(photo_data)
            else:
                group_photos.append(photo_data)
        
        return jsonify({
            'success': True,
            'model': 'arcface',
            'detector': detector_type,
            'matches': len(matching_photos),
            'individual_photos': individual_photos,
            'group_photos': group_photos,
            'total_individual': len(individual_photos),
            'total_group': len(group_photos),
            # Performance metrics for this search
            'performance': {
                'detector': detector_type,
                'face_detection_ms': round(face_detection_time, 2),
                'embedding_generation_ms': round(embedding_generation_time, 2),
                'matching_ms': round(matching_time, 2),
                'total_ms': round(total_time, 2),
                'avg_similarity': round(search_record.avg_similarity, 4) if search_record.avg_similarity else 0,
                'max_similarity': round(search_record.max_similarity, 4) if search_record.max_similarity else 0,
                'min_similarity': round(search_record.min_similarity, 4) if search_record.min_similarity else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/events/<int:event_id>/results')
def view_results(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('user/results.html', event=event)


@user_bp.route('/events/<int:event_id>/gallery')
def photo_gallery(event_id):
    event = Event.query.get_or_404(event_id)
    photos = Photo.query.filter_by(event_id=event_id, processed=True).all()
    return render_template('user/gallery.html', event=event, photos=photos)


@user_bp.route('/events/<int:event_id>/search-stats')
def search_statistics(event_id):
    """Get real-time search evaluation statistics for an event"""
    event = Event.query.get_or_404(event_id)
    
    # Get statistics for ArcFace
    from app.models import SearchRetrieval
    searches = SearchRetrieval.query.filter_by(event_id=event_id, model_type='arcface').all()
    
    if searches:
        avg_matches = sum(s.num_matches for s in searches) / len(searches)
        avg_time = sum(s.processing_time_ms for s in searches) / len(searches)
        avg_similarity = sum(s.avg_similarity for s in searches if s.avg_similarity) / len([s for s in searches if s.avg_similarity])
    else:
        avg_matches = 0
        avg_time = 0
        avg_similarity = 0
    
    return jsonify({
        'success': True,
        'event_id': event_id,
        'event_name': event.name,
        'arcface': {
            'total_searches': len(searches),
            'avg_matches': round(avg_matches, 2),
            'avg_processing_time_ms': round(avg_time, 2),
            'avg_similarity': round(avg_similarity, 4)
        }
    })


@user_bp.route('/events/<int:event_id>/search-history')
def search_history(event_id):
    """Get search history and evaluation data for an event"""
    from app.models import SearchRetrieval
    
    event = Event.query.get_or_404(event_id)
    searches = SearchRetrieval.query.filter_by(event_id=event_id).order_by(SearchRetrieval.timestamp.desc()).all()
    
    searches_data = []
    for search in searches:
        searches_data.append({
            'id': search.id,
            'model': search.model_type,
            'matches': search.num_matches,
            'individual': search.num_individual,
            'group': search.num_group,
            'avg_similarity': search.avg_similarity,
            'max_similarity': search.max_similarity,
            'min_similarity': search.min_similarity,
            'processing_time_ms': search.processing_time_ms,
            'timestamp': search.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'notes': search.notes
        })
    
    return jsonify({
        'success': True,
        'event_id': event_id,
        'event_name': event.name,
        'total_searches': len(searches),
        'searches': searches_data
    })
