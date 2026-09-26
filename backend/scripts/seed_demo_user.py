"""
Seed demo user account
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, User
from werkzeug.security import generate_password_hash

USERNAME = 'demo_user'
EMAIL = 'demo@example.com'

def seed_demo_user():
    with app.app_context():
        user = User.query.filter_by(username=USERNAME).first()
        if user:
            print(f"User '{USERNAME}' already exists with id {user.id}")
        else:
            user = User(
                username=USERNAME,
                email=EMAIL,
                password_hash=generate_password_hash('password123'),
                role='student',
                is_verified=True,
                has_completed_preassessment=True
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created demo user '{USERNAME}' with id {user.id}")

if __name__ == '__main__':
    seed_demo_user()
