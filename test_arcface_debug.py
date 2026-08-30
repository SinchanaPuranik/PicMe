#!/usr/bin/env python
"""Debug script to test ArcFace functionality"""
from app import create_app, db
from app.models import FaceEmbedding
from app.services.arcface_service import ArcFaceService
import cv2
import numpy as np

app = create_app('development')

with app.app_context():
    # Check embeddings in database
    arcface_embeddings = db.session.query(FaceEmbedding).filter_by(model_type='arcface').all()
    print(f"✓ Total ArcFace embeddings in DB: {len(arcface_embeddings)}")
    
    facenet_embeddings = db.session.query(FaceEmbedding).filter_by(model_type='facenet').all()
    print(f"✓ Total FaceNet embeddings in DB: {len(facenet_embeddings)}")
    
    # Test ArcFace model initialization
    print("\n--- Testing ArcFace Model ---")
    try:
        service = ArcFaceService()
        print("✓ ArcFace model initialized successfully")
        
        # Test with dummy image
        dummy_img = np.random.randint(0, 256, (112, 112, 3), dtype='uint8')
        embedding = service.generate_embedding(dummy_img)
        
        if embedding is not None:
            print(f"✓ ArcFace embedding generated: shape {embedding.shape}")
        else:
            print("✗ ArcFace embedding is None")
            
    except Exception as e:
        print(f"✗ Error with ArcFace: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Check if embeddings have data
    if len(arcface_embeddings) > 0:
        print("\n--- First ArcFace Embedding ---")
        emb = arcface_embeddings[0]
        data = emb.get_embedding()
        print(f"✓ Embedding shape: {data.shape if data is not None else 'None'}")
        print(f"  Photo ID: {emb.photo_id}")
        print(f"  Embedding norm: {np.linalg.norm(data) if data is not None else 'N/A'}")
