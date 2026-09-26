"""
Recommendation Agent - Autonomous learning path optimization
"""
from agents.base_agent import BaseAgent
from models import db, Topic, Subtopic, UserProgress
from datetime import datetime, timezone

class RecommendationAgent(BaseAgent):
    """
    Autonomous agent responsible for:
    - Suggesting next topics
    - Optimizing learning paths
    - Balancing difficulty
    - Considering prerequisites
    """
    
    def __init__(self):
        super().__init__("RA-001", "RecommendationAgent")
        self.recommendations_made = 0
        self.learning_paths_created = 0
        self.strategy = "foundation_building"
        self.recommendations = []
        
    def perceive(self, environment):
        """
        Perceive student's learning state
        
        Args:
            environment: dict with {
                'user_id': int,
                'current_topic_id': int (optional),
                'goals': list (optional)
            }
        """
        self.update_state("perceiving")
        self.log(f"Perceiving learning context for user {environment.get('user_id')}")
        
        self.user_id = environment.get('user_id')
        self.current_topic_id = environment.get('current_topic_id')
        self.goals = environment.get('goals', [])
        
        # Get all topics and knowledge states from UserProgress
        self.all_topics = Topic.query.all()
        
        progress_records = UserProgress.query.filter_by(user_id=self.user_id).all() if self.user_id else []
        topic_knowledge = {}
        for p in progress_records:
            if p.subtopic and p.subtopic.topic_id:
                tid = p.subtopic.topic_id
                if tid not in topic_knowledge:
                    topic_knowledge[tid] = []
                topic_knowledge[tid].append(p.knowledge_level or 0.0)
                
        self.knowledge_states = {
            tid: (sum(levels) / len(levels) if levels else 0.0)
            for tid, levels in topic_knowledge.items()
        }
        
        self.log(f"Analyzing {len(self.all_topics)} topics, "
                f"{len(self.knowledge_states)} known states")
        
        return self
    
    def decide(self):
        """
        Autonomous decisions:
        - What topic to recommend next?
        - Short-term vs long-term path?
        - Review vs new content?
        """
        self.update_state("deciding")
        
        # Decision 1: Calculate scores for all topics
        topic_scores = []
        
        for topic in self.all_topics:
            if topic.id == self.current_topic_id:
                continue  # Skip current topic
            
            score = self._calculate_topic_score(topic)
            topic_scores.append((topic, score))
        
        # Sort by score
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Decision 2: Choose recommendation strategy
        if len(self.knowledge_states) < 3:
            # New learner - suggest foundation topics
            self.strategy = "foundation_building"
            self.recommendations = [t for t, s in topic_scores 
                                   if getattr(t, 'difficulty', t.course.difficulty if getattr(t, 'course', None) else 'beginner') == 'beginner'][:3]
            if not self.recommendations:
                self.recommendations = [t for t, s in topic_scores[:3]]
        else:
            # Experienced learner - balanced approach
            self.strategy = "balanced_growth"
            self.recommendations = [t for t, s in topic_scores[:5]]
        
        self.log(f"Strategy: {self.strategy}, {len(self.recommendations)} recommendations")
        
        return self
    
    def _calculate_topic_score(self, topic):
        """
        Autonomous scoring algorithm for topic recommendation
        """
        score = 0
        knowledge_level = self.knowledge_states.get(topic.id, 0)
        difficulty = getattr(topic, 'difficulty', topic.course.difficulty if getattr(topic, 'course', None) else 'beginner')
        category = getattr(topic, 'category', topic.course.name if getattr(topic, 'course', None) else 'General')
        prerequisites = getattr(topic, 'prerequisites', None)
        
        # Factor 1: Unstarted topics (high priority for beginners)
        if knowledge_level == 0:
            score += 5
        # Factor 2: In-progress topics
        elif 0 < knowledge_level < 0.7:
            score += 3
        # Factor 3: Mastered topics (low priority)
        elif knowledge_level >= 0.8:
            score += 0.5
        
        # Factor 4: Prerequisites
        if prerequisites:
            prereq_ids = [int(x.strip()) for x in str(prerequisites).split(',') if x.strip()]
            prereqs_met = all(
                self.knowledge_states.get(pid, 0) > 0.6
                for pid in prereq_ids
            )
            
            if prereqs_met:
                score += 3  # Ready to learn
            else:
                score -= 2  # Not ready yet
        else:
            score += 2  # No prerequisites - easier to start
        
        # Factor 5: Difficulty match
        avg_knowledge = sum(self.knowledge_states.values()) / len(self.knowledge_states) if self.knowledge_states else 0
        
        if difficulty == 'beginner' and avg_knowledge < 0.3:
            score += 2
        elif difficulty == 'intermediate' and 0.3 <= avg_knowledge < 0.7:
            score += 2
        elif difficulty == 'advanced' and avg_knowledge >= 0.7:
            score += 2
        
        # Factor 6: Goals alignment
        if self.goals:
            for goal in self.goals:
                if goal.lower() in topic.name.lower() or goal.lower() in category.lower():
                    score += 4
        
        return score
    
    def act(self):
        """
        Execute: Provide recommendations (prioritize same category/course)
        """
        self.update_state("acting")
        self.log("Generating personalized recommendations...")
        
        if not self.recommendations:
            self.log("No suitable recommendations found", "warning")
            self.update_state("completed")
            return {
                "recommendations": [],
                "message": "Great progress! Review previous topics or explore new categories.",
                "agent": self.name
            }
        
        # Build detailed recommendations
        detailed_recommendations = []
        current_category = None
        
        # If current_topic_id exists, prioritize same category
        if self.current_topic_id:
            current_topic = db.session.get(Topic, self.current_topic_id)
            if current_topic:
                current_category = getattr(current_topic, 'category', current_topic.course.name if getattr(current_topic, 'course', None) else 'General')
        
        for topic in self.recommendations:
            knowledge_level = self.knowledge_states.get(topic.id, 0)
            difficulty = getattr(topic, 'difficulty', topic.course.difficulty if getattr(topic, 'course', None) else 'beginner')
            category = getattr(topic, 'category', topic.course.name if getattr(topic, 'course', None) else 'General')
            
            # Generate reason for recommendation
            if knowledge_level == 0:
                reason = "Ready to explore this new topic"
            elif knowledge_level < 0.5:
                reason = "Continue building on your progress"
            elif knowledge_level < 0.8:
                reason = "Almost there! Finish mastering this"
            else:
                reason = "Review to maintain mastery"
            
            # Mark if it's in the same course
            is_same_course = (category == current_category) if current_category else False
            
            detailed_recommendations.append({
                'topic_id': topic.id,
                'name': topic.name,
                'category': category,
                'difficulty': difficulty,
                'current_knowledge': knowledge_level,
                'reason': reason,
                'priority': 'high' if is_same_course else ('medium' if knowledge_level == 0 else 'low'),
                'is_same_course': is_same_course
            })
        
        # Sort: same course first, then by priority
        detailed_recommendations.sort(
            key=lambda x: (not x['is_same_course'], x['priority'] != 'high', x['current_knowledge']),
            reverse=False
        )
        
        self.recommendations_made += 1
        self.log(f"Recommendations generated (Total: {self.recommendations_made})")
        
        # Store in memory
        self.memory.append({
            "action": "recommendations_generated",
            "count": len(detailed_recommendations),
            "strategy": self.strategy,
            "user_id": self.user_id
        })
        
        self.update_state("completed")
        
        return {
            "recommendations": detailed_recommendations,
            "strategy": self.strategy,
            "next_best": detailed_recommendations[0] if detailed_recommendations else None,
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def create_learning_path(self, target_topic_id):
        """
        Autonomous creation of optimal learning path to target topic
        """
        self.update_state("planning")
        self.log(f"Creating learning path to topic {target_topic_id}")
        
        target_topic = db.session.get(Topic, target_topic_id)
        
        if not target_topic:
            return {"error": "Topic not found"}
        
        path = []
        queue = [target_topic]
        visited = set()
        
        while queue:
            topic = queue.pop(0)
            
            if topic.id in visited:
                continue
            
            visited.add(topic.id)
            knowledge_level = self.knowledge_states.get(topic.id, 0)
            
            # Add to path if not mastered
            if knowledge_level < 0.8:
                path.insert(0, {
                    'topic_id': topic.id,
                    'name': topic.name,
                    'current_knowledge': knowledge_level,
                    'estimated_hours': self._estimate_learning_time(topic, knowledge_level)
                })
            
            # Add prerequisites to queue
            if topic.prerequisites:
                prereq_ids = [int(x.strip()) for x in topic.prerequisites.split(',') if x.strip()]
                for pid in prereq_ids:
                    prereq_topic = db.session.get(Topic, pid)
                    if prereq_topic and prereq_topic.id not in visited:
                        queue.append(prereq_topic)
        
        self.learning_paths_created += 1
        self.log(f"Learning path created with {len(path)} steps")
        
        return {
            "path": path,
            "total_topics": len(path),
            "estimated_total_hours": sum(t['estimated_hours'] for t in path),
            "agent": self.name
        }
    
    def _estimate_learning_time(self, topic, current_knowledge):
        """Estimate hours needed based on difficulty and current knowledge"""
        base_hours = {
            'beginner': 3,
            'intermediate': 5,
            'advanced': 8
        }
        
        hours = base_hours.get(topic.difficulty, 5)
        remaining = 1 - current_knowledge
        
        return round(hours * remaining, 1)
    
    def get_statistics(self):
        """Return agent statistics"""
        return {
            "agent": self.name,
            "recommendations_made": self.recommendations_made,
            "learning_paths_created": self.learning_paths_created,
            "current_strategy": self.strategy if hasattr(self, 'strategy') else None,
            "state": self.state,
            "memory_size": len(self.memory)
        }