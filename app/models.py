from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(256))
    qr_code_path = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    photos = db.relationship('Photo', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def reset_event_embeddings(self):
        """Remove stale embeddings and mark all event photos for reprocessing.

        This ensures each scan rebuilds the event's embedding set from the current
        uploaded photos instead of accumulating old entries.
        """
        photo_ids = [photo.id for photo in self.photos.all()]
        if photo_ids:
            FaceEmbedding.query.filter(FaceEmbedding.photo_id.in_(photo_ids)).delete(
                synchronize_session=False
            )
        Photo.query.filter_by(event_id=self.id).update(
            {Photo.processed: False, Photo.num_faces: 0},
            synchronize_session=False,
        )
    
    def __repr__(self):
        return f'<Event {self.name}>'


class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    num_faces = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    # Relationships
    embeddings = db.relationship('FaceEmbedding', backref='photo', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Photo {self.filename}>'


class FaceEmbedding(db.Model):
    __tablename__ = 'face_embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=False)
    model_type = db.Column(db.String(32), nullable=False)  # 'facenet' or 'arcface'
    embedding_json = db.Column(db.Text, nullable=False)
    face_box = db.Column(db.String(256))  # JSON string with bbox coordinates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_embedding(self, embedding_array):
        """Convert numpy array to JSON string"""
        self.embedding_json = json.dumps(embedding_array.tolist())
    
    def get_embedding(self):
        """Convert JSON string back to numpy array"""
        import numpy as np
        return np.array(json.loads(self.embedding_json))
    
    def set_face_box(self, box):
        """Store face bounding box coordinates"""
        self.face_box = json.dumps(box)
    
    def get_face_box(self):
        """Retrieve face bounding box coordinates"""
        return json.loads(self.face_box) if self.face_box else None
    
    def __repr__(self):
        return f'<FaceEmbedding {self.model_type} for Photo {self.photo_id}>'


class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(32), nullable=False)
    metric_type = db.Column(db.String(64), nullable=False)  # precision, recall, f1, etc.
    value = db.Column(db.Float, nullable=False)
    test_set_size = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Metric {self.model_type} {self.metric_type}: {self.value}>'


class SearchRetrieval(db.Model):
    """Tracks each user search and evaluates model performance on retrieved photos"""
    __tablename__ = 'search_retrievals'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    model_type = db.Column(db.String(32), nullable=False)  # 'facenet' or 'arcface'
    num_matches = db.Column(db.Integer, default=0)  # Total photos matched
    num_individual = db.Column(db.Integer, default=0)  # Individual photos (1 face)
    num_group = db.Column(db.Integer, default=0)  # Group photos (2+ faces)
    
    # Performance metrics for this search
    avg_similarity = db.Column(db.Float)  # Average similarity score
    max_similarity = db.Column(db.Float)  # Highest similarity score
    min_similarity = db.Column(db.Float)  # Lowest similarity score
    median_similarity = db.Column(db.Float)  # Median similarity score
    std_similarity = db.Column(db.Float)  # Standard deviation of similarity
    
    # Processing metrics
    processing_time_ms = db.Column(db.Float)  # Time to process search
    face_detection_time_ms = db.Column(db.Float)  # Time for face detection
    embedding_generation_time_ms = db.Column(db.Float)  # Time to generate embedding
    matching_time_ms = db.Column(db.Float)  # Time for matching
    
    # Search metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    similarity_scores_json = db.Column(db.Text)  # JSON array of all similarity scores
    notes = db.Column(db.Text)
    
    def set_similarity_scores(self, scores_list):
        """Convert list to JSON string"""
        self.similarity_scores_json = json.dumps(scores_list)
    
    def get_similarity_scores(self):
        """Convert JSON string back to list"""
        if self.similarity_scores_json:
            return json.loads(self.similarity_scores_json)
        return []
    
    def __repr__(self):
        return f'<SearchRetrieval {self.id}: {self.model_type} - {self.num_matches} matches>'
