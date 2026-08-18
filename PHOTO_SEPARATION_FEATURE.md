# PICME Photo Separation Feature

## ✨ **Feature Overview**

PICME now automatically **separates search results** into two distinct sections:

1. 🧍 **Individual Photos** - Photos with only you (1 face detected)
2. 👥 **Group Photos** - Photos with you and others (2+ faces detected)

---

## 🎯 **How It Works**

### **During Photo Upload & Processing:**

When admins upload photos, the system:
1. Detects all faces in each photo using MTCNN
2. Counts the number of faces
3. Stores the `num_faces` count with each photo

### **During Face Search:**

When users search for their photos:
1. System finds all matching photos
2. Automatically categorizes them:
   - `num_faces == 1` → **Individual Photos**
   - `num_faces >= 2` → **Group Photos**
3. Displays in separate, color-coded sections

---

## 📊 **Visual Design**

### **Summary Cards (Top):**
```
┌─────────────────────┐  ┌─────────────────────┐
│   👤  Individual    │  │   👥  Group         │
│        Photos       │  │       Photos        │
│         12          │  │         8           │
└─────────────────────┘  └─────────────────────┘
    (Blue Border)            (Green Border)
```

### **Individual Photos Section:**
```
╔════════════════════════════════════════╗
║ 👤 Individual Photos (12)              ║ ← Blue Header
╠════════════════════════════════════════╣
║                                        ║
║  [Photo 1]  [Photo 2]  [Photo 3]      ║
║   98% match  95% match  92% match     ║
║   [Download] [Download] [Download]    ║
║                                        ║
╚════════════════════════════════════════╝
```

### **Group Photos Section:**
```
╔════════════════════════════════════════╗
║ 👥 Group Photos (8)                    ║ ← Green Header
╠════════════════════════════════════════╣
║                                        ║
║  [Photo 1]  [Photo 2]  [Photo 3]      ║
║  (3 people) (5 people) (2 people)     ║
║   96% match  94% match  91% match     ║
║   [Download] [Download] [Download]    ║
║                                        ║
╚════════════════════════════════════════╝
```

---

## 🎨 **Color Coding**

| Section | Color | Badge | Icon |
|---------|-------|-------|------|
| **Individual Photos** | 🔵 Blue (Primary) | Blue badge | 👤 fa-user |
| **Group Photos** | 🟢 Green (Success) | Green badge | 👥 fa-users |

---

## 💻 **Technical Implementation**

### **Backend (app/routes/user.py):**

```python
# Separate photos by face count
individual_photos = []  # num_faces == 1
group_photos = []       # num_faces >= 2

for photo, similarity in matching_photos:
    photo_data = {
        'id': photo.id,
        'filename': photo.filename,
        'url': url_for('static', filename=f'uploads/events/{event_id}/{photo.filename}'),
        'similarity': float(similarity),
        'num_faces': photo.num_faces,  # ← Key field
        'uploaded_at': photo.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if photo.num_faces == 1:
        individual_photos.append(photo_data)
    else:
        group_photos.append(photo_data)

return jsonify({
    'success': True,
    'individual_photos': individual_photos,
    'group_photos': group_photos,
    'total_individual': len(individual_photos),
    'total_group': len(group_photos)
})
```

### **Frontend (app/templates/user/capture_selfie.html):**

```javascript
function displayResults(data) {
    // Update count displays
    document.getElementById('individualCount').textContent = data.total_individual;
    document.getElementById('groupCount').textContent = data.total_group;
    
    // Display individual photos in blue section
    if (data.individual_photos.length > 0) {
        individualSection.style.display = 'block';
        data.individual_photos.forEach(photo => {
            // Create blue-bordered cards with "Solo Photo" header
        });
    }
    
    // Display group photos in green section
    if (data.group_photos.length > 0) {
        groupSection.style.display = 'block';
        data.group_photos.forEach(photo => {
            // Create green-bordered cards with "Group Photo (X people)" header
        });
    }
}
```

---

## 📋 **User Experience**

### **Step-by-Step Flow:**

1. **User captures/uploads selfie**
2. **Clicks "Search Photos"**
3. **System processes and displays:**
   - Summary cards showing counts
   - Individual photos section (if any)
   - Group photos section (if any)

### **Example Results:**

```
✓ Found 20 Photos

┌─────────────────┐  ┌─────────────────┐
│  👤  12         │  │  👥  8          │
│ Individual      │  │ Group Photos    │
└─────────────────┘  └─────────────────┘

═══════════════════════════════════════
👤 Individual Photos (12)
───────────────────────────────────────
[Shows 12 photos where user is alone]

═══════════════════════════════════════
👥 Group Photos (8)
───────────────────────────────────────
[Shows 8 photos with multiple people]
```

---

## 🎯 **Benefits**

