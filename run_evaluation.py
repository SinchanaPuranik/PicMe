#!/usr/bin/env python
"""
Generate performance metrics using existing photos from Event 1
This script evaluates FaceNet and ArcFace on real photos in the database
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Photo, FaceEmbedding, Event, PerformanceMetric
from app.services.face_detection import detect_faces_in_image
from app.services.facenet_service import FaceNetService
from app.services.arcface_service import ArcFaceService
from app.services.matching import compute_cosine_similarity, compute_euclidean_distance
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import time

app = create_app('development')

def evaluate_models_on_database():
    """Evaluate models using embeddings already in the database"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("PICME MODEL EVALUATION - Database-Based")
        print("="*60)
        
        # Get all photos from Event 1
        photos = Photo.query.filter_by(event_id=1, processed=True).all()
        
        if not photos:
            print("\n✗ No processed photos found in Event 1")
            print("Please process photos first using the admin dashboard")
            return
        
        print(f"\n✓ Found {len(photos)} processed photos")
        
        # Get all embeddings
        all_embeddings = FaceEmbedding.query.filter(
            FaceEmbedding.photo_id.in_([p.id for p in photos])
        ).all()
        
        facenet_embeddings = [e for e in all_embeddings if e.model_type == 'facenet']
        arcface_embeddings = [e for e in all_embeddings if e.model_type == 'arcface']
        
        print(f"  - FaceNet embeddings: {len(facenet_embeddings)}")
        print(f"  - ArcFace embeddings: {len(arcface_embeddings)}")
        
        if len(facenet_embeddings) < 2 or len(arcface_embeddings) < 2:
            print("\n✗ Insufficient embeddings for evaluation")
            return
        
        # Evaluate each model
        results = {}
        
        for model_type, embeddings in [('facenet', facenet_embeddings), ('arcface', arcface_embeddings)]:
            print(f"\n--- Evaluating {model_type.upper()} ---")
            
            # Create pairs for evaluation
            y_true = []
            y_pred = []
            processing_times = []
            
            # Compare each embedding with others
            for i, emb1 in enumerate(embeddings):
                query_vec = emb1.get_embedding()
                
                for j, emb2 in enumerate(embeddings):
                    stored_vec = emb2.get_embedding()
                    
                    # Same photo = positive match
                    same_photo = (emb1.photo_id == emb2.photo_id)
                    y_true.append(1 if same_photo else 0)
                    
                    # Compute similarity
                    start_time = time.time()
                    
                    if model_type == 'facenet':
                        distance = compute_euclidean_distance(query_vec, stored_vec)
                        similarity = 1.0 / (1.0 + distance)
                        threshold = 0.6
                    else:  # arcface
                        similarity = compute_cosine_similarity(query_vec, stored_vec)
                        threshold = 0.4
                    
                    processing_times.append(time.time() - start_time)
                    
                    # Prediction: 1 if above threshold, 0 otherwise
                    prediction = 1 if similarity > threshold else 0
                    y_pred.append(prediction)
            
            # Calculate metrics
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            
            # Confusion matrix
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel() if len(set(y_true)) > 1 else (0, 0, 0, sum(y_true))
            
            avg_processing_time = np.mean(processing_times) * 1000 if processing_times else 0
            
            results[model_type] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'false_positives': fp,
                'false_negatives': fn,
                'avg_processing_time_ms': avg_processing_time,
                'test_set_size': len(y_true)
            }
            
            print(f"\n  Precision:   {precision:.4f} ({precision*100:.2f}%)")
            print(f"  Recall:      {recall:.4f} ({recall*100:.2f}%)")
            print(f"  F1-Score:    {f1:.4f} ({f1*100:.2f}%)")
            print(f"  True Positives:  {tp}")
            print(f"  False Positives: {fp}")
            print(f"  True Negatives:  {tn}")
            print(f"  False Negatives: {fn}")
            print(f"  Avg Processing: {avg_processing_time:.2f}ms")
            print(f"  Test Set Size: {len(y_true)}")
        
        # Compare models
        print("\n" + "="*60)
        print("MODEL COMPARISON")
        print("="*60)
        
        fn_res = results['facenet']
        af_res = results['arcface']
        
        print(f"\n{'Metric':<25} {'FaceNet':<15} {'ArcFace':<15} {'Winner':<10}")
        print("-" * 65)
        
        for metric in ['precision', 'recall', 'f1_score']:
            fn_val = fn_res[metric]
            af_val = af_res[metric]
            winner = 'FaceNet' if fn_val > af_val else 'ArcFace' if af_val > fn_val else 'Tie'
            print(f"{metric.replace('_', ' ').title():<25} {fn_val:.4f}         {af_val:.4f}         {winner}")
        
        print(f"\n{'Processing Speed (ms)':<25} {fn_res['avg_processing_time_ms']:.2f}          {af_res['avg_processing_time_ms']:.2f}          ", end="")
        if fn_res['avg_processing_time_ms'] < af_res['avg_processing_time_ms']:
            print("FaceNet")
        else:
            print("ArcFace")
        
        # Save to database
        print("\n" + "="*60)
        save_choice = input("Save results to database? (y/n): ").strip().lower()
        
        if save_choice == 'y':
            # Clear old metrics
            PerformanceMetric.query.delete()
            
            for model_type, result in results.items():
                for metric_name, value in result.items():
                    if metric_name == 'test_set_size':
                        continue
                    
                    metric = PerformanceMetric(
                        model_type=model_type,
                        metric_type=metric_name,
                        value=float(value),
                        test_set_size=result.get('test_set_size'),
                        notes=f'Evaluation based on {result.get("test_set_size")} test pairs'
                    )
                    db.session.add(metric)
            
            db.session.commit()
            print("\n✓ Results saved to database!")
            print(f"✓ Visit http://localhost:5000/admin/metrics to view results")
        else:
            print("\n  Results not saved")


if __name__ == '__main__':
    evaluate_models_on_database()
