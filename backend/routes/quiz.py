"""
Quiz Generation, Preassessment, Submission, and Verification Routes
"""
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import db, User, Course, Topic, Subtopic, UserProgress, QuizAttempt
from extensions import coordinator, llm_service, update_bkt_mastery
from gamification_engine import update_gamification
from routes.auth import get_current_user_id

quiz_bp = Blueprint('quiz', __name__)

def unlock_next_subtopic(user_id, current_subtopic):
    """Unlock the next sequential subtopic for the learner"""
    topic = current_subtopic.topic
    
    next_subtopic = Subtopic.query.filter(
        Subtopic.topic_id == topic.id,
        Subtopic.order_index > current_subtopic.order_index
    ).order_by(Subtopic.order_index).first()
    
    if next_subtopic:
        existing_progress = UserProgress.query.filter_by(
            user_id=user_id,
            subtopic_id=next_subtopic.id
        ).first()
        
        if not existing_progress:
            progress = UserProgress(
                user_id=user_id,
                subtopic_id=next_subtopic.id,
                is_unlocked=True,
                started_at=datetime.now(timezone.utc)
            )
            db.session.add(progress)
        elif not existing_progress.is_unlocked:
            existing_progress.is_unlocked = True
            existing_progress.started_at = datetime.now(timezone.utc)

