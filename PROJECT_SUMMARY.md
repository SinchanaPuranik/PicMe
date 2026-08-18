# PICME Project Summary

## 🎯 Project Overview

**PICME** is an AI-powered photo retrieval system that uses advanced face recognition technology to help event attendees find their photos quickly and easily. The system employs dual AI models (FaceNet and ArcFace) for face matching and provides comprehensive performance metrics for comparison.

## 📋 Features Implemented

### ✅ Core Features
- ✓ Flask backend with PostgreSQL database
- ✓ Admin/User authentication system
- ✓ Event creation and management
- ✓ Photo upload functionality (multiple files)
- ✓ Face detection using MTCNN
- ✓ FaceNet implementation (128D embeddings)
- ✓ ArcFace implementation (512D embeddings)
- ✓ Webcam/selfie capture for face matching
- ✓ Photo retrieval with similarity scoring
- ✓ Group photo handling
- ✓ QR code generation for events

### ✅ Evaluation & Metrics
- ✓ Performance evaluation framework
- ✓ Precision, Recall, F1-Score calculation
- ✓ False positive/negative tracking
- ✓ Processing time benchmarking
- ✓ Model comparison (FaceNet vs ArcFace)
- ✓ Database storage for metrics

### ✅ User Interface
- ✓ Responsive design with Bootstrap 5
- ✓ Admin dashboard with statistics
- ✓ Event management interface
- ✓ Photo upload with preview
- ✓ Webcam integration for selfie capture
- ✓ Real-time face matching
- ✓ Photo gallery with download
- ✓ Results display with similarity scores

## 📁 Project Structure

```
MajorProject/
├── app/
│   ├── __init__.py              # App initialization
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py             # Admin routes
│   │   ├── user.py              # User routes
│   │   ├── auth.py              # Authentication
│   │   └── main.py              # Main routes
│   ├── services/
│   │   ├── face_detection.py   # MTCNN face detection
│   │   ├── facenet_service.py  # FaceNet model
│   │   ├── arcface_service.py  # ArcFace model
│   │   └── matching.py          # Face matching logic
│   ├── static/
│   │   ├── css/style.css        # Custom styles
│   │   ├── js/main.js           # JavaScript utilities
│   │   └── uploads/events/      # Uploaded photos
│   └── templates/
│       ├── base.html            # Base template
│       ├── index.html           # Homepage
│       ├── about.html           # About page
│       ├── admin/               # Admin templates
│       │   ├── dashboard.html
│       │   ├── create_event.html
│       │   ├── view_event.html
│       │   ├── upload_photos.html
│       │   ├── process_photos.html
│       │   └── metrics.html
│       ├── user/                # User templates
│       │   ├── select_event.html
│       │   ├── capture_selfie.html
│       │   ├── results.html
│       │   └── gallery.html
│       └── auth/                # Auth templates
│           ├── login.html
│           └── register.html
├── tests/
│   ├── __init__.py
│   ├── test_face_detection.py   # Face detection tests
│   ├── test_matching.py         # Matching tests
│   └── evaluate_models.py       # Model evaluation script
├── models/                       # AI model storage
├── config.py                     # Configuration
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── setup_database.py             # Database setup script
├── README.md                     # Main documentation
├── INSTALLATION.md               # Installation guide
├── USAGE.md                      # Usage guide
├── API.md                        # API documentation
├── Dockerfile                    # Docker configuration
└── docker-compose.yml            # Docker Compose config
```

## 🛠️ Technology Stack

### Backend
- **Flask 3.0** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-Migrate** - Database migrations

### AI/ML
- **MTCNN** - Face detection
- **FaceNet** - Face recognition (128D embeddings)
- **ArcFace** - Face recognition (512D embeddings)
- **TensorFlow 2.15** - Deep learning framework
- **PyTorch 2.1** - Deep learning framework
- **OpenCV** - Image processing

### Frontend
- **HTML5/CSS3**
- **JavaScript (ES6+)**
- **Bootstrap 5.3** - UI framework
- **Font Awesome 6.4** - Icons
- **WebRTC** - Webcam access

### Additional
- **QR Code** - Event QR generation
- **Pillow** - Image manipulation
- **NumPy** - Numerical operations
- **scikit-learn** - Metrics calculation

## 🔄 System Workflow

### Admin Flow
```
Login → Create Event → Upload Photos → Process Photos (Detect Faces + Generate Embeddings) → View Metrics
```

### User Flow
```
Select Event → Capture Selfie/Upload Photo → Choose AI Model → Search → View Results → Download Photos
```

### Face Recognition Pipeline
```
Input Photo → MTCNN Detection → Face Extraction → Embedding Generation (FaceNet/ArcFace) → 
Similarity Computation → Threshold Matching → Results Ranking → Output Matches
```

## 📊 Database Schema

### Tables
1. **users** - User accounts (admin/regular)
2. **events** - Event information
3. **photos** - Uploaded photos
4. **face_embeddings** - Stored face embeddings (both models)
5. **performance_metrics** - Evaluation results

