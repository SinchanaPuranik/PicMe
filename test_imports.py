import sys
sys.path.insert(0, r'c:\Users\acer\MajorProject')

try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.services.facenet_service import FaceNetService
        from app.services.arcface_service import ArcFaceService
        print("✓ All services imported successfully")
        
        # Try to instantiate
        facenet = FaceNetService()
        print("✓ FaceNet service created")
        
        arcface = ArcFaceService()
        print("✓ ArcFace service created")
        
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    traceback.print_exc()
