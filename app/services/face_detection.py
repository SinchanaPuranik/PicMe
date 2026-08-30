import cv2
import numpy as np
from mtcnn import MTCNN
import os

# Initialize detectors lazily
_mtcnn_detector = None
_haar_cascade = None
_dnn_detector = None
_retinaface_detector = None


def get_mtcnn_detector():
    """Lazy initialization of MTCNN detector"""
    global _mtcnn_detector
    if _mtcnn_detector is None:
        _mtcnn_detector = MTCNN()
    return _mtcnn_detector


def get_haar_cascade():
    """Lazy initialization of Haar Cascade detector"""
    global _haar_cascade
    if _haar_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        _haar_cascade = cv2.CascadeClassifier(cascade_path)
    return _haar_cascade


def get_dnn_detector():
    """Lazy initialization of DNN (Deep Neural Network) detector"""
    global _dnn_detector
    if _dnn_detector is None:
        # Using OpenCV's pre-trained DNN face detector
        modelFile = "models/res10_300x300_ssd_iter_140000.caffemodel"
        configFile = "models/deploy.prototxt"
        
        # Try to load from models directory, otherwise use cv2.dnn default
        if os.path.exists(modelFile) and os.path.exists(configFile):
            _dnn_detector = cv2.dnn.readNetFromCaffe(configFile, modelFile)
        else:
            print("DNN model files not found. Download from: https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector")
            _dnn_detector = None
    return _dnn_detector


def get_retinaface_detector():
    """Lazy initialization of RetinaFace detector"""
    global _retinaface_detector
    if _retinaface_detector is None:
        try:
            from insightface.app import FaceAnalysis
            _retinaface_detector = FaceAnalysis(providers=['CPUExecutionProvider'])
            _retinaface_detector.prepare(ctx_id=-1, det_size=(640, 640))
        except Exception as e:
            print(f"Failed to initialize RetinaFace: {str(e)}")
            _retinaface_detector = None
    return _retinaface_detector


def detect_faces_mtcnn(rgb_image, min_confidence=0.7):
    """Detect faces using MTCNN"""
    detector = get_mtcnn_detector()
    faces = detector.detect_faces(rgb_image)
    
    detected_faces = []
    for face in faces:
        if face['confidence'] >= min_confidence:
            x, y, w, h = face['box']
            x, y = max(0, x), max(0, y)
            x2, y2 = min(rgb_image.shape[1], x + w), min(rgb_image.shape[0], y + h)
            face_img = rgb_image[y:y2, x:x2]
            
            if face_img.size > 0:
                detected_faces.append((face_img, [x, y, w, h], face.get('keypoints', {})))
    
    return detected_faces


def detect_faces_haar(rgb_image, min_confidence=0.7):
    """Detect faces using Haar Cascade"""
    detector = get_haar_cascade()
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    detected_faces = []
    for (x, y, w, h) in faces:
        x, y = max(0, x), max(0, y)
        x2, y2 = min(rgb_image.shape[1], x + w), min(rgb_image.shape[0], y + h)
        face_img = rgb_image[y:y2, x:x2]
        
        if face_img.size > 0:
            detected_faces.append((face_img, [x, y, w, h], {}))
    
    return detected_faces


def detect_faces_dnn(rgb_image, min_confidence=0.5):
    """Detect faces using DNN (Caffe model)"""
    detector = get_dnn_detector()
    if detector is None:
        return []
    
    h, w = rgb_image.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(rgb_image, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0)
    )
    
    detector.setInput(blob)
    detections = detector.forward()
    
    detected_faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        if confidence >= min_confidence:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x2, y2) = box.astype("int")
            
            x, y = max(0, x), max(0, y)
            x2, y2 = min(w, x2), min(h, y2)
            
            face_img = rgb_image[y:y2, x:x2]
            if face_img.size > 0:
                detected_faces.append((face_img, [x, y, x2-x, y2-y], {}))
    
    return detected_faces


