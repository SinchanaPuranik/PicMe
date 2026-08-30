# How to Improve Detector Accuracy

## Why is Accuracy Low?

With only 2 images, low accuracy usually means:
1. **Detectors missing faces** (confidence threshold too high)
2. **Poor annotation** (bounding boxes don't match well)
3. **Small dataset** (2 images isn't enough for reliable statistics)

## Solutions

### 1. **Lower Confidence Threshold** ✅ DONE
- Changed from `0.7` to `0.3`
- This makes detectors more sensitive and detect more faces
- Re-run evaluation to see improvement

### 2. **Check Your Annotations**
Make sure your bounding boxes:
- Cover the entire face (including chin, forehead, ears)
- Are not too tight (leave some margin)
- Match what detectors typically output

**Tip:** Draw boxes slightly larger than the face itself.

### 3. **Add More Test Images**
- **Minimum recommended:** 20-30 images
- **Good dataset:** 50-100 images
- **Excellent dataset:** 200+ images

Include variety:
- Different lighting conditions
- Different angles (frontal, profile)
- Different face sizes
- Indoor/outdoor photos
- Group photos with multiple faces

### 4. **Adjust IoU Threshold**
Currently set to **0.5** (50% overlap required)

- **Lower IoU (0.3-0.4):** More lenient matching, higher accuracy
- **Higher IoU (0.6-0.7):** Stricter matching, lower accuracy

### 5. **Test Individual Detectors**

Different detectors work better in different scenarios:

| Detector | Best For | Worst For |
|----------|----------|-----------|
| **MTCNN** | Frontal faces, good lighting | Side profiles, poor light |
| **Haar Cascade** | Fast detection, simple scenes | Complex backgrounds, angles |
| **DNN** | Balanced, various conditions | Very small faces |
| **RetinaFace** | High accuracy, all conditions | Speed (slowest) |

## Quick Actions Now

### Immediate Fix (Already Done):
```
Confidence lowered: 0.7 → 0.3
```

### Run Evaluation Again:
1. Go to `/admin/metrics`
2. Click **"Run Evaluation"**
3. Check the new accuracy scores

### Expected Results:
- With confidence at 0.3, detectors will find more faces
- TP should increase (more correct detections)
- FP might increase slightly (more false alarms)
- Overall accuracy and recall should improve

## Example: Good Test Dataset

```
test_dataset/
├── photo1.jpg  (1 face, frontal, good light)
├── photo2.jpg  (2 faces, frontal, indoor)
├── photo3.jpg  (3 faces, group photo)
├── photo4.jpg  (1 face, side angle)
├── photo5.jpg  (1 face, outdoor, bright)
├── photo6.jpg  (1 face, poor lighting)
... (at least 20 total)
```

## Debugging Tips

### Check if faces are being detected:
Look at the evaluation output console logs:
- If "TP=0" for all images → confidence too high OR annotations wrong
- If "FP > 10" → too many false detections, raise confidence
- If "FN > TP" → detectors missing faces, lower confidence

### Verify your annotations:
1. Open an annotated image
2. Check if bounding boxes actually cover the faces
3. Make sure boxes aren't too small or too large

## Current Settings

After the fix:
- **IoU Threshold:** 0.5 (50% overlap required for match)
- **Confidence Threshold:** 0.3 (detectors 30% confident or higher)
- **Test Images:** 2 (recommended: 20+)

## Next Steps

1. **Re-run evaluation** with new confidence threshold
2. **Add more test images** (at least 10-20 more)
3. **Review annotations** to ensure they're accurate
4. **Compare detector performance** to see which works best for your photos

Run evaluation now and see improved results! 🚀
