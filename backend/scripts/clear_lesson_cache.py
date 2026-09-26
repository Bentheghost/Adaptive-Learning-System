"""
Reset user lesson states to force fresh LLM lesson generation
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, UserProgress

def clear_lesson_cache():
    with app.app_context():
        print("\nWiping user progress lesson states to clear the cache...")
        progress_records = UserProgress.query.all()
        for prog in progress_records:
            prog.has_learned = False
            if hasattr(prog, 'generated_content'):
                prog.generated_content = None
            if hasattr(prog, 'lesson_text'):
                prog.lesson_text = None
        db.session.commit()
        print("--- SUCCESS: Lesson cache cleared completely! ---")
        print("The next time you open an intermediate or advanced lesson, a fresh, aligned copy will be generated.\n")

if __name__ == '__main__':
    clear_lesson_cache()
