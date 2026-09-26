"""
Database Schema & Progress Reset Entry Point
Delegates to scripts/reset_progress.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.reset_progress import reset_database

if __name__ == '__main__':
    reset_database()