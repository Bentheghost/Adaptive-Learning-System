"""
Topic Recommendation Routes
"""
from flask import Blueprint, request, jsonify
from models import db, Topic, Subtopic, UserProgress
from extensions import coordinator
from routes.auth import get_current_user_id

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/api/recommendations/next-topic', methods=['GET', 'OPTIONS'])
def get_next_topic_recommendation():
    """Recommends the next subtopic or action based on user progress states"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    user_id_raw = request.args.get('user_id') or get_current_user_id()
    if not user_id_raw:
        return jsonify({'success': False, 'recommendation': 'Welcome! Choose a course to begin.', 'action_type': 'overview'}), 200

    try:
        user_id = int(user_id_raw)
        
        # 1. Look for active, unlocked subtopics that are NOT yet completed, ordered by most recently accessed
        active_progress = UserProgress.query.filter_by(
            user_id=user_id,
            is_completed=False,
            is_unlocked=True
        ).order_by(
            UserProgress.last_accessed.desc().nullslast(),
            UserProgress.started_at.desc().nullslast(),
            UserProgress.id.asc()
        ).first()
        
        if active_progress:
            subtopic = db.session.get(Subtopic, active_progress.subtopic_id)
            if subtopic:
                action = "quiz" if (active_progress.current_phase and active_progress.current_phase % 2 == 0) else "lesson"
                message = f"Take assessment for: {subtopic.name}" if action == "quiz" else f"Continue lesson: {subtopic.name}"
                return jsonify({
                    'success': True,
                    'subtopic_id': subtopic.id,
                    'subtopic_name': subtopic.name,
                    'course_id': subtopic.topic.course_id,
                    'recommendation': message,
                    'action_type': action
                }), 200

        # 2. Fallback to Coordinator/RecommendationAgent for next new topic
        result = coordinator.perceive({
            'task': 'recommend_topic',
            'user_id': user_id,
            'context': {'user_id': user_id}
        }).decide().act()

        if result.get('success') and 'RecommendationAgent' in result.get('results', {}):
            agent_result = result['results']['RecommendationAgent']
            recommendations = agent_result.get('recommendations', [])
            
            if recommendations:
                top_rec = recommendations[0]
                topic_id = top_rec['topic_id']
                
                topic = db.session.get(Topic, topic_id)
                if topic:
                    for sub in topic.subtopics:
                        prog = UserProgress.query.filter_by(user_id=user_id, subtopic_id=sub.id).first()
                        if not prog or not prog.is_completed:
                            return jsonify({
                                'success': True,
                                'subtopic_id': sub.id,
                                'subtopic_name': sub.name,
                                'course_id': topic.course_id,
                                'recommendation': f"Start topic: {sub.name}",
                                'action_type': 'lesson'
                            }), 200

        return jsonify({
            'success': True,
            'recommendation': "Explore your courses to start learning!",
            'action_type': "overview"
        }), 200

    except Exception as e:
        print(f"[RECOMMENDATION ERROR] Graceful fallback triggered: {e}")
        return jsonify({
            'success': False,
            'recommendation': "Select a course track from your library below.",
            'action_type': "overview"
        }), 200
