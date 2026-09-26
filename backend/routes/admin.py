"""
Admin and Lecturer Dashboard Routes
"""
import io
import csv
import json
from flask import Blueprint, jsonify, Response
from models import db, User, Subtopic, UserProgress, QuizAttempt, TelemetryCache
from routes.auth import check_admin_or_lecturer_auth

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/export', methods=['GET'])
def export_students():
    user, err_response = check_admin_or_lecturer_auth()
    if err_response:
        return err_response
        
    users = User.query.filter_by(role='student').all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Username', 'Email', 'XP', 'Streak', 'Pre-assessment Completed', 'Joined Date', 'Last Activity'])
    for u in users:
        writer.writerow([
            u.id,
            u.username,
            u.email,
            u.xp,
            u.current_streak,
            'Yes' if u.has_completed_preassessment else 'No',
            u.created_at.strftime('%Y-%m-%d') if u.created_at else '',
            u.last_activity_date.strftime('%Y-%m-%d') if u.last_activity_date else ''
        ])
        
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=student_progress_report.csv'}
    )

@admin_bp.route('/api/admin/flagged-questions', methods=['GET'])
def get_flagged_questions():
    user, err_response = check_admin_or_lecturer_auth()
    if err_response:
        return err_response
        
    flagged = QuizAttempt.query.filter_by(is_flagged=True).order_by(QuizAttempt.created_at.desc()).all()
    result = []
    for f in flagged:
        student = db.session.get(User, f.user_id)
        result.append({
            'id': f.id,
            'question': f.question,
            'user_answer': f.user_answer,
            'correct_answer': f.correct_answer,
            'difficulty': f.difficulty,
            'misconception': f.misconception,
            'username': student.username if student else 'Unknown',
            'date': f.created_at.strftime('%Y-%m-%d %H:%M') if f.created_at else ''
        })
    return jsonify(result)

@admin_bp.route('/api/admin/students', methods=['GET'])
def get_students():
    """Get all students and their progress (Admin/Lecturer only)"""
    user, err_response = check_admin_or_lecturer_auth()
    if err_response:
        return err_response

    students = User.query.filter_by(role='student').all()
    result = []
    
    for student in students:
        progress_records = UserProgress.query.filter_by(user_id=student.id).all()
        
        completed_subtopics = sum(1 for p in progress_records if p.is_completed)
        unlocked_subtopics = sum(1 for p in progress_records if p.is_unlocked)
        total_score = sum(p.best_score for p in progress_records)
        avg_knowledge = sum(p.knowledge_level for p in progress_records)
        
        count = len(progress_records)
        avg_score = round(total_score / count, 1) if count > 0 else 0
        avg_knowledge = round(avg_knowledge / count, 2) if count > 0 else 0
        
        recent_progress = sorted(progress_records, key=lambda x: x.last_accessed or x.created_at, reverse=True) if progress_records else []
        recent_activity = "None"
        if recent_progress:
            sub = db.session.get(Subtopic, recent_progress[0].subtopic_id)
            recent_activity = sub.name if sub else "Unknown"

        result.append({
            'id': student.id,
            'username': student.username,
            'email': student.email,
            'joined': student.created_at.strftime('%Y-%m-%d') if student.created_at else '',
            'completed_subtopics': completed_subtopics,
            'unlocked_subtopics': unlocked_subtopics,
            'avg_score': avg_score,
            'avg_knowledge': avg_knowledge,
            'recent_activity': recent_activity
        })
        
    return jsonify(result)

@admin_bp.route('/api/admin/telemetry', methods=['GET'])
def get_admin_telemetry():
    """Get aggregated telemetry data for the admin dashboard"""
    user, err_response = check_admin_or_lecturer_auth()
    if err_response:
        return err_response

    try:
        telemetry_events = TelemetryCache.query.all()
        lesson_durations = []
        code_attempts = 0
        error_distribution = {}
        
        for event in telemetry_events:
            try:
                data = json.loads(event.data)
                if event.event_type == 'lesson_view':
                    if 'duration_seconds' in data:
                        lesson_durations.append(data['duration_seconds'])
                elif event.event_type == 'code_attempt':
                    code_attempts += 1
                    if not data.get('success') and data.get('error_type'):
                        error_type = data['error_type']
                        error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
            except Exception:
                pass
                
        avg_lesson_time = sum(lesson_durations) / len(lesson_durations) if lesson_durations else 0
        error_chart_data = [{'name': k, 'count': v} for k, v in error_distribution.items()]
        
        return jsonify({
            'avg_lesson_time': round(avg_lesson_time),
            'total_code_attempts': code_attempts,
            'error_distribution': error_chart_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
