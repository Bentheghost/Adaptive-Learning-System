from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Email Verification
    is_verified = db.Column(db.Boolean, default=True)
    verification_otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # New Columns for Gamification & Preassessment
    has_completed_preassessment = db.Column(db.Boolean, default=False)
    xp = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_sessions = db.relationship('LearningSession', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    """Top level: Python Basics, Web Development, etc."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    topics = db.relationship('Topic', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Topic.order_index')

class Topic(db.Model):
    """Mid level: Variables, Functions, Loops, etc."""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subtopics = db.relationship('Subtopic', backref='topic', lazy=True, cascade='all, delete-orphan', order_by='Subtopic.order_index')

class Subtopic(db.Model):
    """Lowest level: Data Types, Variable Scope, etc."""
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Integer, default=70)  # Minimum % to pass
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('UserProgress', backref='subtopic', lazy=True, cascade='all, delete-orphan')

class UserProgress(db.Model):
    """Track user progress for each subtopic with multi-tier phase tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    
    is_unlocked = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False) # True only after completing Phase 6
    has_learned = db.Column(db.Boolean, default=False)
    
    # 🎯 NEW: Multi-Phase State Tracking (Values: 1 to 6)
    # 1: Beginner Lesson, 2: Beginner Quiz, 3: Intermediate Lesson, 4: Intermediate Quiz, 5: Advanced Lesson, 6: Advanced Quiz
    current_phase = db.Column(db.Integer, default=1, nullable=False)
    
    quiz_attempts = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Float, default=0.0)
    last_score = db.Column(db.Float, default=0.0)
    
    knowledge_level = db.Column(db.Float, default=0.0) 
    confidence = db.Column(db.Float, default=0.0)
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'subtopic_id', name='unique_user_subtopic'),)
    
class LearningSession(db.Model):
    """Record of learning sessions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    session_type = db.Column(db.String(20), default='lesson')  # 'lesson' or 'review'
    difficulty_level = db.Column(db.String(20))
    duration = db.Column(db.Integer)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizAttempt(db.Model):
    """Individual quiz question attempts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Group questions by quiz session
    
    question = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    difficulty = db.Column(db.String(20))
    
    # New Columns for Analytics & Hallucination Safeguards
    is_flagged = db.Column(db.Boolean, default=False)
    misconception = db.Column(db.Text)
    knowledge_snapshot = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    question_text = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(250), nullable=False)
    option_2 = db.Column(db.String(250), nullable=False)
    option_3 = db.Column(db.String(250), nullable=False)
    option_4 = db.Column(db.String(250), nullable=False)
    correct_answer = db.Column(db.String(250), nullable=False)
    explanation = db.Column(db.Text)

# ==========================================
# AGGRESSIVE CACHING MODELS
# ==========================================

class CachedLesson(db.Model):
    """Caches AI-generated lessons to avoid API rate limits and latency"""
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, index=True)
    knowledge_level = db.Column(db.Float, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CachedQuizQuestion(db.Model):
    """Stores a pool of generated quiz questions to serve instantly"""
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, index=True)
    question_json = db.Column(db.Text, nullable=False) # Stores the full question/options/answer dict as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CachedExplanation(db.Model):
    """Caches the LLM explanation for why a specific wrong answer is wrong"""
    id = db.Column(db.Integer, primary_key=True)
    question_hash = db.Column(db.String(64), unique=True, nullable=False, index=True) # hash(question + user_answer + correct_answer)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TelemetryCache(db.Model):
    """Caches user interaction telemetry such as time spent, clicks, and code attempts"""
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True) # e.g., 'lesson_view', 'code_attempt'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    context = db.Column(db.String(100)) # e.g., subtopic name or id
    data = db.Column(db.Text, nullable=False) # JSON payload containing clicks, duration, code, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    """Stores chat history for the global Tutor Chatbot"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)