"""
Assessment Agent - Quiz generation for subtopics
"""
from agents.base_agent import BaseAgent
from datetime import datetime, timezone
import random
from models import QuizQuestion

class AssessmentAgent(BaseAgent):
    """Generate adaptive quizzes for subtopics"""
    
    def __init__(self):
        super().__init__("AA-001", "AssessmentAgent")
        self.quizzes_generated = 0
        from llm_service import LLMService
        self.llm_service = LLMService()
        
    def perceive(self, environment):
        """Perceive quiz context"""
        self.update_state("perceiving")
        self.log(f"Perceiving assessment needs for user {environment.get('user_id')}")
        
        self.user_id = environment.get('user_id')
        self.subtopic_id = environment.get('subtopic_id')
        self.subtopic_name = environment.get('subtopic_name')
        self.knowledge_level = environment.get('knowledge_level', 0.0)
        self.quiz_attempts = environment.get('quiz_attempts', 0)
        self.target_difficulty = environment.get('difficulty')
        
        return self
    
    def decide(self):
        """Decide quiz difficulty"""
        self.update_state("deciding")
        
        # First attempt: easier quiz
        if self.quiz_attempts == 0:
            self.num_questions = 5
        elif self.knowledge_level < 0.3:
            self.num_questions = 5
        elif self.knowledge_level < 0.7:
            self.num_questions = 6
        else:
            self.num_questions = 7
            
        # Use target difficulty if provided, otherwise fallback to adaptive
        if self.target_difficulty:
            self.difficulty_level = self.target_difficulty
        else:
            if self.knowledge_level < 0.3:
                self.difficulty_level = "beginner"
            elif self.knowledge_level < 0.7:
                self.difficulty_level = "intermediate"
            else:
                self.difficulty_level = "advanced"
        
        self.log(f"Quiz: {self.num_questions} questions, {self.difficulty_level} level")
        
        return self
    
    def act(self):
        """Generate quiz dynamically using the LLM for all subtopics"""
        self.update_state("acting")
        self.log(f"Generating {self.num_questions} {self.difficulty_level} questions for subtopic: {self.subtopic_name} (ID: {self.subtopic_id}) via LLM...")
        
        try:
            questions = self.llm_service.generate_quiz_with_prompt(
                topic_name=self.subtopic_name,
                num_questions=self.num_questions,
                difficulty=self.difficulty_level
            )
            
            if not questions:
                self.log("LLM returned empty questions array. Loading standard hardcoded fallback pool.", "error")
                questions = self._generate_fallback_questions()
                
            # Add difficulty tag to all generated questions
            for q in questions:
                if 'difficulty' not in q:
                    q['difficulty'] = self.difficulty_level
                    
        except Exception as e:
            self.log(f"Error generating quiz via LLM: {str(e)}. Loading standard hardcoded fallback pool.", "error")
            questions = self._generate_fallback_questions()
            
        self.quizzes_generated += 1
        
        # Append a historical log to agent memory to preserve your statistics metric tracking
        self.memory.append({
            "action": "quiz_generated",
            "subtopic_name": self.subtopic_name,
            "num_questions": len(questions),
            "user_id": self.user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        self.update_state("completed")
        
        return {
            "questions": questions,
            "metadata": {
                "difficulty": self.difficulty_level,
                "question_count": len(questions),
                "agent": self.name,
                "mode": "llm_generated",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _generate_fallback_questions(self):
        """Generate basic fallback questions if database fails or is blank"""
        return [
            {
                "question": f"What is the main concept of {self.subtopic_name}?",
                "options": [
                    "A fundamental programming concept",
                    "An advanced technique",
                    "A deprecated feature",
                    "None of the above"
                ],
                "correct_answer": "A fundamental programming concept",
                "explanation": "This is a basic question about the topic.",
                "difficulty": "beginner"
            },
            {
                "question": f"Which of the following best describes {self.subtopic_name}?",
                "options": [
                    "It is important for understanding the topic",
                    "It is rarely used",
                    "It is only for experts",
                    "It is obsolete"
                ],
                "correct_answer": "It is important for understanding the topic",
                "explanation": "Understanding this concept is crucial.",
                "difficulty": "beginner"
            },
            {
                "question": f"When would you use {self.subtopic_name}?",
                "options": [
                    "When solving related problems",
                    "Never",
                    "Only in special cases",
                    "It depends on the context"
                ],
                "correct_answer": "It depends on the context",
                "explanation": "Context matters in programming.",
                "difficulty": "intermediate"
            }
        ]
    
    def get_statistics(self):
        return {
            "agent": self.name,
            "quizzes_generated": self.quizzes_generated,
            "state": self.state,
            "total_tasks": len(self.memory)
        }