### Relationships
- User → Events (one-to-many)
- Event → Photos (one-to-many)
- Photo → FaceEmbeddings (one-to-many)

## 🎯 AI Models Comparison

| Feature | FaceNet | ArcFace |
|---------|---------|---------|
| **Embedding Size** | 128 dimensions | 512 dimensions |
| **Distance Metric** | Euclidean | Cosine Similarity |
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Moderate |
| **Accuracy** | 85-90% | 90-95% |
| **Memory Usage** | Low | Moderate |
| **Best For** | Large events, quick searches | High accuracy needs |
| **Threshold** | < 0.6 (distance) | > 0.4 (similarity) |

## 📈 Performance Metrics

The system evaluates both models on:
- **Precision** - Accuracy of matches (fewer false positives)
- **Recall** - Completeness of results (fewer false negatives)
- **F1-Score** - Balanced metric
- **False Positives** - Incorrectly matched photos
- **False Negatives** - Missed photos
- **Processing Time** - Speed benchmark

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd MajorProject

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python setup_database.py

# 5. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 6. Run application
python run.py
```

Access at: http://localhost:5000

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

## 📖 Documentation

- **README.md** - Project overview and features
- **INSTALLATION.md** - Detailed installation guide
- **USAGE.md** - Complete usage instructions
- **API.md** - API endpoint documentation

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run model evaluation
python tests/evaluate_models.py
```

## 🔒 Security Features

- Password hashing (Werkzeug)
- Session management (Flask-Login)
- SQL injection protection (SQLAlchemy)
- File upload validation
- Admin role-based access control
- CSRF protection (Flask-WTF)

## 🎨 UI Features

- Responsive design (mobile-friendly)
- Real-time webcam capture
- Drag-and-drop file upload
- Loading indicators
- Image preview
- Similarity score badges
- QR code display
- Photo lightbox/modal view
- Alert notifications

## 📦 Deployment Options

### Development
```bash
python run.py
```

### Production (Linux/Mac)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Production (Windows)
```bash
waitress-serve --listen=*:5000 run:app
```

### Docker
```bash
docker-compose up -d
```

## 🐛 Known Limitations

1. **Face Detection**
   - Requires minimum 50x50 pixel face size
   - Works best with frontal faces
   - May struggle with extreme angles

2. **Performance**
   - Processing time increases with photo count
   - Memory usage scales with embeddings
   - Webcam requires HTTPS (except localhost)

3. **Accuracy**
   - Depends on photo quality
   - Lighting conditions affect results
   - Heavy makeup/accessories may reduce accuracy

## 🔮 Future Enhancements

- [ ] Background processing with Celery
- [ ] Redis caching for embeddings
- [ ] Mobile app (React Native)
- [ ] Real-time face detection in video
- [ ] Advanced age/gender classification
- [ ] Face clustering for event insights
- [ ] Social media integration
- [ ] Bulk download (ZIP)
- [ ] Email notifications
- [ ] Payment integration for commercial use

## 📝 Development Notes

### Adding New Routes
1. Create route function in appropriate blueprint file
2. Add template in templates directory
3. Update navigation in base.html

### Adding New Models
1. Define model in models.py
2. Create migration: `flask db migrate -m "message"`
3. Apply migration: `flask db upgrade`

### Customizing AI Models
- Models are in `app/services/`
- Adjust thresholds in `config.py`
- Replace with pre-trained weights in `models/`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Credits

- **MTCNN** - Face detection
- **FaceNet** - Google's face recognition model
- **ArcFace** - Advanced face recognition
- **Bootstrap** - UI framework
- **Font Awesome** - Icons

## 📞 Support

For issues and questions:
1. Check documentation files
2. Review error logs
3. Search existing issues
4. Create new issue with details

## 🎓 Academic Use

This project is ideal for:
- Computer Vision courses
- Machine Learning projects
- Web Development capstone
- AI model comparison research

## 📊 Project Statistics

- **Total Files:** 50+
- **Lines of Code:** 5000+
- **Python Files:** 20+
- **HTML Templates:** 15+
- **JavaScript Files:** 2
- **CSS Files:** 1
- **Test Files:** 3

## ✅ Project Completion Checklist

- [x] Backend architecture
- [x] Database models
- [x] Authentication system
- [x] Admin interface
- [x] User interface
- [x] Face detection integration
- [x] FaceNet implementation
- [x] ArcFace implementation
- [x] Webcam capture
- [x] Face matching
- [x] Photo retrieval
- [x] Group photo handling
- [x] QR code generation
- [x] Performance metrics
- [x] Model comparison
- [x] Evaluation framework
- [x] Testing suite
- [x] Documentation
- [x] Deployment configs
- [x] Docker support

## 🎉 Project Status

**Status:** ✅ COMPLETE

All requirements have been implemented. The system is fully functional with both FaceNet and ArcFace models, comprehensive evaluation metrics, and a complete user interface for both admin and user workflows.

---

**Built with ❤️ for AI-powered photo retrieval**
