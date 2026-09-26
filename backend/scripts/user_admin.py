"""
User Administration Utility
Usage:
    python user_admin.py list
    python user_admin.py delete <username1> <username2> ...
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, User

def list_users():
    with app.app_context():
        users = User.query.order_by(User.id).all()
        print(f"\n--- Total Users in DB: {len(users)} ---")
        for u in users:
            print(f"- ID: {u.id:3d} | Username: {u.username:15s} | Role: {u.role:8s} | Email: {u.email}")
        print("Done.\n")

def delete_users(usernames):
    if not usernames:
        print("No usernames specified to delete.")
        return
    with app.app_context():
        for username in usernames:
            user = User.query.filter_by(username=username).first()
            if user:
                db.session.delete(user)
                print(f"Deleted user: {username}")
            else:
                print(f"User not found: {username}")
        db.session.commit()
        print("Done.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'list':
            list_users()
        elif cmd == 'delete':
            delete_users(sys.argv[2:])
        else:
            print("Unknown command. Usage: python user_admin.py [list|delete <usernames...>]")
    else:
        list_users()
