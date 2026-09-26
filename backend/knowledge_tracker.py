"""
Knowledge Tracker - Manages user progress and knowledge state
"""
from models import db, UserProgress, Subtopic, QuizAttempt
from datetime import datetime, timedelta
import numpy as np

class KnowledgeTracker:
    """
    Tracks and manages user knowledge progression using 
    Bayesian Knowledge Tracing (BKT) probability models and forgetting curves.
    """
    
    # Dynamic BKT parameters per difficulty tier
    DIFFICULTY_PARAMS = {
        "beginner": {
            "p_trans": 0.25,  # Higher probability of learning transition
            "p_guess": 0.30,  # Higher probability of guessing correctly
            "p_slip": 0.10,   # Lower probability of making a careless slip
        },
        "intermediate": {
            "p_trans": 0.15,
            "p_guess": 0.20,
            "p_slip": 0.15,
        },
        "advanced": {
            "p_trans": 0.10,  # Harder to transition / learn quickly
            "p_guess": 0.10,  # Harder to guess correctly
            "p_slip": 0.20,   # Higher chance of slipping due to complexity
        }
    }
    
    DEFAULT_P_INIT = 0.20
    DEFAULT_P_TRANS = 0.15
    DEFAULT_P_GUESS = 0.20
    DEFAULT_P_SLIP = 0.10

    def __init__(self):
        self.forgetting_rate = 0.05  # Rate at which knowledge decays
        
    @staticmethod
    def calculate_posterior(prior, is_correct, p_slip=DEFAULT_P_SLIP, p_guess=DEFAULT_P_GUESS):
        """
        Step 1: Calculate posterior probability of knowledge given observation P(L | O) using Bayes' Rule.
        
        P(L | O = correct)   = [P(L) * (1 - P(S))] / [P(L) * (1 - P(S)) + (1 - P(L)) * P(G)]
        P(L | O = incorrect) = [P(L) * P(S)]       / [P(L) * P(S)       + (1 - P(L)) * (1 - P(G))]
        """
        prior = max(0.0001, min(0.9999, float(prior)))
        
        if is_correct:
            numerator = prior * (1.0 - p_slip)
            denominator = numerator + ((1.0 - prior) * p_guess)
        else:
            numerator = prior * p_slip
            denominator = numerator + ((1.0 - prior) * (1.0 - p_guess))
            
        if denominator == 0:
            return prior
            
        return numerator / denominator

    @staticmethod
    def apply_transition(posterior, p_trans=DEFAULT_P_TRANS):
        """
        Step 2: Account for learning transition state P(T).
        P(L_t+1) = P(L_t | O_t) + (1 - P(L_t | O_t)) * P(T)
        """
        posterior = max(0.0, min(1.0, float(posterior)))
        return posterior + (1.0 - posterior) * p_trans

    def update_bkt_step(self, current_mastery, is_correct, difficulty="beginner", p_trans=None, p_guess=None, p_slip=None):
        """
        Full Bayesian Knowledge Tracing updating step for a single item observation.
        Combines posterior calculation via Bayes' Rule and learning transition updating.
        """
        params = self.DIFFICULTY_PARAMS.get(str(difficulty).lower(), self.DIFFICULTY_PARAMS["beginner"])
        
        t_rate = p_trans if p_trans is not None else params["p_trans"]
        g_rate = p_guess if p_guess is not None else params["p_guess"]
        s_rate = p_slip if p_slip is not None else params["p_slip"]
        
        posterior = self.calculate_posterior(current_mastery, is_correct, p_slip=s_rate, p_guess=g_rate)
        next_mastery = self.apply_transition(posterior, p_trans=t_rate)
        
        return min(1.0, max(0.0, float(next_mastery)))

    def get_or_create_progress(self, user_id, subtopic_id):
        """Get or create user progress for a subtopic"""
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            subtopic_id=subtopic_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                subtopic_id=subtopic_id,
                is_unlocked=False,
                is_completed=False,
                has_learned=False,
                knowledge_level=self.DEFAULT_P_INIT
            )
            db.session.add(progress)
            db.session.commit()
        
        return progress
    
    def update_from_quiz(self, user_id, subtopic_id, score, passed, item_responses=None, difficulty="beginner"):
        """
        Update user progress using Bayesian Knowledge Tracing (BKT) sequential updates.
        
        Args:
            user_id: int
            subtopic_id: int
            score: float (0-100)
            passed: bool
            item_responses: list of dicts [{'is_correct': bool, 'difficulty': str}, ...] or list of bools
            difficulty: str ("beginner", "intermediate", "advanced") default fallback
        """
        progress = self.get_or_create_progress(user_id, subtopic_id)
        
        # Update quiz stats
        progress.quiz_attempts += 1
        progress.last_score = score
        
        if score > progress.best_score:
            progress.best_score = score

        # Bayesian Knowledge Tracing Probability Updating
        current_mastery = progress.knowledge_level if progress.knowledge_level > 0 else self.DEFAULT_P_INIT
        
        if item_responses and isinstance(item_responses, list) and len(item_responses) > 0:
            # Sequential BKT update per question item
            for item in item_responses:
                if isinstance(item, dict):
                    is_correct = bool(item.get("is_correct", False))
                    item_diff = item.get("difficulty", difficulty)
                else:
                    is_correct = bool(item)
                    item_diff = difficulty
                current_mastery = self.update_bkt_step(current_mastery, is_correct, difficulty=item_diff)
        else:
            # Aggregate score estimation: simulate item responses according to total score percentage
            total_items = 5
            correct_items = int(round((score / 100.0) * total_items))
            for i in range(total_items):
                is_correct = (i < correct_items)
                current_mastery = self.update_bkt_step(current_mastery, is_correct, difficulty=difficulty)

        progress.knowledge_level = min(1.0, max(0.0, current_mastery))
        progress.confidence = min(1.0, score / 100.0)

        if passed and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        
        progress.last_accessed = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return progress
    
    def apply_forgetting_curve(self, user_id):
        """
        Apply forgetting curve to all user's progress records
        Knowledge decays over time if not practiced
        """
        all_progress = UserProgress.query.filter_by(user_id=user_id).all()
        
        updated_count = 0
        for progress in all_progress:
            if progress.last_accessed:
                days_since = (datetime.utcnow() - progress.last_accessed).days
                
                if days_since > 0 and progress.knowledge_level > 0:
                    # Exponential decay
                    decay_factor = np.exp(-self.forgetting_rate * days_since)
                    old_level = progress.knowledge_level
                    progress.knowledge_level *= decay_factor
                    
                    if abs(old_level - progress.knowledge_level) > 0.01:
                        updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
        
        return updated_count
    
    def get_progress_summary(self, user_id):
        """Get overall progress summary for user"""
        all_progress = UserProgress.query.filter_by(user_id=user_id).all()
        
        if not all_progress:
            return {
                'total_unlocked': 0,
                'total_completed': 0,
                'average_knowledge': 0.0,
                'average_score': 0.0,
                'weak_areas': [],
                'strong_areas': []
            }
        
        unlocked = [p for p in all_progress if p.is_unlocked]
        completed = [p for p in all_progress if p.is_completed]
        
        avg_knowledge = sum(p.knowledge_level for p in all_progress) / len(all_progress)
        avg_score = sum(p.best_score for p in all_progress if p.best_score > 0) / len([p for p in all_progress if p.best_score > 0]) if any(p.best_score > 0 for p in all_progress) else 0
        
        # Identify weak and strong areas
        weak_areas = []
        strong_areas = []
        
        for progress in all_progress:
            if progress.quiz_attempts > 0:
                subtopic = Subtopic.query.get(progress.subtopic_id)
                if subtopic:
                    topic = subtopic.topic
                    course = topic.course
                    
                    if progress.best_score < 50:
                        weak_areas.append({
                            'subtopic_id': subtopic.id,
                            'subtopic_name': subtopic.name,
                            'topic_name': topic.name,
                            'course_name': course.name,
                            'score': progress.best_score,
                            'attempts': progress.quiz_attempts
                        })
                    elif progress.best_score >= 90:
                        strong_areas.append({
                            'subtopic_id': subtopic.id,
                            'subtopic_name': subtopic.name,
                            'topic_name': topic.name,
                            'course_name': course.name,
                            'score': progress.best_score
                        })
        
        return {
            'total_unlocked': len(unlocked),
            'total_completed': len(completed),
            'average_knowledge': round(avg_knowledge, 2),
            'average_score': round(avg_score, 1),
            'weak_areas': sorted(weak_areas, key=lambda x: x['score'])[:5],
            'strong_areas': sorted(strong_areas, key=lambda x: x['score'], reverse=True)[:5]
        }
    
    def get_next_subtopic_to_learn(self, user_id):
        """Get the next recommended subtopic to learn"""
        # Find first unlocked but not completed subtopic
        progress_records = UserProgress.query.filter_by(
            user_id=user_id,
            is_unlocked=True,
            is_completed=False
        ).all()
        
        if not progress_records:
            return None
        
        # Get the subtopic with lowest combined order (course > topic > subtopic)
        best_subtopic = None
        min_order = float('inf')
        
        for progress in progress_records:
            subtopic = Subtopic.query.get(progress.subtopic_id)
            if subtopic:
                topic = subtopic.topic
                course = topic.course
                
                # Calculate combined order for proper sequencing
                combined_order = (course.order_index * 10000) + (topic.order_index * 100) + subtopic.order_index
                
                if combined_order < min_order:
                    min_order = combined_order
                    best_subtopic = subtopic
        
        return best_subtopic
    
    def get_review_recommendations(self, user_id, limit=5):
        """Get subtopics that need review (completed but knowledge decaying)"""
        all_progress = UserProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()
        
        review_needed = []
        
        for progress in all_progress:
            if progress.last_accessed:
                days_since = (datetime.utcnow() - progress.last_accessed).days
                
                # If it's been a while and knowledge is dropping
                if days_since > 7 and progress.knowledge_level < 0.8:
                    subtopic = Subtopic.query.get(progress.subtopic_id)
                    if subtopic:
                        topic = subtopic.topic
                        course = topic.course
                        
                        priority = days_since * (1 - progress.knowledge_level)
                        
                        review_needed.append({
                            'subtopic_id': subtopic.id,
                            'subtopic_name': subtopic.name,
                            'topic_name': topic.name,
                            'course_name': course.name,
                            'days_since_practice': days_since,
                            'knowledge_level': progress.knowledge_level,
                            'priority': priority
                        })
        
        # Sort by priority
        review_needed.sort(key=lambda x: x['priority'], reverse=True)
        
        return review_needed[:limit]
    
    def get_statistics(self, user_id):
        """Get detailed statistics for user"""
        all_progress = UserProgress.query.filter_by(user_id=user_id).all()
        
        total_quiz_attempts = sum(p.quiz_attempts for p in all_progress)
        total_time_spent = 0  # Could be calculated from learning sessions
        
        # Get quiz attempts
        total_questions_answered = QuizAttempt.query.filter_by(user_id=user_id).count()
        correct_answers = QuizAttempt.query.filter_by(user_id=user_id, is_correct=True).count()
        
        accuracy = (correct_answers / total_questions_answered * 100) if total_questions_answered > 0 else 0
        
        return {
            'total_subtopics_unlocked': len([p for p in all_progress if p.is_unlocked]),
            'total_subtopics_completed': len([p for p in all_progress if p.is_completed]),
            'total_quiz_attempts': total_quiz_attempts,
            'total_questions_answered': total_questions_answered,
            'overall_accuracy': round(accuracy, 1),
            'average_knowledge_level': round(sum(p.knowledge_level for p in all_progress) / len(all_progress) if all_progress else 0, 2)
        }