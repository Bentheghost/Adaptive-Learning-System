"""
Password Reset Utility
Usage:
    python reset_password.py <email_or_username> [new_password]
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def reset_password(identifier, new_password="Password123!"):
    with app.app_context():
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ Password for user '{user.username}' ({user.email}) successfully reset to: {new_password}")
        else:
            print(f"❌ User not found with email/username: {identifier}")

if __name__ == '__main__':
    if len(sys.path) > 1 and len(sys.argv) > 1:
        ident = sys.argv[1]
        pwd = sys.argv[2] if len(sys.argv) > 2 else "Password123!"
        reset_password(ident, pwd)
    else:
        print("Enter email or username to reset password:")
        ident = input("Identifier: ").strip()
        if ident:
            reset_password(ident)
        else:
            print("No identifier provided. Exiting.")
