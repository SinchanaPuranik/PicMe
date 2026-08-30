import os
from app import create_app, db
from app.models import User, Event, Photo, FaceEmbedding

app = create_app(os.getenv('FLASK_ENV') or 'development')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Photo': Photo,
        'FaceEmbedding': FaceEmbedding
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
