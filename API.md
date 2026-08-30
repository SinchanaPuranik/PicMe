# PICME API Documentation

## Overview

PICME provides REST API endpoints for integration with external applications.

## Authentication

All admin API endpoints require authentication. User endpoints are public.

## Base URL

```
http://localhost:5000
```

## Endpoints

### Events

#### List All Events
```http
GET /user/events
```

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "name": "College Fest 2026",
      "description": "Annual college festival",
      "event_date": "2026-08-15",
      "location": "Main Campus",
      "is_active": true,
      "photos_count": 150
    }
  ]
}
```

#### Get Event Details
```http
GET /admin/events/<event_id>
```

**Response:**
```json
{
  "id": 1,
  "name": "College Fest 2026",
  "description": "Annual college festival",
  "event_date": "2026-08-15",
  "location": "Main Campus",
  "qr_code_url": "/static/uploads/events/event_1_qr.png",
  "photos": [
    {
      "id": 1,
      "filename": "photo1.jpg",
      "num_faces": 3,
      "processed": true
    }
  ]
}
```

### Photo Search

#### Search Photos by Face
```http
POST /user/events/<event_id>/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "model_type": "facenet"
}
```

**Response:**
```json
{
  "success": true,
  "model": "facenet",
  "matches": 12,
  "photos": [
    {
      "id": 1,
      "filename": "photo1.jpg",
      "url": "/static/uploads/events/1/photo1.jpg",
      "similarity": 0.92,
      "uploaded_at": "2026-08-15 10:30:00"
    }
  ]
}
```

### Admin Endpoints

#### Create Event
```http
POST /admin/events/create
Content-Type: application/x-www-form-urlencoded
Authorization: Required
```

**Request Body:**
```
name=College+Fest+2026
description=Annual+festival
event_date=2026-08-15
location=Main+Campus
```

#### Upload Photos
```http
POST /admin/events/<event_id>/upload
Content-Type: multipart/form-data
Authorization: Required
```

**Request Body:**
```
photos: [file1, file2, ...]
```

#### Process Photos
```http
POST /admin/events/<event_id>/process
Authorization: Required
```

**Response:**
```json
{
  "processed": 50,
  "faces_detected": 123,
  "message": "Processing completed"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "No face detected in image"
}
```

### 404 Not Found
```json
{
  "error": "Event not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to generate face embedding"
}
```

## Rate Limiting

- Public endpoints: 100 requests/hour
- Admin endpoints: 1000 requests/hour

## Webhooks

Configure webhooks for event notifications:

```json
{
  "event": "photo.processed",
  "data": {
    "event_id": 1,
    "photo_id": 123,
    "faces_detected": 3
  }
}
```

## SDK Examples

### Python
```python
import requests

# Search photos
response = requests.post(
    'http://localhost:5000/user/events/1/search',
    json={
        'image': image_base64,
        'model_type': 'facenet'
    }
)
results = response.json()
```

### JavaScript
```javascript
// Search photos
fetch('http://localhost:5000/user/events/1/search', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: imageBase64,
        model_type: 'facenet'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Notes

- All dates are in ISO 8601 format
- Image data should be base64 encoded
- Maximum file size: 16MB
- Supported formats: JPG, PNG, GIF