### **For Users:**
1. ✅ **Easy Navigation** - Find solo shots vs group shots quickly
2. ✅ **Clear Organization** - No need to browse through all photos
3. ✅ **Quick Download** - Download all individual or all group photos
4. ✅ **Better UX** - Understand results at a glance

### **For Admins:**
1. ✅ **Automatic** - No manual categorization needed
2. ✅ **Accurate** - Based on actual face detection
3. ✅ **Informative** - Shows number of people in each group photo

---

## 📊 **Data Structure**

### **Response Format:**

```json
{
    "success": true,
    "model": "facenet",
    "matches": 20,
    "individual_photos": [
        {
            "id": 1,
            "filename": "photo1.jpg",
            "url": "/static/uploads/events/1/photo1.jpg",
            "similarity": 0.95,
            "num_faces": 1,
            "uploaded_at": "2026-08-13 10:30:00"
        }
    ],
    "group_photos": [
        {
            "id": 2,
            "filename": "photo2.jpg",
            "url": "/static/uploads/events/1/photo2.jpg",
            "similarity": 0.92,
            "num_faces": 3,
            "uploaded_at": "2026-08-13 10:35:00"
        }
    ],
    "total_individual": 12,
    "total_group": 8
}
```

---

## 🔧 **Customization Options**

### **Change Category Threshold:**

Currently: 1 face = individual, 2+ faces = group

To change (e.g., 1-2 faces = individual, 3+ = group):

```python
# In app/routes/user.py
if photo.num_faces <= 2:  # Changed from == 1
    individual_photos.append(photo_data)
else:
    group_photos.append(photo_data)
```

### **Add More Categories:**

You can add additional categories like:
- **Solo** (1 face)
- **Duo** (2 faces)  
- **Small Group** (3-5 faces)
- **Large Group** (6+ faces)

### **Change Colors:**

Edit in `capture_selfie.html`:
- Individual: Change `border-primary` and `bg-primary` (blue)
- Group: Change `border-success` and `bg-success` (green)

---

## 📈 **Statistics Display**

### **Summary Cards Show:**
```
Individual Photos Card:
- Icon: 👤 (single person)
- Color: Blue
- Number: Count of solo photos

Group Photos Card:
- Icon: 👥 (multiple people)  
- Color: Green
- Number: Count of group photos
```

### **Photo Cards Show:**
```
Individual Photo:
- Header: "👤 Solo Photo"
- Border: Blue
- Button: Blue download button

Group Photo:
- Header: "👥 Group Photo (X people)"
- Border: Green
- Button: Green download button
- Shows actual face count
```

---

## ✨ **Special Cases**

### **No Results:**
```
Shows message:
"No matching photos found
Try with a different photo or check another event"
```

### **Only Individual Photos:**
```
- Individual section shown
- Group section hidden
- Group count shows 0
```

### **Only Group Photos:**
```
- Group section shown
- Individual section hidden
- Individual count shows 0
```

### **Mixed Results:**
```
- Both sections shown
- Counts reflect actual numbers
- Sections appear in order:
  1. Individual Photos (blue)
  2. Group Photos (green)
```

---

## 🎨 **Visual Examples**

### **Card Styling:**

**Individual Photo Card:**
```html
┌────────────────────────┐
│ 👤 Solo Photo         │ ← Blue header
├────────────────────────┤
│                        │
│   [Photo Image]        │
│                        │
├────────────────────────┤
│ 🟢 95% match [📥]     │ ← Footer with badge
└────────────────────────┘
```

**Group Photo Card:**
```html
┌────────────────────────┐
│ 👥 Group (3 people)   │ ← Green header
├────────────────────────┤
│                        │
│   [Photo Image]        │
│                        │
├────────────────────────┤
│ 🟢 92% match [📥]     │ ← Footer with badge
└────────────────────────┘
```

---

## 🚀 **Performance**

- ✅ No additional processing time
- ✅ Categorization happens instantly
- ✅ No extra database queries
- ✅ Uses existing `num_faces` field

---

## 🔍 **Testing**

### **Test Scenarios:**

1. **Upload mix of individual and group photos**
   - Expected: Both sections appear with correct counts

2. **Upload only individual photos**
   - Expected: Only individual section shown

3. **Upload only group photos**
   - Expected: Only group section shown

4. **Search with no matches**
   - Expected: "No results" message shown

---

## 📝 **Summary**

The photo separation feature:
- ✅ **Automatically categorizes** search results
- ✅ **Uses color coding** for easy identification
- ✅ **Shows face counts** on group photos
- ✅ **Improves user experience** significantly
- ✅ **Requires no extra work** from admins
- ✅ **Already implemented** and ready to use!

---

## 🎉 **Try It Now!**

1. Login as admin and upload photos
2. Process photos (face detection)
3. Login as user
4. Capture selfie
5. Search photos
6. See results separated into individual and group sections!

---

**Your PICME system now intelligently organizes search results!** 📸✨
