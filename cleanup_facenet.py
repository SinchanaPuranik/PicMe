"""
Clean up FaceNet embeddings - migration to ArcFace only
Run this once after updating the codebase
"""
from app import create_app, db
from app.models import FaceEmbedding

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("PICME - Clean FaceNet Embeddings")
    print("="*60)
    
    # Count FaceNet embeddings
    facenet_count = FaceEmbedding.query.filter_by(model_type='facenet').count()
    print(f"\nFound {facenet_count} FaceNet embeddings")
    
    if facenet_count > 0:
        confirm = input(f"\nDelete all {facenet_count} FaceNet embeddings? (yes/no): ")
        if confirm.lower() == 'yes':
            FaceEmbedding.query.filter_by(model_type='facenet').delete()
            db.session.commit()
            print(f"✓ Deleted {facenet_count} FaceNet embeddings")
            print("✓ System now uses ArcFace only")
        else:
            print("✗ Cancelled")
    else:
        print("✓ No FaceNet embeddings to clean up")
    
    # Show remaining embeddings
    arcface_count = FaceEmbedding.query.filter_by(model_type='arcface').count()
    print(f"\nArcFace embeddings: {arcface_count}")
    print("\n" + "="*60)
