# Quick Start: Using Face Detectors in PICME

## 🚀 Getting Started in 3 Steps

### Step 1: Access Admin Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```
Login with admin credentials:
- **Username:** admin
- **Password:** admin123

---

### Step 2: Test Available Detectors
1. Click **"Test Face Detectors"** button on dashboard
2. View which detectors are available:
   - ✅ **MTCNN** - Ready (Default, Balanced)
   - ✅ **Haar Cascade** - Ready (Fast)
   - ❌ **DNN** - Needs Setup (Accurate)
   - ✅ **RetinaFace** - Ready (Most Accurate)

---

### Step 3: Process Photos with Your Chosen Detector
1. Navigate to an **Event**
2. Click **"Process Photos"**
3. Select your detector from dropdown
4. Adjust confidence (0.5-0.95)
5. Click **"Start Processing"**

---

## 🎯 Quick Recommendations

### Need Speed? ⚡
**Use: Haar Cascade**
```
Detector: Haar Cascade
Confidence: 0.9
Processing Time: ~0.5s per image
```

### Need Accuracy? 🎯
**Use: RetinaFace**
```
Detector: RetinaFace
Confidence: 0.5-0.7
Processing Time: ~5-8s per image
```

### Need Balance? ⚖️
**Use: MTCNN (Default)**
```
Detector: MTCNN
Confidence: 0.9
Processing Time: ~2-3s per image
```

---

## 📊 Detector Cheat Sheet

| When to Use | Detector | Confidence |
|-------------|----------|------------|
| 🏃 Quick demo/testing | Haar Cascade | 0.9 |
| 📸 General event photos | MTCNN | 0.85-0.9 |
| 🎭 Group photos, varied poses | DNN | 0.6-0.8 |
| 🔬 Critical accuracy needed | RetinaFace | 0.5-0.7 |
| 🌙 Poor lighting | RetinaFace | 0.5 |
| ☀️ Good lighting | Haar/MTCNN | 0.9 |
| 👥 Large groups | MTCNN/DNN | 0.7-0.85 |
| 👤 Individual portraits | Any | 0.9 |

---

## 🔧 Common Settings

### High Quality Event (Wedding, Corporate)
```yaml
Detector: RetinaFace
Confidence: 0.6
Why: Maximum accuracy for important photos
Trade-off: Slower processing (worth it)
```

### Quick Social Event (Party, Casual)
```yaml
Detector: MTCNN
Confidence: 0.85
Why: Fast enough, good accuracy
Trade-off: Balanced approach
```

### Large Volume Processing (Festival, Conference)
```yaml
Detector: Haar Cascade
Confidence: 0.9
Why: Process hundreds of photos quickly
Trade-off: May miss some faces
```

### Mixed Quality Photos (User Uploads)
```yaml
Detector: MTCNN
Confidence: 0.75
Why: Handles various qualities well
Trade-off: More false positives
```

---

## ⚠️ Troubleshooting

### No Faces Detected?
1. **Lower confidence threshold** (try 0.5-0.7)
2. **Try different detector** (RetinaFace is most robust)
3. **Check image quality** (resolution, lighting)
4. **Verify faces are visible** (not too small/far)

### Too Many False Positives?
1. **Increase confidence** (try 0.9-0.95)
2. **Switch to MTCNN or RetinaFace** (more accurate)
3. **Check photo quality** (better photos = better results)

### Processing Too Slow?
1. **Use Haar Cascade** (fastest option)
2. **Lower image resolution** (resize before upload)
3. **Process in smaller batches**
4. **Consider DNN** (good balance)

### DNN Not Available?
```bash
# Download model files (see FACE_DETECTORS.md)
mkdir models
cd models
# Download deploy.prototxt and .caffemodel
# Restart server
```

---

## 🎓 Learning Path

### Beginner
1. ✅ Start with **MTCNN** (default)
2. ✅ Use confidence **0.9**
3. ✅ Process small batch first
4. ✅ Check results

### Intermediate
1. ✅ Test **all detectors** on same photos
2. ✅ Compare results on test page
3. ✅ Adjust confidence based on needs
4. ✅ Choose best for your use case

### Advanced
1. ✅ Benchmark performance
2. ✅ Use API endpoints
3. ✅ Set up DNN detector
4. ✅ Optimize for your hardware

---

## 💡 Pro Tips

### Tip 1: Test Before Bulk Processing
Always test on 5-10 photos first with different detectors to see which works best for your photo set.

### Tip 2: Confidence Sweet Spots
- **High quality photos:** 0.9-0.95
- **Mixed quality:** 0.7-0.85
- **Poor quality:** 0.5-0.7
- **When in doubt:** 0.8

### Tip 3: Combine Detectors
For critical events, use multiple detectors and combine results for maximum coverage.

### Tip 4: Processing Time
- **1-50 photos:** Any detector is fine
- **50-200 photos:** MTCNN or Haar
- **200+ photos:** Haar Cascade
- **Accuracy critical:** Always RetinaFace

### Tip 5: Landmarks Matter
If you need face alignment (for better matching), use **MTCNN** or **RetinaFace** (they provide landmarks).

---

## 📱 Quick Reference Card

```
╔══════════════════════════════════════════╗
║       PICME Detector Quick Guide         ║
╠══════════════════════════════════════════╣
║                                          ║
║  SPEED PRIORITY:                         ║
║  ▸ Haar Cascade (conf: 0.9)             ║
║                                          ║
║  ACCURACY PRIORITY:                      ║
║  ▸ RetinaFace (conf: 0.5-0.7)           ║
║                                          ║
║  BALANCED:                               ║
║  ▸ MTCNN (conf: 0.85-0.9)               ║
║                                          ║
║  AVAILABLE EVERYWHERE:                   ║
║  ▸ MTCNN, Haar, RetinaFace              ║
║                                          ║
║  NEEDS SETUP:                            ║
║  ▸ DNN (download models)                ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## 🎬 Example Workflow

### Processing Event Photos

**Step-by-Step:**

1. **Upload Photos** (Admin → Event → Upload Photos)
2. **Test Detectors** (Admin → Test Face Detectors)
3. **View Benchmark** (See which detector finds most faces)
4. **Choose Detector** (Based on results)
5. **Process Photos** (Event → Process Photos)
6. **Select Settings:**
   - Detector: [Your choice]
   - Confidence: [Based on test]
7. **Start Processing**
8. **Verify Results** (Check detected faces count)
9. **Adjust if Needed** (Re-process with different settings)

---

## 📞 Need Help?

- **Full Documentation:** See `FACE_DETECTORS.md`
- **Technical Details:** See `DETECTOR_FEATURES_SUMMARY.md`
- **Project Guide:** See `README.md`

---

## ✅ Checklist

Before processing important event photos:

- [ ] Tested on sample photos
- [ ] Compared detector results
- [ ] Chose appropriate detector
- [ ] Set confidence threshold
- [ ] Backed up original photos
- [ ] Started with small batch
- [ ] Verified results
- [ ] Adjusted if needed
- [ ] Processed full batch

---

**Happy Face Detecting! 📸✨**

*PICME - AI-Powered Photo Retrieval System*
