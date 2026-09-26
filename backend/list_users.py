"""
List Users Entry Point
Delegates to scripts/user_admin.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.user_admin import list_users

if __name__ == '__main__':
    list_users()
