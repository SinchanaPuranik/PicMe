import numpy as np
from app.models import Photo, FaceEmbedding
from app import db


def find_matching_photos(query_embedding, event_id, model_type='facenet', threshold=0.6, top_k=50):
    """
    Find photos matching the query face embedding
    
    Args:
        query_embedding: Query face embedding vector
        event_id: Event ID to search within
        model_type: 'facenet' or 'arcface'
        threshold: Similarity threshold for matching
        top_k: Maximum number of results to return
        
    Returns:
        List of (Photo, similarity_score) tuples, sorted by similarity
    """
    # Get all embeddings for the event with the specified model type
    embeddings = db.session.query(FaceEmbedding, Photo).join(
        Photo, FaceEmbedding.photo_id == Photo.id
    ).filter(
        Photo.event_id == event_id,
        Photo.processed == True,
        FaceEmbedding.model_type == model_type
    ).all()
    
    if not embeddings:
        return []
    
    # Compute similarities
    matches = []
    for embedding_obj, photo in embeddings:
        stored_embedding = embedding_obj.get_embedding()
        
        if model_type == 'facenet':
            # FaceNet uses Euclidean distance (lower is better)
            distance = np.linalg.norm(query_embedding - stored_embedding)
            # Convert distance to similarity (0-1, higher is better)
            similarity = 1.0 / (1.0 + distance)
            
            # Apply threshold (distance < threshold)
            if distance < threshold:
                matches.append((photo, similarity))
        else:
            # ArcFace uses cosine similarity (higher is better)
            similarity = compute_cosine_similarity(query_embedding, stored_embedding)
            
            # Apply threshold (similarity > threshold)
            if similarity > threshold:
                matches.append((photo, similarity))
    
    # Remove duplicates (same photo with multiple faces)
    unique_matches = {}
    for photo, similarity in matches:
        if photo.id not in unique_matches or similarity > unique_matches[photo.id][1]:
            unique_matches[photo.id] = (photo, similarity)
    
    # Sort by similarity (descending)
    sorted_matches = sorted(unique_matches.values(), key=lambda x: x[1], reverse=True)
    
    # Return top K results
    return sorted_matches[:top_k]


def compute_cosine_similarity(embedding1, embedding2):
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Cosine similarity score (0-1)
    """
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


def compute_euclidean_distance(embedding1, embedding2):
    """
    Compute Euclidean distance between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Euclidean distance
    """
    return np.linalg.norm(embedding1 - embedding2)


def batch_match_faces(query_embeddings, event_id, model_type='facenet', threshold=0.6):
    """
    Match multiple query faces against event photos
    
    Args:
        query_embeddings: List of query face embeddings
        event_id: Event ID to search within
        model_type: 'facenet' or 'arcface'
        threshold: Similarity threshold for matching
        
    Returns:
        Dictionary mapping query index to list of matching photos
    """
    results = {}
    
    for idx, query_embedding in enumerate(query_embeddings):
        matches = find_matching_photos(query_embedding, event_id, model_type, threshold)
        results[idx] = matches
    
    return results
