# PICME Upload Limits & Configuration Guide

## 📊 Current Upload Settings

### **Per Photo Limits:**
```
Maximum File Size: 16 MB per photo
Allowed Formats: JPG, JPEG, PNG, GIF
```

### **Number of Photos:**
```
Per Upload: UNLIMITED (can select multiple files)
Per Event: UNLIMITED
Total System: Limited only by disk space
```

### **Recommended Specifications:**
```
Photo Resolution: 1920x1080 or higher
Minimum Face Size: 50x50 pixels
Optimal Quality: High-quality JPEG (85-95% quality)
```

---

## 🔢 Practical Limits

### **Upload Session:**
- ✅ You can select **unlimited photos** in one upload
- ✅ Browser can handle 50-200 photos at once
- ✅ For better performance, upload in batches of **50-100 photos**

### **Event Capacity:**
```
Small Event:   50-100 photos   ✓ Excellent performance
Medium Event:  100-500 photos  ✓ Good performance
Large Event:   500-1000 photos ✓ May need batch processing
Very Large:    1000+ photos    ⚠️ Recommend batch uploads
```

### **Storage Calculations:**

| Photo Quality | Size | 100 Photos | 500 Photos | 1000 Photos |
|--------------|------|------------|------------|-------------|
| Low (1-2 MB) | 1.5 MB | ~150 MB | ~750 MB | ~1.5 GB |
| Medium (3-5 MB) | 4 MB | ~400 MB | ~2 GB | ~4 GB |
| High (8-15 MB) | 12 MB | ~1.2 GB | ~6 GB | ~12 GB |

---

## ⚙️ How to Change Upload Limits

### **Increase File Size Limit:**

Edit `config.py` and change:

```python
# Current: 16 MB
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# For 32 MB:
MAX_CONTENT_LENGTH = 32 * 1024 * 1024

# For 50 MB:
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

# For 100 MB:
MAX_CONTENT_LENGTH = 100 * 1024 * 1024
```

### **Add More File Formats:**

```python
# Current formats
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Add more formats:
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}
```

### **Enable Batch Processing:**

For very large uploads, the system automatically processes photos in batches during face detection.

---

## 🚀 Performance Tips

### **For Best Performance:**

1. **Photo Quality:**
   - Use high-resolution photos (1920x1080+)
   - Compress to reasonable size (2-5 MB)
   - Ensure good lighting

2. **Upload Strategy:**
   ```
   Recommended batch sizes:
   - Good PC: 50-100 photos per upload
   - Powerful PC: 100-200 photos per upload
   - Any PC: Process 50-100 at a time
   ```

3. **Processing Time:**
   ```
   Estimated time per photo:
   - Face Detection: 1-3 seconds
   - FaceNet Embedding: 0.5-1 second
   - ArcFace Embedding: 1-2 seconds
   - Total per photo: 3-6 seconds
   
   For 100 photos: 5-10 minutes
   For 500 photos: 25-50 minutes
   ```

---

## 💾 Disk Space Requirements

### **Database:**
```
Photo metadata: ~1 KB per photo
Face embeddings: 
  - FaceNet: ~512 bytes per face
  - ArcFace: ~2 KB per face
  
For 1000 photos with avg 2 faces each:
  Metadata: ~1 MB
  Embeddings: ~5 MB
  Total DB: ~6 MB
```

### **Photo Storage:**
```
Original photos stored as-is
No compression applied
Space = Number of photos × Average photo size
```

### **Total System Requirements:**

| Event Size | Photos | Storage Needed | RAM Recommended | Processing Time |
|------------|--------|----------------|-----------------|-----------------|
| Small | 50 | ~500 MB | 4 GB | ~5 min |
| Medium | 200 | ~1.5 GB | 8 GB | ~20 min |
| Large | 500 | ~3-5 GB | 16 GB | ~50 min |
| Very Large | 1000+ | ~8-15 GB | 16+ GB | ~2 hours |

---

## 📈 Scalability Options

### **For Large Events:**

1. **Batch Upload & Processing:**
   ```
   - Upload 100 photos
   - Process them
   - Upload next 100
   - Repeat
   ```

2. **Optimize Photos Before Upload:**
   ```bash
   # Use tools to resize/compress:
   - ImageMagick
   - Photoshop Batch
   - Online compressors
   ```

3. **Background Processing (Advanced):**
   - Can add Celery for async processing
   - Process photos in background
   - Users get notification when done

4. **Use Production Database:**
   - Switch from SQLite to PostgreSQL
   - Better performance for large datasets
   - See `INSTALLATION.md` for setup

---

## 🛠️ Configuration Examples