@quiz_bp.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    """Generate adaptive quiz questions for a subtopic"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    subtopic_id = data.get('subtopic_id')
    if not subtopic_id:
        return jsonify({'error': 'Missing subtopic_id'}), 400
    
    subtopic = Subtopic.query.get_or_404(subtopic_id)
    
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        subtopic_id=subtopic_id
    ).first()
    
    if not progress or not progress.is_unlocked:
        return jsonify({'error': 'This subtopic is locked.'}), 403
    
    if progress.current_phase in [1, 3, 5]:
        return jsonify({'error': 'Please complete the corresponding lesson tier for this level before attempting the assessment.'}), 403
    
    quiz_difficulty = "beginner"
    if progress.current_phase == 2:
        quiz_difficulty = "beginner"
    elif progress.current_phase == 4:
        quiz_difficulty = "intermediate"
    elif progress.current_phase == 6:
        quiz_difficulty = "advanced"

    result = coordinator.perceive({
        'task': 'generate_quiz',
        'user_id': user_id,
        'context': {
            'subtopic_id': subtopic_id,
            'subtopic_name': subtopic.name,
            'difficulty': quiz_difficulty,
            'knowledge_level': progress.knowledge_level,
            'quiz_attempts': progress.quiz_attempts
        }
    }).decide().act()
    
    if not result.get('success'):
        return jsonify({'error': result.get('error', 'Quiz generation failed')}), 500
    
    assessment_result = result['results'].get('AssessmentAgent', {})
    session_id = str(uuid.uuid4())
    topic = subtopic.topic
    course = topic.course
    
    return jsonify({
        'session_id': session_id,
        'questions': assessment_result.get('questions', []),
        'subtopic_name': subtopic.name,
        'topic_name': topic.name,
        'course_name': course.name,
        'passing_score': subtopic.passing_score
    })

@quiz_bp.route('/api/preassessment/submit', methods=['POST'])
def submit_preassessment():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json or {}
    score = data.get('score', 0)
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    user.has_completed_preassessment = True
    initial_knowledge = 0.2 + (score / 100.0) * 0.6
    update_gamification(user.id, xp_gained=20)
    
    progress_records = UserProgress.query.filter_by(user_id=user.id).all()
    for p in progress_records:
        if p.knowledge_level < initial_knowledge:
            p.knowledge_level = initial_knowledge
            
    db.session.commit()
    
    return jsonify({
        'message': 'Pre-assessment completed successfully',
        'initial_knowledge': initial_knowledge,
        'xp_gained': 20
    })

@quiz_bp.route('/api/quiz/submit', methods=['POST', 'OPTIONS'])
def submit_quiz():
    """Submit quiz, calculate BKT updates, score attempts, and advance curriculum phase"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    subtopic_id = data.get('subtopic_id')
    session_id = data.get('session_id')
    answers = data.get('answers', [])
    
    if not subtopic_id:
        return jsonify({'error': 'Missing subtopic_id identifier parameter'}), 400
        
    subtopic = Subtopic.query.get_or_404(subtopic_id)
    correct_count = 0
    review_data = []
    
    for answer in answers:
        user_answer_raw = answer.get('user_answer', '')
        correct_answer_raw = answer.get('correct_answer', '')
        explanation_raw = answer.get('explanation', 'Review the textbook concepts associated with this subtopic block.')
        
        user_answer = str(user_answer_raw).strip().lower()
        correct_answer = str(correct_answer_raw).strip().lower()
        
        is_correct = (user_answer == correct_answer)
        if is_correct:
            correct_count += 1
            
        review_data.append({
            "question": answer.get('question', ''),
            "user_answer": user_answer_raw,
            "correct_answer": correct_answer_raw,
            "is_correct": is_correct,
            "explanation": explanation_raw,
            "difficulty": answer.get('difficulty', 'beginner'),
            "misconception": None
        })
        
        misconception = None
        if not is_correct:
            try:
                misconception = llm_service.explain_answer(
                    answer.get('question', ''), 
                    user_answer_raw, 
                    correct_answer_raw,
                    subtopic.name
                )
            except Exception:
                misconception = None
            review_data[-1]["misconception"] = misconception
        
        attempt = QuizAttempt(
            user_id=user_id,
            subtopic_id=subtopic_id,
            session_id=session_id,
            question=answer.get('question', ''),
            user_answer=str(user_answer_raw),
            correct_answer=str(correct_answer_raw),
            is_correct=is_correct,
            difficulty=answer.get('difficulty', 'beginner'),
            misconception=misconception
        )
        db.session.add(attempt)
    
    total_questions = len(answers)
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    passed = score >= 70.0
    
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        subtopic_id=subtopic_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            subtopic_id=subtopic_id,
            quiz_attempts=0,
            best_score=0.0,
            knowledge_level=0.50,
            confidence=0.1
        )
        db.session.add(progress)
    
    progress.quiz_attempts += 1
    progress.last_score = score
    if score > progress.best_score:
        progress.best_score = score
        
    for attempt, item in zip(QuizAttempt.query.filter_by(session_id=session_id).all(), review_data):
        is_correct_bool = bool(item["is_correct"])
        progress.knowledge_level = update_bkt_mastery(progress.knowledge_level, is_correct_bool, difficulty=item["difficulty"])
        attempt.knowledge_snapshot = progress.knowledge_level
        
    progress.confidence = score / 100
    progress.updated_at = datetime.now(timezone.utc)
    
    if passed:
        update_gamification(user_id, xp_gained=50)
    
    message_text = "Keep studying to boost your BKT mastery estimate!"
    recommendations = []

    if passed:
        if progress.current_phase == 2:
            progress.current_phase = 3
            message_text = "Success! Beginner tier mastered. Unlocking your Intermediate lesson track."
            recommendations.append(f"👍 Strong beginner performance! The BKT engine has promoted you to the Intermediate level for '{subtopic.name}'. Click 'Read Lesson' to explore advanced operator properties.")
        elif progress.current_phase == 4:
            progress.current_phase = 5
            message_text = "Excellent! Intermediate tier mastered. Unlocking your Advanced lesson track."
            recommendations.append(f"🔥 Proficiency verified! Ready for deep technical concepts. The curriculum engine has unlocked your Advanced tier lesson module covering heap memory allocations and LEGB scope rules.")
        elif progress.current_phase == 6:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)
            unlock_next_subtopic(user_id, subtopic)
            message_text = "Sensational! You've completely mastered all tiers of this subtopic! Next topic unlocked."
            if score == 100:
                recommendations.append(f"🎯 Perfect advanced score! Your multi-tier conceptual understanding of '{subtopic.name}' is exceptional. The core system loop has unlocked the subsequent subtopic track.")
            else:
                recommendations.append(f"🏆 Ultimate Mastery Achieved! You have successfully advanced through all three difficulty tiers. Move on to your next unlocked subtopic module.")
    else:
        if score < 70:
            recommendations.append(f"📚 Concept Review Recommended: Your score fell below the 70% threshold for Phase {progress.current_phase}. Re-verify your previous lesson notes before attempting this tier again.")
            
        if progress.current_phase == 2:
            progress.current_phase = 1
        elif progress.current_phase == 4:
            progress.current_phase = 3
        elif progress.current_phase == 6:
            progress.current_phase = 5

    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': round(score, 1),
        'correct_count': correct_count,
        'total_questions': total_questions,
        'passed': passed,
        'best_score': progress.best_score,
        'quiz_attempts': progress.quiz_attempts,
        'current_phase': progress.current_phase,
        'recommendations': recommendations,
        'review_data': review_data,
        'message': message_text
    }), 200

@quiz_bp.route('/api/quiz/flag', methods=['POST'])
def flag_quiz_question():
    """Flags a specific question from a quiz attempt"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json or {}
    question_text = data.get('question')
    
    attempt = QuizAttempt.query.filter_by(
        user_id=user_id,
        question=question_text
    ).order_by(QuizAttempt.created_at.desc()).first()
    
    if attempt:
        attempt.is_flagged = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Question flagged for review'})
        
    return jsonify({'error': 'Question attempt not found'}), 404

@quiz_bp.route('/api/quiz/history', methods=['GET'])
def get_quiz_history():
    """Get history of quiz attempts for the authenticated user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
        
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.created_at.desc()).limit(100).all()
    result = [{
        'id': a.id,
        'subtopic_id': a.subtopic_id,
        'session_id': a.session_id,
        'question': a.question,
        'user_answer': a.user_answer,
        'correct_answer': a.correct_answer,
        'is_correct': a.is_correct,
        'difficulty': a.difficulty,
        'misconception': a.misconception,
        'created_at': a.created_at.isoformat() if a.created_at else None
    } for a in attempts]
    
    return jsonify(result)
