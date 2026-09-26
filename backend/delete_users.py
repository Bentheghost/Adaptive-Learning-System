"""
Delete Users Entry Point
Delegates to scripts/user_admin.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.user_admin import delete_users

if __name__ == '__main__':
    if len(sys.argv) > 1:
        delete_users(sys.argv[1:])
    else:
        print("Usage: python delete_users.py <username1> [username2 ...]")