### **For Small Events (50-100 photos):**
```python
# config.py - Current settings work perfectly
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### **For Medium Events (100-500 photos):**
```python
# config.py - Increase file size
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
```

### **For Large Events (500-1000 photos):**
```python
# config.py - Higher limits
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# Also consider:
# - Use PostgreSQL instead of SQLite
# - More RAM (16GB recommended)
# - SSD storage for better I/O
```

### **For Very Large Events (1000+ photos):**
```python
# config.py - Maximum settings
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

# Required:
# - PostgreSQL database
# - 16+ GB RAM
# - SSD storage
# - Consider batch processing
# - Possibly add Redis caching
```

---

## 📝 How to Apply Changes

### **Step 1: Edit config.py**
```bash
# Open config.py
# Change MAX_CONTENT_LENGTH value
# Save file
```

### **Step 2: Restart Server**
```bash
# Stop server (Ctrl+C in terminal)
# Start again:
python run.py
```

### **Step 3: Clear Browser Cache**
```
Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
```

---

## ⚠️ Important Notes

### **Limitations:**

1. **Browser Limits:**
   - Modern browsers handle large files well
   - Uploading 100+ photos at once may freeze UI
   - Use batch uploads for better experience

2. **Memory Limits:**
   - Processing all photos uses RAM
   - Face detection is memory-intensive
   - 8GB RAM recommended minimum

3. **Processing Time:**
   - Each photo takes 3-6 seconds to process
   - Large batches take significant time
   - Progress shown in UI

4. **SQLite Limitations:**
   - Current setup uses SQLite
   - Great for small-medium events
   - For 500+ photos, consider PostgreSQL

---

## 🎯 Recommendations by Event Size

### **50-100 Photos:**
✅ Current settings perfect  
✅ Upload all at once  
✅ Process immediately  
⏱️ Total time: ~5-10 minutes  

### **100-500 Photos:**
✅ Current settings work  
⚠️ Consider uploading in 2-3 batches  
✅ Process in batches of 100  
⏱️ Total time: ~30-60 minutes  

### **500-1000 Photos:**
⚠️ Increase MAX_CONTENT_LENGTH to 32-50MB  
⚠️ Upload in batches of 100-150  
⚠️ Process in batches  
⚠️ Consider PostgreSQL  
⏱️ Total time: 1-2 hours  

### **1000+ Photos:**
🔴 Increase MAX_CONTENT_LENGTH to 50-100MB  
🔴 Mandatory batch uploads (100-200 per batch)  
🔴 Use PostgreSQL  
🔴 16+ GB RAM required  
🔴 Consider background processing  
⏱️ Total time: 2-4 hours  

---

## 📊 Quick Reference Table

| Metric | Current Value | Can Change To |
|--------|--------------|---------------|
| Max File Size | 16 MB | Up to 100 MB |
| Photos Per Upload | Unlimited | Unlimited |
| Photos Per Event | Unlimited | Unlimited |
| Batch Size (Recommended) | 50-100 | 50-200 |
| Allowed Formats | JPG, PNG, GIF | + WebP, BMP, TIFF |
| Processing Speed | 3-6 sec/photo | Depends on hardware |

---

## 🔍 Monitoring Upload Progress

The system provides:
- ✅ Upload progress indicator
- ✅ Processing status
- ✅ Face detection count
- ✅ Completion notification

---

## 💡 Best Practices

1. **Pre-Upload:**
   - Check photo quality
   - Ensure faces are visible
   - Remove blurry photos
   - Organize by event

2. **During Upload:**
   - Upload in reasonable batches
   - Wait for processing to complete
   - Monitor system resources

3. **After Upload:**
   - Verify face detection count
   - Test face matching
   - Review results

---

## 🆘 Troubleshooting

### **"File too large" error:**
→ Increase `MAX_CONTENT_LENGTH` in config.py

### **Browser freezes during upload:**
→ Upload smaller batches (50-100 photos)

### **Processing takes too long:**
→ Process in smaller batches
→ Check system RAM usage
→ Consider upgrading hardware

### **Out of memory error:**
→ Reduce batch size
→ Close other applications
→ Add more RAM

---

## 📞 Summary

**Current Configuration:**
- ✅ **16 MB** max file size
- ✅ **Unlimited** photos per upload
- ✅ **JPG, PNG, GIF** formats
- ✅ Suitable for events up to **500 photos**

**For Larger Events:**
- Edit `config.py` to increase limits
- Upload in batches
- Consider PostgreSQL for 500+ photos
- Ensure adequate RAM and storage

---

**Need help changing settings? Check `config.py` and restart the server!** 🚀
