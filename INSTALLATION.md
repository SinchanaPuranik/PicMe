# PICME Installation Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Webcam (for selfie capture feature)
- 4GB+ RAM recommended

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd MajorProject
```

## Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Installation may take 10-15 minutes due to deep learning libraries.

## Step 4: Install and Configure PostgreSQL

### Windows

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and remember the password for the `postgres` user
3. Add PostgreSQL to PATH (usually done automatically)

### Linux

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Mac

```bash
brew install postgresql
brew services start postgresql
```

## Step 5: Setup Database

```bash
python setup_database.py
```

Enter your PostgreSQL admin password when prompted. This script will:
- Create database user `picme_user`
- Create databases: `picme_dev`, `picme_test`, `picme_prod`
- Grant necessary privileges

## Step 6: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

2. Edit `.env` and update if needed (defaults should work):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEV_DATABASE_URL=postgresql://picme_user:picme_pass@localhost/picme_dev
```

## Step 7: Initialize Database Tables

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Step 8: Run the Application

```bash
python run.py
```

The application will be available at: http://localhost:5000

## Step 9: Login

Default admin credentials:
- Username: `admin`
- Password: `admin123`

**Important:** Change the admin password after first login!

## Troubleshooting

### Issue: `psycopg2` installation fails

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: Database connection error

**Solution:**
1. Verify PostgreSQL is running:
```bash
# Windows
pg_ctl status

# Linux
sudo systemctl status postgresql
```

2. Check database exists:
```bash
psql -U postgres -l
```

### Issue: MTCNN model download fails

**Solution:**
- Ensure stable internet connection
- The model will download automatically on first use
- Check firewall settings

### Issue: Webcam not accessible

**Solution:**
1. Grant browser permission to access camera
2. Use HTTPS (or localhost)
3. Check if another application is using the webcam

### Issue: Out of memory during processing

**Solution:**
- Process photos in smaller batches
- Close other applications
- Increase system swap/virtual memory

## Development Mode

For development with auto-reload:

```bash
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac
flask run --debug
```

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

Run model evaluation:
```bash
python tests/evaluate_models.py
```

## Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --listen=*:5000 run:app
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-secret-key>
DATABASE_URL=postgresql://picme_user:picme_pass@localhost/picme_prod
```

## Docker Deployment (Optional)

```bash
docker-compose up -d
```

## Updating the Application

```bash
git pull
pip install -r requirements.txt --upgrade
flask db migrate -m "Migration message"
flask db upgrade
```

## Support

For issues and questions:
- Check the documentation in README.md
- Review closed issues on GitHub
- Create a new issue with detailed information

## Security Notes

1. Change default admin password immediately
2. Use strong SECRET_KEY in production
3. Enable HTTPS in production
4. Regularly backup database
5. Keep dependencies updated

## Performance Optimization

1. **Database Indexing:**
   - Already configured in models.py
   
2. **Image Optimization:**
   - Consider resizing large uploads
   - Implement lazy loading for galleries
   
3. **Caching:**
   - Enable Flask caching for static resources
   - Cache embeddings in production

4. **Batch Processing:**
   - Process photos in background tasks
   - Use Celery for async processing (advanced)

## Next Steps

1. Create your first event
2. Upload test photos
3. Process photos to generate embeddings
4. Test face matching with webcam
5. Review performance metrics
6. Compare FaceNet vs ArcFace results
