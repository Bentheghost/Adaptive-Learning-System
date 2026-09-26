"""
Routes package for Adaptive E-Learning System
"""
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.courses import courses_bp
from routes.quiz import quiz_bp
from routes.recommendations import recommendations_bp
from routes.progress import progress_bp
from routes.tutor import tutor_bp

__all__ = [
    'auth_bp',
    'admin_bp',
    'courses_bp',
    'quiz_bp',
    'recommendations_bp',
    'progress_bp',
    'tutor_bp'
]
