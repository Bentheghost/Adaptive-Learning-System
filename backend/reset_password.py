"""
Password Reset Entry Point
Delegates to scripts/reset_password.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.reset_password import reset_password

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ident = sys.argv[1]
        pwd = sys.argv[2] if len(sys.argv) > 2 else "Password123!"
        reset_password(ident, pwd)
    else:
        print("Usage: python reset_password.py <email_or_username> [new_password]")
        ident = input("Identifier: ").strip()
        if ident:
            reset_password(ident)
