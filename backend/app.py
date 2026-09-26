"""
Adaptive E-Learning System - Flask Application Entry Point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import (
    db, User, Course, Topic, Subtopic, UserProgress, 
    LearningSession, QuizAttempt, TelemetryCache, ChatMessage, QuizQuestion
)
from extensions import knowledge_tracker, llm_service, coordinator, update_bkt_mastery
from services.seed_data import init_database_data

# Route Blueprints
from routes import (
    auth_bp, admin_bp, courses_bp, 
    quiz_bp, recommendations_bp, progress_bp, tutor_bp
)

def create_app():
    """Application factory for Adaptive E-Learning System"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS for local development and production
    CORS(app, 
         supports_credentials=True, 
         origins=r"https?://.*",
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Initialize database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(tutor_bp)

    # Root Health Route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Adaptive E-Learning API',
            'version': '2.0.0',
            'status': 'running'
        })

    return app

app = create_app()

def init_db():
    """Initialize database tables and seed baseline curriculum"""
    with app.app_context():
        init_database_data()

# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("🚀 Starting Adaptive E-Learning System Backend...")
    print(f"📍 Server running on: http://localhost:{port}")
    print(f"📊 Agent Analytics:  http://localhost:{port}/api/agent-analytics")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)