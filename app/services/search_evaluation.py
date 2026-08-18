"""
Real-time evaluation of model performance during photo retrieval
"""
import numpy as np
import time
from app.models import SearchRetrieval
from app import db


class SearchEvaluator:
    """Evaluates model performance on retrieved photos"""
    
    @staticmethod
    def evaluate_retrieval(event_id, model_type, matching_photos, 
                          face_detection_time, embedding_generation_time, 
                          matching_time, total_time):
        """
        Evaluate the performance of a photo retrieval search
        
        Args:
            event_id: Event ID where search occurred
            model_type: 'facenet' or 'arcface'
            matching_photos: List of (Photo, similarity_score) tuples
            face_detection_time: Time for face detection (ms)
            embedding_generation_time: Time to generate embedding (ms)
            matching_time: Time for matching (ms)
            total_time: Total processing time (ms)
            
        Returns:
            SearchRetrieval object with evaluation results
        """
        
        # Extract similarity scores
        similarity_scores = [score for _, score in matching_photos]
        
        # Count photos by type
        num_individual = sum(1 for photo, _ in matching_photos if photo.num_faces == 1)
        num_group = sum(1 for photo, _ in matching_photos if photo.num_faces > 1)
        
        # Calculate statistics
        stats = SearchEvaluator._calculate_statistics(similarity_scores)
        
        # Create search retrieval record
        search_record = SearchRetrieval(
            event_id=event_id,
            model_type=model_type,
            num_matches=len(matching_photos),
            num_individual=num_individual,
            num_group=num_group,
            avg_similarity=stats['mean'],
            max_similarity=stats['max'],
            min_similarity=stats['min'],
            median_similarity=stats['median'],
            std_similarity=stats['std'],
            processing_time_ms=total_time,
            face_detection_time_ms=face_detection_time,
            embedding_generation_time_ms=embedding_generation_time,
            matching_time_ms=matching_time
        )
        
        # Store similarity scores
        search_record.set_similarity_scores(similarity_scores)
        
        # Add notes about performance
        search_record.notes = SearchEvaluator._generate_performance_notes(
            model_type, len(matching_photos), stats, total_time
        )
        
        # Save to database
        db.session.add(search_record)
        db.session.commit()
        
        return search_record
    
    @staticmethod
    def _calculate_statistics(scores):
        """Calculate statistics on similarity scores"""
        if not scores:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0
            }
        
        scores_arr = np.array(scores)
        
        return {
            'mean': float(np.mean(scores_arr)),
            'median': float(np.median(scores_arr)),
            'std': float(np.std(scores_arr)),
            'min': float(np.min(scores_arr)),
            'max': float(np.max(scores_arr))
        }
    
    @staticmethod
    def _generate_performance_notes(model_type, num_matches, stats, total_time):
        """Generate human-readable performance notes"""
        notes = f"Retrieved {num_matches} photos using {model_type.upper()}\n"
        
        if num_matches > 0:
            notes += f"Similarity Range: {stats['min']:.4f} - {stats['max']:.4f}\n"
            notes += f"Average Similarity: {stats['mean']:.4f}\n"
            notes += f"Median Similarity: {stats['median']:.4f}\n"
            notes += f"Std Dev: {stats['std']:.4f}\n"
        
        notes += f"Total Processing Time: {total_time:.2f}ms"
        
        return notes
    
    @staticmethod
    def get_search_statistics(event_id, model_type=None):
        """Get aggregate statistics for all searches in an event"""
        query = SearchRetrieval.query.filter_by(event_id=event_id)
        
        if model_type:
            query = query.filter_by(model_type=model_type)
        
        searches = query.all()
        
        if not searches:
            return None
        
        # Aggregate statistics
        total_searches = len(searches)
        total_matches = sum(s.num_matches for s in searches)
        avg_matches = total_matches / total_searches if total_searches > 0 else 0
        
        avg_similarity = np.mean([s.avg_similarity for s in searches if s.avg_similarity])
        max_similarity = max(s.max_similarity for s in searches if s.max_similarity)
        min_similarity = min(s.min_similarity for s in searches if s.min_similarity)
        
        avg_processing_time = np.mean([s.processing_time_ms for s in searches if s.processing_time_ms])
        
        return {
            'total_searches': total_searches,
            'total_matches': total_matches,
            'avg_matches_per_search': avg_matches,
            'avg_similarity': avg_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'avg_processing_time_ms': avg_processing_time,
            'searches': searches
        }
    
    @staticmethod
    def compare_models(event_id):
        """Compare performance of both models on the same event"""
        facenet_stats = SearchEvaluator.get_search_statistics(event_id, 'facenet')
        arcface_stats = SearchEvaluator.get_search_statistics(event_id, 'arcface')
        
        comparison = {
            'facenet': facenet_stats,
            'arcface': arcface_stats
        }
        
        if facenet_stats and arcface_stats:
            # Which model found more matches?
            comparison['better_recall'] = 'facenet' if facenet_stats['avg_matches_per_search'] > arcface_stats['avg_matches_per_search'] else 'arcface'
            
            # Which model is faster?
            comparison['faster'] = 'facenet' if facenet_stats['avg_processing_time_ms'] < arcface_stats['avg_processing_time_ms'] else 'arcface'
            
            # Which model has better quality matches (higher avg similarity)?
            comparison['higher_quality'] = 'facenet' if facenet_stats['avg_similarity'] > arcface_stats['avg_similarity'] else 'arcface'
        
        return comparison
