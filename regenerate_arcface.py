#!/usr/bin/env python
"""Regenerate ArcFace embeddings with the new InsightFace model"""
from app import create_app, db
from app.models import Photo, FaceEmbedding
from app.services.face_detection import detect_faces_in_image
from app.services.arcface_service import ArcFaceService

app = create_app('development')

with app.app_context():
    # Delete old ArcFace embeddings
    old_embeddings = FaceEmbedding.query.filter_by(model_type='arcface').delete()
    db.session.commit()
    print(f"✓ Deleted {old_embeddings} old ArcFace embeddings")
    
    # Get all processed photos
    photos = Photo.query.filter_by(processed=True).all()
    print(f"\n--- Regenerating ArcFace embeddings for {len(photos)} photos ---")
    
    # Initialize ArcFace service
    arcface_service = ArcFaceService()
    
    if arcface_service.app is None:
        print("✗ ArcFace model failed to initialize!")
        exit(1)
    
    success_count = 0
    fail_count = 0
    total_faces = 0
    
    for i, photo in enumerate(photos, 1):
        try:
            print(f"\n[{i}/{len(photos)}] Processing {photo.filename}...")
            
            # Detect faces
            faces = detect_faces_in_image(photo.filepath)
            print(f"  Detected {len(faces)} faces")
            
            for j, (face_img, box) in enumerate(faces):
                try:
                    # Generate ArcFace embedding with new model
                    embedding = arcface_service.generate_embedding(face_img)
                    
                    if embedding is not None:
                        fe = FaceEmbedding(photo_id=photo.id, model_type='arcface')
                        fe.set_embedding(embedding)
                        fe.set_face_box(box)
                        db.session.add(fe)
                        total_faces += 1
                        print(f"    Face {j+1}: ✓ embedding generated")
                    else:
                        print(f"    Face {j+1}: ✗ embedding is None")
                        fail_count += 1
                        
                except Exception as e:
                    print(f"    Face {j+1}: ✗ Error - {str(e)}")
                    fail_count += 1
            
            success_count += 1
            db.session.commit()
            
        except Exception as e:
            print(f"  ✗ Error processing photo: {str(e)}")
            fail_count += 1
            continue
    
    print(f"\n--- Summary ---")
    print(f"✓ Photos processed successfully: {success_count}")
    print(f"✗ Photos failed: {fail_count}")
    print(f"✓ Total ArcFace embeddings generated: {total_faces}")
    
    # Verify embeddings
    arcface_count = FaceEmbedding.query.filter_by(model_type='arcface').count()
    print(f"✓ ArcFace embeddings in database: {arcface_count}")
