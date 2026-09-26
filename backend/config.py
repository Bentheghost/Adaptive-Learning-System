import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'adaptive-learning-default-secret-key'
    
    # Database Configuration (supports DATABASE_URL from .env with fallback)
    default_db_uri = "postgresql+psycopg://postgres:admin123@localhost:5432/adaptive_learning2_db"
    raw_db_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI') or default_db_uri
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
    # API Keys & Third-Party Services
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@adaptivelearning.com')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Knowledge Tracing Parameters
    INITIAL_KNOWLEDGE = 0.0  
    LEARNING_RATE = 0.15  # Progression rate per practice
    FORGETTING_RATE = 0.05  # Ebbinghaus decay factor
    
    # Difficulty Levels
    DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced']