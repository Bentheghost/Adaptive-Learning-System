"""
Demo User Seeder Entry Point
Delegates to scripts/seed_demo_user.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.seed_demo_user import seed_demo_user

if __name__ == '__main__':
    seed_demo_user()
