"""
Cache clearing utility
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, LearningSession, CachedLesson, CachedQuizQuestion, CachedExplanation

def clear_all_caches():
    with app.app_context():
        count_sessions = db.session.query(LearningSession).delete()
        count_lessons = db.session.query(CachedLesson).delete()
        count_questions = db.session.query(CachedQuizQuestion).delete()
        count_explanations = db.session.query(CachedExplanation).delete()
        db.session.commit()
        print(f"\n--- SUCCESS: Cleared Caches ---")
        print(f"- Learning Sessions: {count_sessions}")
        print(f"- Cached Lessons: {count_lessons}")
        print(f"- Cached Quiz Questions: {count_questions}")
        print(f"- Cached Explanations: {count_explanations}")
        print("-------------------------------\n")

if __name__ == '__main__':
    clear_all_caches()
