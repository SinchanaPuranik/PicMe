import numpy as np
import cv2
from keras_facenet import FaceNet


class FaceNetService:
    """Service for FaceNet face recognition"""
    
    def __init__(self):
        """Initialize FaceNet model"""
        try:
            self.model = FaceNet()
            self.input_size = (160, 160)
            print("FaceNet model loaded successfully")
        except Exception as e:
            print(f"Error loading FaceNet model: {str(e)}")
            self.model = None
    
    def generate_embedding(self, face_img):
        """
        Generate face embedding using FaceNet
        
        Args:
            face_img: Face image array (RGB)
            
        Returns:
            128-dimensional embedding vector
        """
        if self.model is None:
            print("FaceNet model not loaded")
            return None
        
        try:
            # Preprocess face
            face_resized = cv2.resize(face_img, self.input_size)
            
            # FaceNet expects images in range [0, 255]
            if face_resized.max() <= 1.0:
                face_resized = (face_resized * 255).astype('uint8')
            
            # Add batch dimension
            face_batch = np.expand_dims(face_resized, axis=0)
            
            # Generate embedding
            embedding = self.model.embeddings(face_batch)
            
            # Return as 1D array
            return embedding[0]
            
        except Exception as e:
            print(f"Error generating FaceNet embedding: {str(e)}")
            return None
    
    def compute_distance(self, embedding1, embedding2):
        """
        Compute Euclidean distance between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Euclidean distance
        """
        return np.linalg.norm(embedding1 - embedding2)
    
    def compute_similarity(self, embedding1, embedding2):
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
    
    def is_same_person(self, embedding1, embedding2, threshold=0.6):
        """
        Determine if two embeddings represent the same person
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            threshold: Distance threshold for matching
            
        Returns:
            Boolean indicating if same person
        """
        distance = self.compute_distance(embedding1, embedding2)
        return distance < threshold
