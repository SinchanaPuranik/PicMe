# PICME - AI-Powered Photo Retrieval System

A face recognition system that allows event organizers to upload photos and attendees to find their photos using facial recognition.

## Features

### Day 1 - Foundation
- Flask backend with PostgreSQL database
- Admin/User authentication system
- Event creation and management
- Photo upload functionality
- Face detection pipeline

### Day 2 - AI Implementation
- Dual face recognition models (FaceNet & ArcFace)
- Face embedding generation and storage
- Webcam/selfie capture for face matching
- Photo retrieval with face matching
- Group photo handling

### Day 3 - Evaluation & Polish
- Performance evaluation metrics (Precision, Recall, F1-score)
- False positive/negative analysis
- Processing time benchmarks
- FaceNet vs ArcFace comparison
- Photo gallery with QR code generation
- Final UI polish and demo

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Face Detection**: MTCNN / RetinaFace
- **Face Recognition**: FaceNet, ArcFace
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Image Processing**: OpenCV, PIL
- **Deep Learning**: TensorFlow/Keras, PyTorch

## Project Structure

```
picme/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_detection.py
│   │   ├── facenet_service.py
│   │   ├── arcface_service.py
│   │   └── matching.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── templates/
│       ├── admin/
│       └── user/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up PostgreSQL database
6. Configure environment variables
7. Run migrations: `flask db upgrade`
8. Start server: `python run.py`

## Usage

### Admin Flow
1. Login as admin
2. Create event
3. Upload photos
4. System detects faces and generates embeddings

### User Flow
1. Select event
2. Capture selfie via webcam
3. System matches face with photos
4. View and download matched photos

## Performance Metrics

The system evaluates both FaceNet and ArcFace models on:
- Precision
- Recall
- F1-Score
- False Positives/Negatives
- Processing Time

## License

MIT
