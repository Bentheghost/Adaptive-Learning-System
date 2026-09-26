"""
Courses, Curriculum and Lesson Generation Routes
"""
import re
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import db, Course, Topic, Subtopic, UserProgress, LearningSession
from extensions import coordinator
from gamification_engine import update_gamification
from routes.auth import get_current_user_id

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with user progress"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    courses = Course.query.order_by(Course.order_index).all()
    result = []
    
    for course in courses:
        total_subtopics = sum(len(topic.subtopics) for topic in course.topics)
        completed_subtopics = 0
        
        for topic in course.topics:
            for subtopic in topic.subtopics:
                progress = UserProgress.query.filter_by(
                    user_id=user_id,
                    subtopic_id=subtopic.id
                ).first()
                if progress and progress.is_completed:
                    completed_subtopics += 1
        
        completion_percentage = (completed_subtopics / total_subtopics * 100) if total_subtopics > 0 else 0
        
        result.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'difficulty': course.difficulty,
            'total_topics': len(course.topics),
            'total_subtopics': total_subtopics,
            'completed_subtopics': completed_subtopics,
            'completion_percentage': round(completion_percentage, 1)
        })
    
    return jsonify(result)

@courses_bp.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_detail(course_id):
    """Get course with all topics, subtopics and student progress"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    course = Course.query.get_or_404(course_id)
    
    # Auto-unlock first subtopic if no progress exists
    first_topic = Topic.query.filter_by(course_id=course.id).order_by(Topic.order_index).first()
    if first_topic:
        first_subtopic = Subtopic.query.filter_by(topic_id=first_topic.id).order_by(Subtopic.order_index).first()
        if first_subtopic:
            any_progress_in_course = db.session.query(UserProgress).join(
                Subtopic, UserProgress.subtopic_id == Subtopic.id
            ).join(
                Topic, Subtopic.topic_id == Topic.id
            ).filter(
                Topic.course_id == course.id,
                UserProgress.user_id == user_id
            ).first()
            
            if not any_progress_in_course:
                first_progress = UserProgress(
                    user_id=user_id,
                    subtopic_id=first_subtopic.id,
                    is_unlocked=True,
                    started_at=datetime.now(timezone.utc)
                )
                db.session.add(first_progress)
                db.session.commit()
    
    # Build topics data
    topics_data = []
    for topic in course.topics:
        subtopics_data = []
        for subtopic in topic.subtopics:
            progress = UserProgress.query.filter_by(
                user_id=user_id,
                subtopic_id=subtopic.id
            ).first()
            
            subtopics_data.append({
                'id': subtopic.id,
                'name': subtopic.name,
                'description': subtopic.description,
                'order_index': subtopic.order_index,
                'passing_score': subtopic.passing_score,
                'is_unlocked': progress.is_unlocked if progress else False,
                'is_completed': progress.is_completed if progress else False,
                'has_learned': progress.has_learned if progress else False,
                'best_score': progress.best_score if progress else 0,
                'last_score': progress.last_score if progress else 0,
                'quiz_attempts': progress.quiz_attempts if progress else 0,
                'knowledge_level': progress.knowledge_level if progress else 0.0,
                'current_phase': progress.current_phase if progress else 1
            })
        
        topics_data.append({
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'order_index': topic.order_index,
            'subtopics': subtopics_data
        })
    
    return jsonify({
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'difficulty': course.difficulty,
        'topics': topics_data
    })

@courses_bp.route('/api/generate-lesson', methods=['POST', 'OPTIONS'])
def generate_lesson():
    """Generate lesson for a subtopic with smart database caching and curriculum alignment tracking"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    subtopic_id = data.get('subtopic_id')
    is_review = data.get('is_review', False)
    previous_score = data.get('previous_score', 0)
    
    if not subtopic_id:
        return jsonify({'error': 'Missing subtopic_id'}), 400
        
    subtopic = Subtopic.query.get_or_404(subtopic_id)
    topic = subtopic.topic
    course = topic.course
    
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        subtopic_id=subtopic_id
    ).first()
    
    if progress and not progress.is_unlocked:
        return jsonify({'error': 'This subtopic is locked.'}), 403

    current_difficulty = "beginner"
    if progress:
        if progress.current_phase in [1, 2]:
            current_difficulty = "beginner"
            progress.current_phase = 1
        elif progress.current_phase in [3, 4]:
            current_difficulty = "intermediate"
            progress.current_phase = 3
        elif progress.current_phase in [5, 6]:
            current_difficulty = "advanced"
            progress.current_phase = 5
    else:
        progress = UserProgress(
            user_id=user_id,
            subtopic_id=subtopic_id,
            is_unlocked=True,
            current_phase=1,
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(progress)
        
    target_type = 'review' if is_review else 'lesson'
    
    existing_session = LearningSession.query.filter_by(
        user_id=user_id,
        subtopic_id=subtopic_id,
        session_type=target_type,
        difficulty_level=current_difficulty
    ).order_by(LearningSession.created_at.desc()).first()

    is_placeholder = False
    if existing_session:
        content_lower = (existing_session.content or "").lower()
        is_placeholder = (
            not existing_session.content or 
            len(existing_session.content.strip()) < 10 or
            "check your internet connection" in content_lower or 
            "fallback" in content_lower
        )

    if existing_session and not is_review and not is_placeholder:
        if progress:
            progress.has_learned = True
            progress.last_accessed = datetime.now(timezone.utc)
            if progress.current_phase == 1:
                progress.current_phase = 2
            elif progress.current_phase == 3:
                progress.current_phase = 4
            elif progress.current_phase == 5:
                progress.current_phase = 6
            db.session.commit()
            
        cleaned_cache = re.sub(r'^```(json|html|markdown)?\s*|```$', '', existing_session.content.strip(), flags=re.MULTILINE)
        
        return jsonify({
            'content': cleaned_cache,
            'subtopic_name': subtopic.name,
            'topic_name': topic.name,
            'course_name': course.name,
            'difficulty': current_difficulty,
            'current_phase': progress.current_phase if progress else 1,
            'is_review': is_review,
            'cached': True
        }), 200

    try:
        result = coordinator.perceive({
            'task': 'generate_review' if is_review else 'generate_lesson',
            'user_id': user_id,
            'context': {
                'subtopic_id': subtopic_id,
                'subtopic_name': subtopic.name,
                'difficulty': current_difficulty,
                'is_review': is_review,
                'quiz_score': previous_score,
                'knowledge_level': progress.knowledge_level if progress else 0.0
            }
        }).decide().act()
    except Exception as e:
        print(f"[CRITICAL] Multi-agent execution failure: {e}")
        return jsonify({'error': 'The agent core is temporarily overloaded. Please try again in a few moments.'}), 429
    
    if not result.get('success', False):
        return jsonify({'error': result.get('error', 'Generation failed')}), 500
    
    teaching_result = result['results'].get('TeachingAgent', {})
    content = teaching_result.get('content', '')
    
    if content:
        content = re.sub(r'^```(json|html|markdown)?\s*|```$', '', content.strip(), flags=re.MULTILINE)
    
    learning_session = LearningSession(
        user_id=user_id,
        subtopic_id=subtopic_id,
        content=content,
        session_type=target_type,
        difficulty_level=current_difficulty,
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(learning_session)
    
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            subtopic_id=subtopic_id,
            is_unlocked=True,
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(progress)
    
    progress.has_learned = True
    progress.last_accessed = datetime.now(timezone.utc)
    
    if progress.current_phase == 1:
        progress.current_phase = 2
    elif progress.current_phase == 3:
        progress.current_phase = 4
    elif progress.current_phase == 5:
        progress.current_phase = 6
    
    db.session.commit()
    update_gamification(user_id, xp_gained=10)
    
    return jsonify({
        'content': content,
        'subtopic_name': subtopic.name,
        'topic_name': topic.name,
        'course_name': course.name,
        'difficulty': current_difficulty,
        'is_review': is_review,
        'cached': False
    }), 200
