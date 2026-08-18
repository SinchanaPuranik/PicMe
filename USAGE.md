# PICME Usage Guide

## Table of Contents

1. [Admin Workflow](#admin-workflow)
2. [User Workflow](#user-workflow)
3. [Model Comparison](#model-comparison)
4. [Performance Evaluation](#performance-evaluation)
5. [Best Practices](#best-practices)

## Admin Workflow

### 1. Login as Admin

1. Navigate to http://localhost:5000
2. Click "Login"
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`

### 2. Create an Event

1. Go to Admin Dashboard
2. Click "Create New Event"
3. Fill in event details:
   - **Name:** Event name (e.g., "College Fest 2026")
   - **Description:** Brief description
   - **Event Date:** Select date
   - **Location:** Event venue
4. Click "Create Event"
5. A QR code will be automatically generated

### 3. Upload Photos

1. Click on the event from dashboard
2. Click "Upload Photos"
3. Select multiple photos (supports JPG, PNG, GIF)
4. Click "Upload Photos"
5. Photos will be saved to the event

### 4. Process Photos

1. After uploading, click "Process Unprocessed Photos"
2. Review the photos to be processed
3. Click "Start Processing"
4. System will:
   - Detect faces using MTCNN
   - Generate FaceNet embeddings (128D)
   - Generate ArcFace embeddings (512D)
   - Store embeddings in database

**Note:** Processing time depends on:
- Number of photos
- Number of faces per photo
- System specifications

### 5. Monitor Events

From the dashboard you can:
- View all events
- See photo counts
- Check processing status
- Access QR codes
- Delete events if needed

### 6. View Performance Metrics

1. Click "View Performance Metrics"
2. Review:
   - Precision scores
   - Recall scores
   - F1-scores
   - False positives/negatives
   - Processing times
   - Model comparisons

## User Workflow

### 1. Select Event

1. Navigate to http://localhost:5000
2. Click "Find My Photos"
3. Browse available events
4. Click on the event you attended

### 2. Capture Selfie

**Option A: Webcam Capture**
1. Allow browser to access webcam
2. Position your face in the frame
3. Click "Capture Photo"
4. If not satisfied, click "Retake"

**Option B: Upload Selfie**
1. Click the upload area or drag and drop
2. Select a clear photo of your face
3. Preview will be shown

### 3. Select AI Model

Choose between:
- **FaceNet:** Faster, good for most cases (128D embeddings)
- **ArcFace:** More accurate, slightly slower (512D embeddings)

### 4. Search Photos

1. Click "Search Photos"
2. Wait for AI processing (10-30 seconds)
3. Results will show:
   - Number of matches found
   - Similarity percentage for each photo
   - Preview of matched photos

### 5. Download Photos

- Click download icon on individual photos
- All photos are available in high resolution

## Model Comparison

### FaceNet

**Advantages:**
- Fast processing
- Lower memory usage
- Good for real-time applications
- 128-dimensional embeddings

**When to use:**
- Large events with many photos
- Quick searches needed
- Limited hardware resources

### ArcFace

**Advantages:**
- Higher accuracy
- Better with difficult lighting
- More robust to angles
- 512-dimensional embeddings

**When to use:**
- Accuracy is critical
- Smaller photo sets
- Professional events
- High-quality photos available

### Performance Comparison

| Metric | FaceNet | ArcFace |
|--------|---------|---------|
| Speed | ⚡⚡⚡ Fast | ⚡⚡ Moderate |
| Accuracy | ✓✓ Good | ✓✓✓ Excellent |
| Memory | 🔹 Low | 🔹🔹 Moderate |
| Embedding Size | 128D | 512D |

## Performance Evaluation

### Running Evaluation Tests

1. Prepare test dataset:
```
tests/test_dataset/
  person1/
    photo1.jpg
    photo2.jpg
  person2/
    photo1.jpg
    photo2.jpg
```

2. Run evaluation:
```bash
python tests/evaluate_models.py
```

3. Review metrics:
- Precision: Percentage of correct matches
- Recall: Percentage of all photos found
- F1-Score: Balance between precision and recall
- False Positives: Wrong matches
- False Negatives: Missed photos

### Understanding Metrics

**Precision:**
```
Precision = True Positives / (True Positives + False Positives)
```
- High precision = Few wrong matches
- Critical for user experience

**Recall:**
```
Recall = True Positives / (True Positives + False Negatives)
```
- High recall = Few missed photos
- Critical for completeness

**F1-Score:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
- Balanced metric
- Higher is better

## Best Practices

### For Admins

1. **Photo Quality:**
   - Use high-resolution photos (1920x1080 or higher)
   - Ensure good lighting
   - Avoid blurry or motion-blurred images

2. **Face Detection:**
   - Photos with clear, frontal faces work best
   - Group photos are supported
   - Minimum face size: 50x50 pixels

3. **Processing:**
   - Process photos in batches of 50-100
   - Process during off-peak hours
   - Monitor system resources

4. **Event Management:**
   - Use descriptive event names
   - Include location for user reference
   - Generate QR codes for easy access
   - Archive old events regularly

### For Users

1. **Selfie Capture:**
   - Face the camera directly
   - Ensure good lighting
   - Remove sunglasses and hats
   - Use neutral expression (similar to event photos)

2. **Photo Upload:**
   - Use recent photos
   - Clear, frontal face photos work best
   - Avoid heavily filtered images

3. **Model Selection:**
   - Try FaceNet first (faster)
   - Use ArcFace if FaceNet results are insufficient
   - Compare both models for best results

4. **Search Tips:**
   - If no results, try a different photo
   - Check if you selected the correct event
   - Try both AI models
   - Ensure the event photos are processed

### Photo Guidelines

**✓ Good Photos:**
- Clear, well-lit faces
- Frontal or slight angle
- Minimal accessories
- High resolution
- Natural expressions

**✗ Avoid:**
- Heavy filters or effects
- Extreme angles
- Poor lighting (too dark/bright)
- Blurry or pixelated
- Sunglasses or face coverings

## Troubleshooting

### No Faces Detected

**Causes:**
- Face too small in photo
- Poor lighting
- Extreme angle
- Face obstructed

**Solutions:**
- Use higher resolution
- Improve lighting
- Ensure frontal view
- Remove obstructions

### No Matching Photos Found

**Causes:**
- Different appearance in query photo
- Event photos not processed
- Wrong event selected
- Threshold too strict

**Solutions:**
- Try different selfie
- Verify event is processed
- Try alternate AI model
- Contact admin to reprocess

### Slow Processing

**Causes:**
- Large number of photos
- Limited system resources
- High-resolution images

**Solutions:**
- Process in smaller batches
- Close other applications
- Upgrade hardware
- Use FaceNet instead of ArcFace

## Advanced Features

### QR Code Sharing

1. Admins can download event QR codes
2. Print and display at event venue
3. Attendees scan to access directly
4. URL opens event selection page

### Batch Operations

For processing multiple events:
```python
# Custom script
from app import create_app, db
from app.models import Event, Photo

app = create_app()
with app.app_context():
    events = Event.query.filter_by(processed=False).all()
    for event in events:
        # Process photos
        pass
```

### API Access (Future)

REST API endpoints can be added for:
- Mobile app integration
- Third-party integrations
- Automated workflows

## FAQ

**Q: How many faces can be detected in one photo?**
A: Unlimited. The system handles group photos with multiple faces.

**Q: How accurate is face matching?**
A: 85-95% accuracy depending on photo quality and model used.

**Q: Can I use photos with makeup or costumes?**
A: Yes, but accuracy may vary. Use a query photo similar to event photos.

**Q: Is my data private?**
A: Yes. Photos are stored locally and only accessible through the system.

**Q: Can I delete my photos?**
A: Contact the event admin. Admins can delete entire events.

**Q: What happens to old events?**
A: Admins can archive or delete old events to free up space.

**Q: Can I access events offline?**
A: No. Internet connection required for face matching.

## Support

For issues:
1. Check INSTALLATION.md
2. Review error messages
3. Check system logs
4. Contact system administrator

For feature requests:
1. Document your use case
2. Provide examples
3. Submit to development team
