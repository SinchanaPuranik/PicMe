import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.face_detection import detect_faces_in_image, preprocess_face
import numpy as np


class TestFaceDetection(unittest.TestCase):
    """Test cases for face detection functionality"""
    
    def test_detect_faces_invalid_path(self):
        """Test face detection with invalid image path"""
        faces = detect_faces_in_image('invalid_path.jpg')
        self.assertEqual(len(faces), 0)
    
    def test_preprocess_face(self):
        """Test face preprocessing"""
        # Create dummy face image
        face_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Preprocess
        processed = preprocess_face(face_img, target_size=(160, 160))
        
        # Check shape and value range
        self.assertEqual(processed.shape, (160, 160, 3))
        self.assertTrue(processed.max() <= 1.0)
        self.assertTrue(processed.min() >= 0.0)


if __name__ == '__main__':
    unittest.main()
