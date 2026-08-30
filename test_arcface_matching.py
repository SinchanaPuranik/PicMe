#!/usr/bin/env python
"""Test ArcFace matching logic"""
from app import create_app, db
from app.models import FaceEmbedding, Photo
from app.services.arcface_service import ArcFaceService
from app.services.matching import find_matching_photos
import numpy as np

app = create_app('development')

with app.app_context():
    # Get a sample ArcFace embedding
    arcface_embeddings = db.session.query(FaceEmbedding).filter_by(model_type='arcface').all()
    
    if len(arcface_embeddings) > 0:
        print("--- ArcFace Matching Test ---")
        
        # Get embeddings for event 1
        embeddings_event1 = db.session.query(FaceEmbedding, Photo).join(
            Photo, FaceEmbedding.photo_id == Photo.id
        ).filter(
            Photo.event_id == 1,
            FaceEmbedding.model_type == 'arcface'
        ).all()
        
        print(f"Total ArcFace embeddings for Event 1: {len(embeddings_event1)}")
        
        if len(embeddings_event1) > 1:
            # Use the first embedding as query
            query_embedding = embeddings_event1[0][0].get_embedding()
            print(f"\nQuery embedding shape: {query_embedding.shape}")
            print(f"Query embedding norm: {np.linalg.norm(query_embedding)}")
            
            # Test matching with different thresholds
            print("\n--- Similarity Scores (Sample Comparisons) ---")
            for i in range(min(3, len(embeddings_event1))):
                stored_emb = embeddings_event1[i][0].get_embedding()
                
                # Cosine similarity
                dot_product = np.dot(query_embedding, stored_emb)
                norm1 = np.linalg.norm(query_embedding)
                norm2 = np.linalg.norm(stored_emb)
                similarity = dot_product / (norm1 * norm2)
                
                print(f"  Embedding {i}: similarity = {similarity:.4f} (dot={dot_product:.4f})")
            
            # Test with threshold 0.4
            print("\n--- Testing Thresholds ---")
            for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
                matches = find_matching_photos(query_embedding, 1, 'arcface', threshold=threshold)
                print(f"  Threshold {threshold}: {len(matches)} matches")
                if matches:
                    print(f"    Top match: similarity={matches[0][1]:.4f}")
    else:
        print("No ArcFace embeddings found!")
