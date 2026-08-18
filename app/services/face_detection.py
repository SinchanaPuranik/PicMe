import cv2
import numpy as np
from mtcnn import MTCNN

# Initialize MTCNN detector
mtcnn_detector = MTCNN()


def detect_faces_in_image(image_path, detector='mtcnn', min_confidence=0.9):
    """
    Detect faces in an image using MTCNN
    
    Args:
        image_path: Path to the image file
        detector: Detector type ('mtcnn' or 'retinaface') - currently only MTCNN is supported
        min_confidence: Minimum confidence threshold for face detection
        
    Returns:
        List of tuples (face_image, bounding_box)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return []
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = mtcnn_detector.detect_faces(rgb_image)
        
        detected_faces = []
        for face in faces:
            if face['confidence'] >= min_confidence:
                x, y, w, h = face['box']
                x, y = max(0, x), max(0, y)
                x2, y2 = min(rgb_image.shape[1], x + w), min(rgb_image.shape[0], y + h)
                face_img = rgb_image[y:y2, x:x2]
                
                if face_img.size > 0:
                    detected_faces.append((face_img, [x, y, w, h]))
        
        return detected_faces
    except Exception as e:
        print(f"Error detecting faces: {str(e)}")
        return []


def preprocess_face(face_img, target_size=(160, 160)):
    """
    Preprocess face image for model input
    
    Args:
        face_img: Face image array (RGB)
        target_size: Target size for resizing
        
    Returns:
        Preprocessed face image
    """
    try:
        face_resized = cv2.resize(face_img, target_size)
        face_normalized = face_resized.astype('float32') / 255.0
        return face_normalized
    except Exception as e:
        print(f"Error preprocessing face: {str(e)}")
        return None


def align_face(face_img, landmarks):
    """
    Align face based on facial landmarks
    
    Args:
        face_img: Face image array
        landmarks: Dictionary of facial landmarks
        
    Returns:
        Aligned face image
    """
    try:
        left_eye = landmarks['left_eye']
        right_eye = landmarks['right_eye']
        
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX))
        
        eyes_center = ((left_eye[0] + right_eye[0]) // 2, 
                      (left_eye[1] + right_eye[1]) // 2)
        M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
        
        aligned = cv2.warpAffine(face_img, M, (face_img.shape[1], face_img.shape[0]))
        return aligned
    except Exception as e:
        print(f"Error aligning face: {str(e)}")
        return face_img
