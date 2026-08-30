"""
Performance evaluation tests for FaceNet vs ArcFace
"""
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import time
from app.services.facenet_service import FaceNetService
from app.services.arcface_service import ArcFaceService
from app.services.matching import compute_cosine_similarity, compute_euclidean_distance


class FaceRecognitionEvaluator:
    """Evaluate face recognition models"""
    
    def __init__(self):
        self.facenet = FaceNetService()
        self.arcface = ArcFaceService()
        self.results = {}
    
    def generate_test_embeddings(self, test_images, model='facenet'):
        """Generate embeddings for test images"""
        embeddings = []
        service = self.facenet if model == 'facenet' else self.arcface
        
        for img in test_images:
            embedding = service.generate_embedding(img)
            if embedding is not None:
                embeddings.append(embedding)
        
        return embeddings
    
    def evaluate_matching_accuracy(self, query_embeddings, gallery_embeddings, 
                                   ground_truth, model='facenet', threshold=0.6):
        """
        Evaluate matching accuracy
        
        Args:
            query_embeddings: List of query face embeddings
            gallery_embeddings: List of gallery face embeddings
            ground_truth: True labels for matches
            model: 'facenet' or 'arcface'
            threshold: Matching threshold
        
        Returns:
            Dictionary with metrics
        """
        predictions = []
        processing_times = []
        
        for query in query_embeddings:
            start_time = time.time()
            
            # Find best match
            best_similarity = -1
            best_match = -1
            
            for idx, gallery_emb in enumerate(gallery_embeddings):
                if model == 'facenet':
                    distance = compute_euclidean_distance(query, gallery_emb)
                    similarity = 1.0 / (1.0 + distance)
                else:
                    similarity = compute_cosine_similarity(query, gallery_emb)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = idx
            
            processing_times.append(time.time() - start_time)
            
            # Apply threshold
            if best_similarity > threshold:
                predictions.append(best_match)
            else:
                predictions.append(-1)  # No match
        
        # Calculate metrics
        precision = precision_score(ground_truth, predictions, average='weighted', zero_division=0)
        recall = recall_score(ground_truth, predictions, average='weighted', zero_division=0)
        f1 = f1_score(ground_truth, predictions, average='weighted', zero_division=0)
        
        # Calculate false positives/negatives
        false_positives = sum(1 for p, gt in zip(predictions, ground_truth) if p != gt and p != -1)
        false_negatives = sum(1 for p, gt in zip(predictions, ground_truth) if p == -1 and gt != -1)
        
        avg_processing_time = np.mean(processing_times) * 1000  # Convert to ms
        
        return {
            'model': model,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'avg_processing_time_ms': avg_processing_time,
            'total_queries': len(query_embeddings),
            'threshold': threshold
        }
    
    def compare_models(self, test_data):
        """
        Compare FaceNet and ArcFace performance
        
        Args:
            test_data: Dictionary with query_images, gallery_images, ground_truth
        
        Returns:
            Comparison results
        """
        print("Evaluating FaceNet...")
        facenet_query = self.generate_test_embeddings(test_data['query_images'], 'facenet')
        facenet_gallery = self.generate_test_embeddings(test_data['gallery_images'], 'facenet')
        facenet_results = self.evaluate_matching_accuracy(
            facenet_query, facenet_gallery, test_data['ground_truth'], 
            'facenet', threshold=0.6
        )
        
        print("Evaluating ArcFace...")
        arcface_query = self.generate_test_embeddings(test_data['query_images'], 'arcface')
        arcface_gallery = self.generate_test_embeddings(test_data['gallery_images'], 'arcface')
        arcface_results = self.evaluate_matching_accuracy(
            arcface_query, arcface_gallery, test_data['ground_truth'],
            'arcface', threshold=0.4
        )
        
        return {
            'facenet': facenet_results,
            'arcface': arcface_results,
            'winner': self._determine_winner(facenet_results, arcface_results)
        }
    
    def _determine_winner(self, facenet, arcface):
        """Determine which model performs better"""
        facenet_score = (facenet['precision'] + facenet['recall'] + facenet['f1_score']) / 3
        arcface_score = (arcface['precision'] + arcface['recall'] + arcface['f1_score']) / 3
        
        if facenet_score > arcface_score:
            return 'facenet'
        elif arcface_score > facenet_score:
            return 'arcface'
        else:
            return 'tie'
    
    def print_comparison(self, results):
        """Print comparison results"""
        print("\n" + "="*60)
        print("FACE RECOGNITION MODEL COMPARISON")
        print("="*60)
        
        for model_name in ['facenet', 'arcface']:
            model_results = results[model_name]
            print(f"\n{model_name.upper()} Results:")
            print(f"  Precision:          {model_results['precision']:.4f}")
            print(f"  Recall:             {model_results['recall']:.4f}")
            print(f"  F1 Score:           {model_results['f1_score']:.4f}")
            print(f"  False Positives:    {model_results['false_positives']}")
            print(f"  False Negatives:    {model_results['false_negatives']}")
            print(f"  Avg Processing:     {model_results['avg_processing_time_ms']:.2f} ms")
            print(f"  Threshold:          {model_results['threshold']}")
        
        print(f"\n{'='*60}")
        print(f"WINNER: {results['winner'].upper()}")
        print(f"{'='*60}\n")


def run_evaluation():
    """Run model evaluation"""
    # This would use actual test data in production
    print("Face Recognition Model Evaluation")
    print("Note: This is a template. Add your test dataset to run actual evaluation.")
    
    evaluator = FaceRecognitionEvaluator()
    
    # Example test data structure (replace with actual data)
    # test_data = {
    #     'query_images': [...],  # List of face images to query
    #     'gallery_images': [...],  # List of face images in gallery
    #     'ground_truth': [...]  # True match labels
    # }
    
    # results = evaluator.compare_models(test_data)
    # evaluator.print_comparison(results)
    
    print("\nTo run evaluation:")
    print("1. Prepare test dataset with labeled faces")
    print("2. Load images using cv2 or PIL")
    print("3. Call evaluator.compare_models(test_data)")
    print("4. Results will show which model performs better")


if __name__ == '__main__':
    run_evaluation()
