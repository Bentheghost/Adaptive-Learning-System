"""
Reset database schema / tables for progress tracking
"""
import sys
import os
import traceback

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db

def reset_database():
    print("⚠️ Hard resetting database tables to apply fresh schema...")
    with app.app_context():
        try:
            db.reflect()
            print("Dropping existing student activity structures...")
            db.drop_all()
            print("Recreating updated schema blueprints...")
            db.create_all()
            print("\n-------------------------------------------------------------")
            print("✅ SUCCESS: Database schema rebuilt completely!")
            print(" Your account tracking is at a pure baseline state.")
            print("-------------------------------------------------------------\n")
        except Exception as e:
            print(f"❌ Rebuild failure encountered: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    reset_database()
