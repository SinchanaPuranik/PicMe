import unittest
from datetime import datetime
import numpy as np

from app import create_app, db
from app.models import Event, Photo, FaceEmbedding, User


class TestEventEmbeddingReset(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        self.user = User(username='tester', email='tester@example.com', is_admin=False)
        self.user.set_password('secret')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_reset_event_embeddings_removes_old_embeddings_for_the_event_only(self):
        event1 = Event(
            name='Event 1',
            description='First event',
            event_date=datetime.utcnow(),
            location='HQ',
            creator_id=self.user.id,
        )
        event2 = Event(
            name='Event 2',
            description='Second event',
            event_date=datetime.utcnow(),
            location='Office',
            creator_id=self.user.id,
        )
        db.session.add_all([event1, event2])
        db.session.commit()

        photo1 = Photo(filename='p1.jpg', filepath='/tmp/p1.jpg', event_id=event1.id, processed=True)
        photo2 = Photo(filename='p2.jpg', filepath='/tmp/p2.jpg', event_id=event1.id, processed=True)
        photo3 = Photo(filename='p3.jpg', filepath='/tmp/p3.jpg', event_id=event2.id, processed=True)
        db.session.add_all([photo1, photo2, photo3])
        db.session.commit()

        emb1 = FaceEmbedding(photo_id=photo1.id, model_type='facenet')
        emb1.set_embedding(np.array([1.0, 2.0, 3.0]))
        emb2 = FaceEmbedding(photo_id=photo2.id, model_type='arcface')
        emb2.set_embedding(np.array([4.0, 5.0, 6.0]))
        emb3 = FaceEmbedding(photo_id=photo3.id, model_type='facenet')
        emb3.set_embedding(np.array([7.0, 8.0, 9.0]))
        db.session.add_all([emb1, emb2, emb3])
        db.session.commit()

        event1.reset_event_embeddings()
        db.session.commit()

        self.assertEqual(FaceEmbedding.query.filter_by(photo_id=photo1.id).count(), 0)
        self.assertEqual(FaceEmbedding.query.filter_by(photo_id=photo2.id).count(), 0)
        self.assertEqual(FaceEmbedding.query.filter_by(photo_id=photo3.id).count(), 1)
        self.assertFalse(Photo.query.get(photo1.id).processed)
        self.assertFalse(Photo.query.get(photo2.id).processed)
        self.assertTrue(Photo.query.get(photo3.id).processed)


if __name__ == '__main__':
    unittest.main()
