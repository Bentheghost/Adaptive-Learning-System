"""
Lesson Cache Clearer Entry Point
Delegates to scripts/clear_lesson_cache.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.clear_lesson_cache import clear_lesson_cache

if __name__ == '__main__':
    clear_lesson_cache()