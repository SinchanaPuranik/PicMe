from flask import Blueprint

# Create blueprints
admin_bp = Blueprint('admin', __name__)
user_bp = Blueprint('user', __name__)
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.routes import admin, user, auth, main
