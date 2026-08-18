# PICME Quick Start Guide

## ✅ Installation Complete!

All dependencies are installed. The project is configured to use SQLite for easy setup (no PostgreSQL required for testing).

## 🚀 Start the Application

### Option 1: Quick Start (Recommended)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Initialize database
$env:FLASK_APP="run.py"
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
python run.py
```

### Option 2: One-Line Start

```powershell
.\venv\Scripts\Activate.ps1 ; $env:FLASK_APP="run.py" ; flask db init ; flask db migrate -m "Initial" ; flask db upgrade ; python run.py
```

## 📱 Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## 🔐 Default Login

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## 📋 Quick Workflow

### For Admins:
1. Login with admin credentials
2. Click "Create New Event"
3. Fill in event details and create
4. Click "Upload Photos" and select multiple photos
5. Click "Process Unprocessed Photos" to detect faces
6. View generated QR code for event

### For Users:
1. Go to homepage
2. Click "Find My Photos"
3. Select an event
4. Capture a selfie or upload a photo
5. Choose AI model (FaceNet or ArcFace)
6. Click "Search Photos"
7. Download your matched photos

## 🧪 Test the System

### Create Test Event
```
Name: Test Event 2026
Description: Testing PICME system
Date: 2026-08-15
Location: Test Campus
```

### Upload Sample Photos
- Use photos with clear, visible faces
- JPG, PNG, or GIF format
- Multiple faces per photo supported

### Process Photos
- Click "Process Unprocessed Photos"
- Wait for face detection and embedding generation
- Check dashboard for statistics

### Search for Photos
- Capture a selfie (allow webcam access)
- Try both FaceNet and ArcFace models
- Compare results and similarity scores

## 📊 View Performance Metrics

1. Go to Admin Dashboard
2. Click "View Performance Metrics"
3. See model comparison data

## 🔧 Troubleshooting

### Database Issues
```powershell
# Reset database
Remove-Item picme_dev.db -ErrorAction SilentlyContinue
Remove-Item -Recurse migrations -ErrorAction SilentlyContinue
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Webcam Not Working
- Allow browser permission
- Use Chrome or Edge browser
- Or upload a selfie instead

### Port Already in Use
```powershell
# Use different port
$env:FLASK_RUN_PORT="8000"
python run.py
```

### Module Not Found
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Documentation

- **README.md** - Project overview
- **INSTALLATION.md** - Detailed setup
- **USAGE.md** - Complete user guide
- **API.md** - API documentation
- **PROJECT_SUMMARY.md** - Technical summary

## 🎯 Next Steps

1. ✅ Start the application
2. ✅ Login as admin
3. ✅ Create your first event
4. ✅ Upload test photos
5. ✅ Process photos
6. ✅ Test face matching
7. ✅ Compare FaceNet vs ArcFace
8. ✅ View performance metrics

## 💡 Tips

- **Photo Quality:** Use high-resolution photos for better results
- **Face Detection:** Ensure faces are clearly visible and well-lit
- **Model Selection:** FaceNet is faster, ArcFace is more accurate
- **Processing Time:** Depends on number of photos and faces
- **Batch Size:** Process 50-100 photos at a time for optimal performance

## 🐛 Common Issues

**Issue: "Table already exists"**
```powershell
flask db stamp head
```

**Issue: "No module named 'app'"**
```powershell
# Make sure you're in project root
cd C:\Users\acer\MajorProject
.\venv\Scripts\Activate.ps1
```

**Issue: TensorFlow warnings**
- Normal - TensorFlow shows info messages
- Application works fine

## 🔄 Restart Application

```powershell
# Stop: Press Ctrl+C in terminal

# Restart:
.\venv\Scripts\Activate.ps1
python run.py
```

## 📞 Need Help?

Check these files:
1. INSTALLATION.md - Full installation guide
2. USAGE.md - Detailed usage instructions
3. README.md - Project documentation

## 🎉 You're Ready!

Your PICME system is ready to use. Start by creating an event and uploading photos!

**Happy Face Matching! 📸**
