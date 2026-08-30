"""
Model Evaluation Script
Compares FaceNet and ArcFace performance on a ground-truth test set
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import PerformanceMetric
from app.services.face_detection import detect_faces_in_image
from app.services.facenet_service import FaceNetService
from app.services.arcface_service import ArcFaceService
from app.services.matching import compute_cosine_similarity, compute_euclidean_distance
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import time


class ModelEvaluator:
    """Evaluates face recognition models"""
    
    def __init__(self):
        self.facenet = FaceNetService()
        self.arcface = ArcFaceService()
        self.results = {
            'facenet': {},
            'arcface': {}
        }
    
    def create_ground_truth_set(self, test_dir):
        """
        Create ground truth dataset
        Expected structure:
        test_dir/
            person1/
                photo1.jpg
                photo2.jpg
            person2/
                photo1.jpg
                photo2.jpg
        """
        ground_truth = {}
        
        for person_id in os.listdir(test_dir):
            person_dir = os.path.join(test_dir, person_id)
            if not os.path.isdir(person_dir):
                continue
            
            ground_truth[person_id] = []
            for photo in os.listdir(person_dir):
                photo_path = os.path.join(person_dir, photo)
                if photo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    ground_truth[person_id].append(photo_path)
        
        return ground_truth
    
    def evaluate_model(self, model_type='facenet', threshold=0.6):
        """
        Evaluate a model's performance
        
        Args:
            model_type: 'facenet' or 'arcface'
            threshold: Matching threshold
        """
        print(f"\n{'='*50}")
        print(f"Evaluating {model_type.upper()}")
        print(f"{'='*50}")
        
        # You can customize this path to your test dataset
        test_dir = 'tests/test_dataset'
        
        if not os.path.exists(test_dir):
            print(f"Test directory not found: {test_dir}")
            print("Please create a test dataset following the structure in the docstring")
            return None
        
        ground_truth = self.create_ground_truth_set(test_dir)
        
        if not ground_truth:
            print("No ground truth data found")
            return None
        
        # Generate embeddings for all photos
        embeddings = {}
        processing_times = []
        
        for person_id, photos in ground_truth.items():
            embeddings[person_id] = []
            
            for photo_path in photos:
                start_time = time.time()
                
                # Detect face
                faces = detect_faces_in_image(photo_path)
                if not faces:
                    continue
                
                # Handle both old format (face_img, box) and new format (face_img, box, landmarks)
                face_data = faces[0]
                if len(face_data) == 2:
                    face_img, _ = face_data
                else:
                    face_img, _, _ = face_data
                
                # Generate embedding
                if model_type == 'facenet':
                    embedding = self.facenet.generate_embedding(face_img)
                else:
                    embedding = self.arcface.generate_embedding(face_img)
                
                if embedding is not None:
                    embeddings[person_id].append(embedding)
                
                processing_times.append(time.time() - start_time)
        
        # Compute metrics
        y_true = []
        y_pred = []
        
        # For each person, compare their first photo against all others
        for person_id, person_embeddings in embeddings.items():
            if len(person_embeddings) < 2:
                continue
            
            query_embedding = person_embeddings[0]
            
            # Compare with same person (positives)
            for emb in person_embeddings[1:]:
                if model_type == 'facenet':
                    distance = compute_euclidean_distance(query_embedding, emb)
                    match = distance < threshold
                else:
                    similarity = compute_cosine_similarity(query_embedding, emb)
                    match = similarity > threshold
                
                y_true.append(1)
                y_pred.append(1 if match else 0)
            
            # Compare with other people (negatives)
            for other_id, other_embeddings in embeddings.items():
                if other_id == person_id:
                    continue
                
                for emb in other_embeddings:
                    if model_type == 'facenet':
                        distance = compute_euclidean_distance(query_embedding, emb)
                        match = distance < threshold
                    else:
                        similarity = compute_cosine_similarity(query_embedding, emb)
                        match = similarity > threshold
                    
                    y_true.append(0)
                    y_pred.append(1 if match else 0)
        
        if not y_true:
            print("Insufficient data for evaluation")
            return None
        
        # Calculate metrics
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Count false positives and false negatives
        fp = sum((p == 1 and t == 0) for p, t in zip(y_pred, y_true))
        fn = sum((p == 0 and t == 1) for p, t in zip(y_pred, y_true))
        
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        
        results = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'false_positives': fp,
            'false_negatives': fn,
            'avg_processing_time': avg_processing_time,
            'test_set_size': len(y_true)
        }
        
        self.results[model_type] = results
        
        # Print results
        print(f"\nResults for {model_type.upper()}:")
        print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
        print(f"  Recall: {recall:.4f} ({recall*100:.2f}%)")
        print(f"  F1-Score: {f1:.4f} ({f1*100:.2f}%)")
        print(f"  False Positives: {fp}")
        print(f"  False Negatives: {fn}")
        print(f"  Avg Processing Time: {avg_processing_time:.4f}s")
        print(f"  Test Set Size: {len(y_true)}")
        
        return results
    
    def save_results_to_db(self):
        """Save evaluation results to database"""
        app = create_app()
        with app.app_context():
            for model_type, results in self.results.items():
                if not results:
                    continue
                
                # Save each metric
                for metric_name, value in results.items():
                    if metric_name == 'test_set_size':
                        continue
                    
                    metric = PerformanceMetric(
                        model_type=model_type,
                        metric_type=metric_name,
                        value=float(value),
                        test_set_size=results.get('test_set_size'),
                        notes=f'Evaluation run at {time.strftime("%Y-%m-%d %H:%M:%S")}'
                    )
                    db.session.add(metric)
            
            db.session.commit()
            print("\n✓ Results saved to database")
    
    def compare_models(self):
        """Compare FaceNet and ArcFace performance"""
        print(f"\n{'='*50}")
        print("MODEL COMPARISON")
        print(f"{'='*50}")
        
        if not self.results['facenet'] or not self.results['arcface']:
            print("Run both model evaluations first")
            return
        
        fn_results = self.results['facenet']
        af_results = self.results['arcface']
        
        print(f"\n{'Metric':<25} {'FaceNet':<15} {'ArcFace':<15} {'Winner':<10}")
        print("-" * 65)
        
        metrics = ['precision', 'recall', 'f1_score']
        for metric in metrics:
            fn_val = fn_results[metric]
            af_val = af_results[metric]
            winner = 'FaceNet' if fn_val > af_val else 'ArcFace' if af_val > fn_val else 'Tie'
            print(f"{metric.replace('_', ' ').title():<25} {fn_val:.4f}         {af_val:.4f}         {winner}")
        
        print(f"\n{'Processing Speed':<25} {fn_results['avg_processing_time']:.4f}s       {af_results['avg_processing_time']:.4f}s       {'FaceNet' if fn_results['avg_processing_time'] < af_results['avg_processing_time'] else 'ArcFace'}")


def main():
    """Main evaluation function"""
    evaluator = ModelEvaluator()
    
    print("PICME Model Evaluation")
    print("=" * 50)
    
    # Evaluate FaceNet
    evaluator.evaluate_model('facenet', threshold=0.6)
    
    # Evaluate ArcFace
    evaluator.evaluate_model('arcface', threshold=0.4)
    
    # Compare results
    evaluator.compare_models()
    
    # Save to database
    save = input("\nSave results to database? (y/n): ")
    if save.lower() == 'y':
        evaluator.save_results_to_db()


if __name__ == '__main__':
    main()
