"""
Knowledge Agent - Autonomous knowledge state management
"""
from agents.base_agent import BaseAgent
from knowledge_tracker import KnowledgeTracker
from models import db, UserProgress
import numpy as np
from datetime import datetime, timedelta

class KnowledgeAgent(BaseAgent):
    """
    Autonomous agent responsible for:
    - Tracking knowledge evolution
    - Predicting future performance
    - Identifying knowledge gaps
    - Suggesting review topics
    """
    
    def __init__(self):
        super().__init__("KA-001", "KnowledgeAgent")
        self.tracker = KnowledgeTracker()
        self.predictions_made = 0
        self.updates_performed = 0
        
    def perceive(self, environment):
        """
        Perceive student's learning state
        
        Args:
            environment: dict with {
                'user_id': int,
                'subtopic_id': int (optional),
                'recent_activities': list
            }
        """
        self.update_state("perceiving")
        self.log(f"Perceiving knowledge state for user {environment.get('user_id')}")
        
        self.user_id = environment.get('user_id')
        self.subtopic_id = environment.get('subtopic_id')
        self.recent_activities = environment.get('recent_activities', [])
        
        # Get all progress records
        self.progress_records = UserProgress.query.filter_by(
            user_id=self.user_id
        ).all()
        
        self.log(f"Found {len(self.progress_records)} progress records")
        
        return self
    
    def decide(self):
        """
        Autonomous decisions:
        - Which subtopics need review?
        - What's the optimal learning path?
        - Are there knowledge gaps?
        """
        self.update_state("deciding")
        
        # Decision 1: Apply forgetting curves
        topics_needing_review = []
        for progress in self.progress_records:
            if progress.last_accessed:
                days_since_practice = (datetime.utcnow() - progress.last_accessed).days
                
                if days_since_practice > 7 and progress.knowledge_level > 0.3:
                    topics_needing_review.append({
                        'subtopic_id': progress.subtopic_id,
                        'days_since': days_since_practice,
                        'current_level': progress.knowledge_level,
                        'priority': days_since_practice * (1 - progress.knowledge_level)
                    })
        
        # Sort by priority
        topics_needing_review.sort(key=lambda x: x['priority'], reverse=True)
        self.review_recommendations = topics_needing_review[:3]
        
        # Decision 2: Identify knowledge gaps
        self.knowledge_gaps = [
            progress for progress in self.progress_records
            if 0 < progress.knowledge_level < 0.4 and progress.quiz_attempts > 0
        ]
        
        # Decision 3: Predict next knowledge level
        if self.subtopic_id:
            self.predicted_next_level = self._predict_knowledge_growth(self.subtopic_id)
        else:
            self.predicted_next_level = None
        
        self.log(f"Decisions: {len(self.review_recommendations)} topics need review, "
                f"{len(self.knowledge_gaps)} knowledge gaps found")
        
        return self
    
    def _predict_knowledge_growth(self, subtopic_id):
        """Predict knowledge growth based on BKT transition probability P(T)"""
        progress = UserProgress.query.filter_by(
            user_id=self.user_id,
            subtopic_id=subtopic_id
        ).first()
        
        current_level = progress.knowledge_level if progress else self.tracker.DEFAULT_P_INIT
        
        # Determine transition rate P(T) based on learner experience level
        p_trans = 0.10 if (progress and progress.quiz_attempts > 3) else 0.20
        predicted = self.tracker.apply_transition(current_level, p_trans=p_trans)
        
        self.predictions_made += 1
        self.log(f"Predicted BKT knowledge growth: {current_level:.2f} → {predicted:.2f}")
        
        return predicted

    
    def act(self):
        """
        Execute: Update knowledge states and provide recommendations
        """
        self.update_state("acting")
        self.log("Updating knowledge states...")
        
        # Apply forgetting curves
        updated_count = self.tracker.apply_forgetting_curve(self.user_id)
        
        self.updates_performed += updated_count
        self.log(f"Updated {updated_count} knowledge states")
        self.update_state("completed")
        
        return {
            "review_recommendations": self.review_recommendations,
            "knowledge_gaps": [
                {
                    'subtopic_id': gap.subtopic_id,
                    'level': gap.knowledge_level,
                    'confidence': gap.confidence
                }
                for gap in self.knowledge_gaps
            ],
            "predicted_growth": self.predicted_next_level,
            "updated_count": updated_count,
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_statistics(self):
        """Return agent statistics"""
        return {
            "agent": self.name,
            "predictions_made": self.predictions_made,
            "updates_performed": self.updates_performed,
            "state": self.state,
            "memory_size": len(self.memory)
        }