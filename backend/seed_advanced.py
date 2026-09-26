"""
Advanced Quiz Questions Seeder Entry Point
Delegates to scripts/seed_advanced.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.seed_advanced import seed_advanced_questions

if __name__ == '__main__':
    seed_advanced_questions()