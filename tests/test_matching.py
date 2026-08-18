import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.matching import compute_cosine_similarity, compute_euclidean_distance
import numpy as np


class TestMatching(unittest.TestCase):
    """Test cases for face matching functionality"""
    
    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical embeddings"""
        embedding = np.random.rand(128)
        similarity = compute_cosine_similarity(embedding, embedding)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors"""
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.0, 1.0, 0.0])
        similarity = compute_cosine_similarity(embedding1, embedding2)
        self.assertAlmostEqual(similarity, 0.0, places=5)
    
    def test_euclidean_distance_identical(self):
        """Test Euclidean distance with identical embeddings"""
        embedding = np.random.rand(128)
        distance = compute_euclidean_distance(embedding, embedding)
        self.assertAlmostEqual(distance, 0.0, places=5)
    
    def test_euclidean_distance_different(self):
        """Test Euclidean distance with different embeddings"""
        embedding1 = np.zeros(128)
        embedding2 = np.ones(128)
        distance = compute_euclidean_distance(embedding1, embedding2)
        self.assertGreater(distance, 0.0)


if __name__ == '__main__':
    unittest.main()
