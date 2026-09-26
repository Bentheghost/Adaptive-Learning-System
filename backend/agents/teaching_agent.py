"""
Teaching Agent - Simplified version for debugging
"""
from agents.base_agent import BaseAgent
from llm_service import LLMService
from datetime import datetime

class TeachingAgent(BaseAgent):
    """Generate lessons and reviews"""
    
    def __init__(self):
        super().__init__("TA-001", "TeachingAgent")
        self.llm_service = LLMService()
        self.lessons_generated = 0
        
    def perceive(self, environment):
        """Perceive student state"""
        self.update_state("perceiving")
        print(f"[TeachingAgent] Perceiving environment...")
        
        self.user_id = environment.get('user_id')
        self.subtopic_id = environment.get('subtopic_id')
        self.subtopic_name = environment.get('subtopic_name', 'Unknown Topic')
        self.knowledge_level = environment.get('knowledge_level', 0.5)
        self.is_review = environment.get('is_review', False)
        self.quiz_score = environment.get('quiz_score', 0)
        
        print(f"[TeachingAgent] Topic: {self.subtopic_name}, Review: {self.is_review}")
        
        return self
    
    def decide(self):
        """Decide teaching approach"""
        self.update_state("deciding")
        
        try:
            quiz_score_val = float(self.quiz_score or 0.0)
        except (ValueError, TypeError):
            quiz_score_val = 0.0
            
        try:
            knowledge_val = float(self.knowledge_level or 0.0)
        except (ValueError, TypeError):
            knowledge_val = 0.0
            
        if self.is_review:
            if quiz_score_val < 50:
                self.lesson_complexity = "beginner"
                self.example_count = 4
            elif quiz_score_val < 70:
                self.lesson_complexity = "beginner"
                self.example_count = 3
            else:
                self.lesson_complexity = "intermediate"
                self.example_count = 2
        else:
            if knowledge_val < 0.3:
                self.lesson_complexity = "beginner"
                self.example_count = 3
            elif knowledge_val < 0.7:
                self.lesson_complexity = "intermediate"
                self.example_count = 2
            else:
                self.lesson_complexity = "intermediate"
                self.example_count = 1
        
        print(f"[TeachingAgent] Complexity: {self.lesson_complexity}, Examples: {self.example_count}")
        
        return self
    
    def act(self):
        """Generate lesson"""
        self.update_state("acting")
        
        try:
            print(f"[TeachingAgent] Starting content generation...")
            
            if self.is_review:
                return self._generate_review()
            else:
                return self._generate_lesson()
                
        except Exception as e:
            print(f"[TeachingAgent] ERROR in act(): {str(e)}")
            import traceback
            traceback.print_exc()
            self.update_state("error")
            return {
                "error": str(e),
                "content": self._get_fallback_content()
            }
    
    def _generate_lesson(self):
        """Generate curriculum-aligned tier specific HTML lesson"""
        print(f"[TeachingAgent] Generating lesson for: {self.subtopic_name} at tier: {self.lesson_complexity}")
        
        # 🎯 FIX: Do not pass a custom_prompt parameter string override here.
        # Let the LLMService use its default prompt logic, but append your specific HTML structure guidelines to it!
        try:
          print("[TeachingAgent] Calling LLM service...")
          
          content = self.llm_service.generate_lesson_with_prompt(
              topic_name=self.subtopic_name,
              difficulty=self.lesson_complexity,
              knowledge_level=self.knowledge_level,
              custom_prompt=None  # Allows _default_lesson_prompt to handle milestones!
          )
          
          print(f"[TeachingAgent] LLM returned content length: {len(content) if content else 0}")
          
          if not content:
              print("[TeachingAgent] WARNING: LLM returned empty content, using fallback")
              content = self._get_fallback_content()
          
          self.lessons_generated += 1
          print(f"[TeachingAgent] [OK] Lesson generated (Total: {self.lessons_generated})")
          
          self.update_state("completed")
          
          return {
              "content": content,
              "metadata": {
                  "complexity": self.lesson_complexity,
                  "agent": self.name,
                  "generated_at": datetime.utcnow().isoformat()
              }
          }
          
        except Exception as e:
          print(f"[TeachingAgent] [ERROR] Error in _generate_lesson: {str(e)}")
          return {
              "content": self._get_fallback_content(),
              "metadata": {"fallback": True, "error": str(e)}
          }

    def _generate_review(self):
        """Generate curriculum-aligned adaptive HTML review"""
        print(f"[TeachingAgent] Generating review for: {self.subtopic_name}, score: {self.quiz_score}%")
        
        try:
          print("[TeachingAgent] Calling LLM for review...")
          
          # 🎯 FIX: Let review modes tap into the curriculum guidelines safely
          content = self.llm_service.generate_lesson_with_prompt(
              topic_name=self.subtopic_name,
              difficulty=self.lesson_complexity,
              knowledge_level=self.quiz_score / 100,
              custom_prompt=None
          )
          
          print(f"[TeachingAgent] Review content length: {len(content) if content else 0}")
          
          if not content:
              content = self._get_fallback_content()
          
          print(f"[TeachingAgent] [OK] Review generated")
          
          return {
              "content": content,
              "metadata": {
                  "review_type": "adaptive",
                  "quiz_score": self.quiz_score,
                  "agent": self.name
              }
          }
          
        except Exception as e:
          print(f"[TeachingAgent] [ERROR] Error in _generate_review: {str(e)}")
          return {
              "content": self._get_fallback_content(),
              "metadata": {"fallback": True, "error": str(e)}
          }
    
    def _get_fallback_content(self):
        """Fallback content when everything fails"""
        return f"""
<div class="lesson-header">
<h2>📚 {self.subtopic_name}</h2>
</div>

<div class="lesson-section">
<h3>🎯 Introduction</h3>
<p>Welcome to the lesson on <strong>{self.subtopic_name}</strong>. This is an important concept in programming.</p>
</div>

<div class="lesson-section">
<h3>💡 Core Concepts</h3>
<p>Understanding {self.subtopic_name} will help you:</p>
<ul>
<li>Write better code</li>
<li>Solve problems more effectively</li>
<li>Build on foundational knowledge</li>
</ul>
</div>

<div class="lesson-section">
<h3>💻 Example</h3>
<pre><code class="language-python">
# Basic example of {self.subtopic_name}
def example():
    # Your code here
    result = "Hello, World!"
    return result

# Test the function
output = example()
print(output)
</code></pre>
<p>This example demonstrates the basic usage of {self.subtopic_name}.</p>
</div>

<div class="lesson-section key-takeaways">
<h3>🔑 Key Takeaways</h3>
<ul>
<li>Understanding {self.subtopic_name} is essential</li>
<li>Practice regularly to improve</li>
<li>Apply concepts to real projects</li>
</ul>
</div>

<p><em>Note: This is a simplified lesson. The AI-generated content will be more detailed.</em></p>
"""
    
    def get_statistics(self):
        """Return agent statistics"""
        return {
            "agent": self.name,
            "lessons_generated": self.lessons_generated,
            "state": self.state
        }