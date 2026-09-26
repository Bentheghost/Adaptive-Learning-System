"""
BKT Math Verification Test Suite Entry Point
Delegates to tests/test_bkt.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tests.test_bkt import test_bkt

if __name__ == "__main__":
    test_bkt()
