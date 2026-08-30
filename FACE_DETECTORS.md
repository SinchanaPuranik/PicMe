# Face Detectors Guide

This document provides information about the face detection algorithms available in PICME.

## Available Detectors

### 1. MTCNN (Multi-task Cascaded Convolutional Networks)
**Status:** ✅ Available by default

**Description:**
- Deep learning-based face detector
- Uses a cascade of three neural networks (P-Net, R-Net, O-Net)
- Provides face landmarks (eyes, nose, mouth)
- Handles various face poses and sizes

**Performance:**
- **Speed:** Medium (2-5 seconds per image)
- **Accuracy:** High (90-95%)
- **Best for:** General purpose, balanced performance

**Configuration:**
```python
detector = 'mtcnn'
min_confidence = 0.9  # Range: 0.0-1.0
```

---

### 2. Haar Cascade
**Status:** ✅ Available (OpenCV built-in)

**Description:**
- Classical computer vision technique
- Uses Haar-like features and AdaBoost
- Fast but less accurate than deep learning methods
- Best for frontal face detection

**Performance:**
- **Speed:** Fast (<1 second per image)
- **Accuracy:** Medium (70-85%)
- **Best for:** Quick detection, frontal faces, low-resource environments

**Configuration:**
```python
detector = 'haar'
min_confidence = 0.9  # Not as meaningful for Haar
```

**Pros:**
- Very fast
- No deep learning required
- Works on CPU efficiently

**Cons:**
- Lower accuracy
- Struggles with non-frontal faces
- More false positives

---

### 3. DNN (Deep Neural Network - Caffe Model)
**Status:** ⚠️ Requires model files

**Description:**
- Uses OpenCV's DNN module with pre-trained Caffe model
- ResNet-10 based architecture
- Good balance of speed and accuracy

**Performance:**
- **Speed:** Medium-Fast (1-3 seconds per image)
- **Accuracy:** High (85-92%)
- **Best for:** Various angles, good accuracy with decent speed

**Setup:**
1. Download model files:
   - `res10_300x300_ssd_iter_140000.caffemodel`
   - `deploy.prototxt`
2. Place in `models/` directory

**Download Links:**
```bash
# From OpenCV GitHub repository
wget https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
wget https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

**Configuration:**
```python
detector = 'dnn'
min_confidence = 0.5  # Range: 0.0-1.0
```

---

### 4. RetinaFace (InsightFace)
**Status:** ✅ Available via InsightFace library

**Description:**
- State-of-the-art face detector
- Provides high-quality face landmarks (5 points)
- Best accuracy for challenging scenarios
- Part of InsightFace framework

**Performance:**
- **Speed:** Slow (5-10 seconds per image)
- **Accuracy:** Very High (95-98%)
- **Best for:** Maximum accuracy, landmark detection, difficult poses

**Configuration:**
```python
detector = 'retinaface'
min_confidence = 0.5  # Range: 0.0-1.0
```

**Features:**
- 5-point facial landmarks (both eyes, nose, mouth corners)
- Handles occlusions well
- Works with various face sizes
- Better with profile faces

**Pros:**
- Highest accuracy
- Robust to various conditions
- Provides quality landmarks

**Cons:**
- Slower processing
- Higher memory usage
- Requires more computation

---

## Comparison Table

| Detector | Speed | Accuracy | Landmarks | CPU-Friendly | GPU Boost |
|----------|-------|----------|-----------|--------------|-----------|
| **MTCNN** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Yes (5 pts) | Medium | Yes |
| **Haar Cascade** | ⭐⭐⭐⭐⭐ | ⭐⭐ | No | Excellent | No |
| **DNN** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | No | Good | Yes |
| **RetinaFace** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Yes (5 pts) | Poor | Yes |

---

## Usage in PICME

### Admin Interface

1. **Navigate to:** Admin Dashboard → Event → Process Photos
2. **Select Detector:** Choose from the dropdown menu
3. **Set Confidence:** Adjust threshold (0.5-0.95 recommended)
4. **Process:** Click "Start Processing"

### API Usage

```python
from app.services.face_detection import detect_faces_in_image

# Use specific detector
faces = detect_faces_in_image(
    image_path='path/to/image.jpg',
    detector='mtcnn',  # or 'haar', 'dnn', 'retinaface'
    min_confidence=0.9
)

# Returns: List of (face_image, bounding_box, landmarks)
for face_img, bbox, landmarks in faces:
    x, y, w, h = bbox
    # Process face...
```

### Programmatic Access

```python
from app.services.face_detection import (
    get_available_detectors,
    benchmark_detectors
)

# Check availability
detectors = get_available_detectors()
print(detectors)  # {'mtcnn': True, 'haar': True, ...}

# Benchmark all detectors
results = benchmark_detectors('test_image.jpg', min_confidence=0.9)
for detector, stats in results.items():
    print(f"{detector}: {stats['num_faces']} faces in {stats['time_seconds']:.2f}s")
```

---

## Recommendations

### For Event Photos (General Use)
**Recommended:** MTCNN
- Good balance of speed and accuracy
- Handles various poses
- Provides landmarks for alignment

### For Quick Processing
**Recommended:** Haar Cascade
- Fastest option
- Works well for frontal faces
- Lower resource usage

### For Maximum Accuracy
**Recommended:** RetinaFace
- Best detection quality
- Handles difficult scenarios
- Worth the extra processing time

### For Production Deployment
**Recommended:** DNN or MTCNN
- Good balance
- Reliable performance
- Reasonable resource usage

---

## Testing Detectors

### Test Page
Navigate to: **Admin Dashboard → Test Face Detectors**

This page shows:
- Detector availability status
- Performance comparison
- Benchmark results
- Processing time charts

### Manual Testing

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run benchmark script
python -c "
from app.services.face_detection import benchmark_detectors
results = benchmark_detectors('path/to/test_image.jpg')
import json
print(json.dumps(results, indent=2))
"
```

---

## Troubleshooting

### MTCNN Issues
```bash
pip install mtcnn
```

### DNN Model Not Found
Download models and place in `models/` directory:
```bash
mkdir models
cd models
# Download from OpenCV repository (see Setup section above)
```

### RetinaFace Errors
```bash
pip install insightface onnxruntime
```

### General Issues
- Ensure OpenCV is installed: `pip install opencv-python opencv-contrib-python`
- Check CUDA for GPU acceleration (optional)
- Verify image file paths are correct

---

## Performance Tips

1. **Use appropriate confidence thresholds:**
   - High quality photos: 0.9-0.95
   - Mixed quality: 0.7-0.85
   - Low quality: 0.5-0.7

2. **Choose detector based on needs:**
   - Speed priority → Haar Cascade
   - Accuracy priority → RetinaFace
   - Balance → MTCNN or DNN

3. **Batch processing:**
   - Process multiple photos in one session
   - Detector initialization happens once

4. **Image quality:**
   - Higher resolution = better detection
   - Good lighting helps all detectors
   - Frontal faces are easier to detect

---

## Future Enhancements

Potential additions:
- YOLO face detection
- MediaPipe face detection
- Custom trained models
- Face quality scoring
- Parallel processing
- GPU acceleration options

---

## References

- **MTCNN Paper:** Joint Face Detection and Alignment using Multi-task Cascaded Convolutional Networks
- **Haar Cascades:** Viola-Jones face detection framework
- **RetinaFace Paper:** Single-stage Dense Face Localisation in the Wild
- **OpenCV DNN:** https://github.com/opencv/opencv/tree/master/samples/dnn

---

For more information, visit the [PICME documentation](README.md) or contact the development team.
