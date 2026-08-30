import io
import unittest
from datetime import datetime

from app import create_app, db
from app.models import Event, User


class TestUploadRedirect(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        self.admin = User(username='admin', email='admin@example.com', is_admin=True)
        self.admin.set_password('admin123')
        db.session.add(self.admin)
        db.session.commit()

        self.event = Event(
            name='Upload Event',
            description='Test event',
            event_date=datetime.utcnow(),
            location='HQ',
            creator_id=self.admin.id,
        )
        db.session.add(self.event)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_upload_redirects_back_to_upload_page(self):
        self.client.post('/auth/admin-login', data={
            'username': 'admin',
            'password': 'admin123',
        }, follow_redirects=False)

        image = io.BytesIO(b'fake-image-data')
        image.name = 'test.jpg'

        response = self.client.post(
            f'/admin/events/{self.event.id}/upload',
            data={'photos': [image]},
            content_type='multipart/form-data',
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f'/admin/events/{self.event.id}/upload')


if __name__ == '__main__':
    unittest.main()
