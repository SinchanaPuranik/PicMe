import numpy as np
import cv2
import os

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False


class ArcFaceService:
    """Service for ArcFace face recognition using InsightFace"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - reuse same model instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize ArcFace model from InsightFace"""
        if self._initialized:
            return
            
        self._initialized = True
        self.embedding_size = 512
        self.app = None
        
        try:
            if not INSIGHTFACE_AVAILABLE:
                print("Warning: InsightFace not available. Install it with: pip install insightface")
                self.app = None
                return
            
            # Initialize InsightFace with ArcFace model
            # Use 'detection' for face detection and 'recognition' for ArcFace embeddings
            self.app = FaceAnalysis(providers=['CPUProvider'])
            self.app.prepare(ctx_id=-1, det_thresh=0.5)  # Use CPU
            
            print("ArcFace (InsightFace) model loaded successfully")
            
        except Exception as e:
            print(f"Error loading ArcFace model: {str(e)}")
            import traceback
            traceback.print_exc()
            self.app = None
    
    def generate_embedding(self, face_img):
        """
        Generate face embedding using ArcFace (InsightFace)
        
        Args:
            face_img: Face image array (BGR or RGB)
            
        Returns:
            512-dimensional embedding vector
        """
        if self.app is None:
            print("ArcFace model not loaded")
            return None
        
        try:
            # Convert to uint8 if needed
            if face_img.dtype != np.uint8:
                if face_img.max() <= 1.0:
                    face_img = (face_img * 255).astype('uint8')
                else:
                    face_img = face_img.astype('uint8')
            
            # Ensure it's BGR format (OpenCV standard)
            if len(face_img.shape) == 3 and face_img.shape[2] == 3:
                # Resize to expected input size
                face_img = cv2.resize(face_img, (112, 112))
            
            # Use InsightFace to get embedding
            # Create a dummy image with the face for processing
            faces = self.app.get(face_img)
            
            if len(faces) == 0:
                print("No face detected in image")
                return None
            
            # Get embedding from the first (and should be only) face
            embedding = faces[0].embedding
            
            # Ensure it's normalized
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            print(f"Error generating ArcFace embedding: {str(e)}")
            import traceback
            traceback.print_exc()
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
    
    def is_same_person(self, embedding1, embedding2, threshold=0.4):
        """
        Determine if two embeddings represent the same person
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            threshold: Distance threshold for matching
            
        Returns:
            Boolean indicating if same person
        """
        similarity = self.compute_similarity(embedding1, embedding2)
        return similarity > threshold