def detect_faces_retinaface(rgb_image, min_confidence=0.5):
    """Detect faces using RetinaFace (InsightFace)"""
    detector = get_retinaface_detector()
    if detector is None:
        return []
    
    try:
        # Convert RGB to BGR for InsightFace
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        faces = detector.get(bgr_image)
        
        detected_faces = []
        for face in faces:
            if face.det_score >= min_confidence:
                bbox = face.bbox.astype(int)
                x, y, x2, y2 = bbox
                x, y = max(0, x), max(0, y)
                x2, y2 = min(rgb_image.shape[1], x2), min(rgb_image.shape[0], y2)
                
                face_img = rgb_image[y:y2, x:x2]
                if face_img.size > 0:
                    keypoints = {}
                    if hasattr(face, 'kps') and face.kps is not None:
                        keypoints = {
                            'left_eye': tuple(face.kps[0]),
                            'right_eye': tuple(face.kps[1]),
                            'nose': tuple(face.kps[2]),
                            'left_mouth': tuple(face.kps[3]),
                            'right_mouth': tuple(face.kps[4])
                        }
                    detected_faces.append((face_img, [x, y, x2-x, y2-y], keypoints))
        
        return detected_faces
    except Exception as e:
        print(f"Error in RetinaFace detection: {str(e)}")
        return []


def detect_faces_in_image(image_path, detector='mtcnn', min_confidence=0.7):
    """
    Detect faces in an image using various detectors
    
    Args:
        image_path: Path to the image file
        detector: Detector type - 'mtcnn', 'haar', 'dnn', 'retinaface', or 'all'
        min_confidence: Minimum confidence threshold for face detection
        
    Returns:
        List of tuples (face_image, bounding_box, landmarks)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return []
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Map detector names to functions
        detector_map = {
            'mtcnn': detect_faces_mtcnn,
            'haar': detect_faces_haar,
            'dnn': detect_faces_dnn,
            'retinaface': detect_faces_retinaface
        }
        
        if detector == 'all':
            # Try all detectors and combine results
            all_faces = []
            for det_name, det_func in detector_map.items():
                try:
                    faces = det_func(rgb_image, min_confidence)
                    all_faces.extend(faces)
                except Exception as e:
                    print(f"Error with {det_name} detector: {str(e)}")
            return all_faces
        elif detector in detector_map:
            return detector_map[detector](rgb_image, min_confidence)
        else:
            print(f"Unknown detector: {detector}. Using MTCNN as default.")
            return detect_faces_mtcnn(rgb_image, min_confidence)
        
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


def get_available_detectors():
    """
    Get list of available face detectors
    
    Returns:
        Dictionary with detector names and their availability status
    """
    detectors = {
        'mtcnn': False,
        'haar': False,
        'dnn': False,
        'retinaface': False
    }
    
    try:
        get_mtcnn_detector()
        detectors['mtcnn'] = True
    except:
        pass
    
    try:
        get_haar_cascade()
        detectors['haar'] = True
    except:
        pass
    
    try:
        detector = get_dnn_detector()
        detectors['dnn'] = detector is not None
    except:
        pass
    
    try:
        detector = get_retinaface_detector()
        detectors['retinaface'] = detector is not None
    except:
        pass
    
    return detectors


def benchmark_detectors(image_path, min_confidence=0.9):
    """
    Benchmark all available detectors on a single image
    
    Args:
        image_path: Path to the image file
        min_confidence: Minimum confidence threshold
        
    Returns:
        Dictionary with detector names and their results
    """
    import time
    
    results = {}
    detectors = ['mtcnn', 'haar', 'dnn', 'retinaface']
    
    for detector_name in detectors:
        try:
            start_time = time.time()
            faces = detect_faces_in_image(image_path, detector=detector_name, min_confidence=min_confidence)
            end_time = time.time()
            
            results[detector_name] = {
                'num_faces': len(faces),
                'time_seconds': end_time - start_time,
                'success': True
            }
        except Exception as e:
            results[detector_name] = {
                'num_faces': 0,
                'time_seconds': 0,
                'success': False,
                'error': str(e)
            }
    
    return results
