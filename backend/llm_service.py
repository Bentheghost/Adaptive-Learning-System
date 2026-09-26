from google import genai  # Updated to the modern SDK
from google.genai import types  # Import configuration types
from config import Config
import json
import time
from pydantic import BaseModel, Field
from typing import List, Dict, TypedDict

# ============ STRUCTURED OUTPUT SCHEMAS (TypedDict Mode) ============

class QuizQuestionSchema(TypedDict):
    question: str
    options: Dict[str, str]  # Expects keys: 'A', 'B', 'C', 'D'
    correct_answer: str     # Expects: 'A', 'B', 'C', or 'D'
    explanation: str

class QuizSchema(TypedDict):
    questions: List[QuizQuestionSchema]

# ============ MAIN LLM SERVICE OBJECT ============

class LLMService:
    def __init__(self):
        # Initialize the modern client using your configured API key
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = 'gemini-flash-lite-latest'
        
        # Set up the generation config using the new SDK format
        self.generation_config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192
        )
    
    def _generate_with_retry(self, model, contents, config, max_retries=3):
        import time
        for attempt in range(max_retries):
            try:
                return self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                error_str = str(e)
                if '503' in error_str or '429' in error_str or 'UNAVAILABLE' in error_str.upper():
                    if attempt < max_retries - 1:
                        sleep_time = (attempt + 1) * 2  # 2s, 4s
                        print(f"[LLMService] [WARN] API overloaded (503). Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                        continue
                raise e

    # ============ AGENT-COMPATIBLE METHODS ============
    
    def generate_lesson_with_prompt(self, topic_name, difficulty, knowledge_level, custom_prompt=None):
        """
        Generate lesson with custom prompt (for Teaching Agent)
        """
        try:
            from models import db, CachedLesson
            tolerance = 0.15
            cached = CachedLesson.query.filter_by(
                topic_name=topic_name,
                difficulty=difficulty
            ).filter(
                CachedLesson.knowledge_level.between(knowledge_level - tolerance, knowledge_level + tolerance)
            ).first()
            
            if cached:
                print(f"[LLMService] [CACHE HIT] for lesson: {topic_name} at {difficulty}")
                return cached.content
        except Exception as e:
            print(f"[LLMService] Cache read error: {e}")

        if custom_prompt:
            prompt = custom_prompt
        else:
            # Use default prompt structure
            prompt = self._default_lesson_prompt(topic_name, difficulty, knowledge_level)
        
        try:
            # Updated to use the modern client.models.generate_content layout
            response = self._generate_with_retry(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            try:
                from models import db, CachedLesson
                new_cache = CachedLesson(
                    topic_name=topic_name,
                    difficulty=difficulty,
                    knowledge_level=knowledge_level,
                    content=response.text
                )
                db.session.add(new_cache)
                db.session.commit()
                print(f"[LLMService] [CACHE] Saved new lesson to cache")
            except Exception as e:
                db.session.rollback()
                print(f"[LLMService] Cache write error: {e}")

            return response.text # Ensure it returns the text property cleanly
        except Exception as e:
            print(f"Error generating lesson: {e}")
            return self._get_fallback_lesson(topic_name, difficulty)
    
    def generate_quiz_with_prompt(self, topic_name, num_questions, difficulty='intermediate', custom_prompt=None):
        """
        Generate quiz with custom prompt (for Assessment Agent)
        Bypasses enterprise flags while guaranteeing bulletproof JSON structural generation rules.
        """
        try:
            from models import db, CachedQuizQuestion
            import json, random
            
            cached_qs = CachedQuizQuestion.query.filter_by(
                topic_name=topic_name,
                difficulty=difficulty
            ).all()
            
            if len(cached_qs) >= num_questions:
                print(f"[LLMService] [CACHE HIT] for quiz: {topic_name} ({num_questions} qs)")
                selected = random.sample(cached_qs, num_questions)
                return [json.loads(q.question_json) for q in selected]
        except Exception as e:
            print(f"[LLMService] Cache read error: {e}")

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._default_quiz_prompt(topic_name, num_questions, difficulty)
        
        try:
            import random
            
            # Pure manual JSON Schema definition to prevent Pydantic from adding 'additionalProperties: False'
            json_schema_definition = {
                "type": "OBJECT",
                "properties": {
                    "questions": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "question": {"type": "STRING"},
                                "options": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "A": {"type": "STRING"},
                                        "B": {"type": "STRING"},
                                        "C": {"type": "STRING"},
                                        "D": {"type": "STRING"}
                                    },
                                    "required": ["A", "B", "C", "D"]
                                },
                                "correct_answer": {"type": "STRING"},
                                "explanation": {"type": "STRING"}
                            },
                            "required": ["question", "options", "correct_answer", "explanation"]
                        }
                    }
                },
                "required": ["questions"]
            }
            
            # Pass our dictionary directly as a structural generation constraint
            structured_config = types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=json_schema_definition
            )
            
            response = self._generate_with_retry(
                model=self.model_name,
                contents=f"Generate {num_questions} multiple-choice quiz questions based on this topic criteria: {topic_name}. Context guidance: {prompt}",
                config=structured_config
            )
            
            parsed_data = json.loads(response.text.strip())
            questions = parsed_data.get("questions", [])
            
            # --- Dynamic Option Scrambling Loop ---
            if isinstance(questions, list):
                for q in questions:
                    old_correct_key = q.get("correct_answer")
                    if not old_correct_key or "options" not in q:
                        continue
                        
                    correct_value = q["options"].get(old_correct_key)
                    
                    # Convert options to list and shuffle
                    options_list = list(q["options"].values())
                    random.shuffle(options_list)
                    
                    q["options"] = options_list
                    # Set correct_answer to the actual text string to match frontend expectations
                    q["correct_answer"] = correct_value
            
            try:
                from models import db, CachedQuizQuestion
                import json
                for q in questions:
                    new_q = CachedQuizQuestion(
                        topic_name=topic_name,
                        difficulty=difficulty,
                        question_json=json.dumps(q)
                    )
                    db.session.add(new_q)
                db.session.commit()
                print(f"[LLMService] [CACHE] Saved {len(questions)} new questions to cache pool")
            except Exception as e:
                db.session.rollback()
                print(f"[LLMService] Cache write error: {e}")
                
            return questions
                
        except Exception as e:
            print(f"[ERROR] generate_quiz_with_prompt structural failure: {str(e)}")
            return self._get_fallback_quiz(topic_name, 'intermediate', num_questions)
    
    def generate_hint_with_context(self, question, context, hint_level='moderate'):
        """
        Generate hint with specific context (for Tutor Agent)
        """
        challenge = context.get('challenge', '')
        attempt_count = context.get('attempt_count', 1)
        
        hint_instructions = {
            'subtle': 'Provide a gentle nudge without revealing the solution. Ask guiding questions.',
            'moderate': 'Explain the concept and provide a partial solution or approach.',
            'detailed': 'Provide clear explanation with example code, but encourage student to try.'
        }
        
        prompt = f"""
        You are a supportive programming tutor.
        
        STUDENT CONTEXT:
        - Question: {question}
        - Challenge: {challenge}
        - Previous attempts: {attempt_count}
        
        INSTRUCTIONS:
        {hint_instructions.get(hint_level, hint_instructions['moderate'])}
        
        Be encouraging and educational. Keep response 2-4 sentences.
        """
        
        try:
            response = self._generate_with_retry(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error generating hint: {e}")
            return "Think about what you've learned. Break the problem into smaller steps!"

    def generate_chat_response(self, message, history=None):
        """
        Generate response for the global Tutor Chatbot using conversation history.
        """
        history_text = ""
        if history:
            history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
        
        prompt = f"""
        You are an AI Programming Tutor for an adaptive e-learning platform.
        Be encouraging, concise, and educational. Do not just give answers to coding questions; guide the student.
        
        CONVERSATION HISTORY:
        {history_text}
        
        Student: {message}
        Tutor:
        """
        
        try:
            response = self._generate_with_retry(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "I'm sorry, I'm having trouble connecting right now. Could you ask that again later?"
    
    # ============ LEGACY METHODS (Still supported) ============
    
    def generate_lesson(self, topic_name, difficulty, knowledge_level):
        """
        Generate personalized lesson content (Legacy method)
        """
        return self.generate_lesson_with_prompt(
            topic_name, 
            difficulty, 
            knowledge_level, 
            custom_prompt=None
        )
    
    def generate_quiz_questions(self, topic_name, difficulty, num_questions=5):
        """
        Generate quiz questions for a topic (Legacy method)
        """
        prompt = self._default_quiz_prompt(topic_name, num_questions)
        return self.generate_quiz_with_prompt(topic_name, num_questions, prompt)
    
    def explain_answer(self, question, user_answer, correct_answer, topic):
        """
        Generate explanation for why an answer is correct/incorrect
        """
        import hashlib
        hash_str = f"{question}|{user_answer}|{correct_answer}".encode('utf-8')
        q_hash = hashlib.sha256(hash_str).hexdigest()
        
        try:
            from models import db, CachedExplanation
            cached = CachedExplanation.query.filter_by(question_hash=q_hash).first()
            if cached:
                print(f"[LLMService] [CACHE HIT] for explanation")
                return cached.explanation
        except Exception as e:
            print(f"[LLMService] Cache read error: {e}")

        prompt = f"""
        Topic: {topic}
        Question: {question}
        Student's Answer: {user_answer}
        Correct Answer: {correct_answer}
        
        Provide a clear, encouraging explanation (2-3 sentences) about:
        1. Why the correct answer is right
        2. If wrong, what misconception the student might have
        3. A tip to remember this concept
        
        Be supportive and educational.
        """
        
        try:
            response = self._generate_with_retry(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            try:
                from models import db, CachedExplanation
                new_exp = CachedExplanation(question_hash=q_hash, explanation=response.text)
                db.session.add(new_exp)
                db.session.commit()
                print(f"[LLMService] [CACHE] Saved new explanation to cache")
            except Exception as e:
                db.session.rollback()
                print(f"[LLMService] Cache write error: {e}")
                
            return response.text
        except Exception as e:
            print(f"Error generating explanation: {e}")
            if user_answer == correct_answer:
                return f"Correct! The answer {correct_answer} demonstrates your understanding of {topic}."
            else:
                return f"The correct answer is {correct_answer}. Review the key concepts of {topic} to strengthen your understanding."
    
    def generate_study_tips(self, weak_topics, strong_topics):
        """
        Generate personalized study recommendations
        """
        weak_str = ', '.join(weak_topics) if weak_topics else 'None'
        strong_str = ', '.join(strong_topics) if strong_topics else 'None'
        
        prompt = f"""
        Based on a student's performance:
        
        Weak areas: {weak_str}
        Strong areas: {strong_str}
        
        Provide 3-5 personalized, actionable study tips.
        
        FORMATTING RULES:
        - Start each tip with a dash (-)
        - Keep each tip to 2-3 sentences
        - Use **bold** for key terms
        - Be specific and encouraging
        - Make tips actionable
        
        Format as simple bullet points with dashes.
        """
        
        try:
            response = self._generate_with_retry(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error generating tips: {e}")
            return "- Practice regularly with focused study sessions\n- Review weak topics daily\n- Build on your strengths\n- Take breaks to avoid burnout\n- Track your progress"
    
    # ============ PRIVATE HELPER METHODS ============
    
    def _default_quiz_prompt(self, topic_name, num_questions, difficulty='intermediate'):
        """Default quiz prompt structure"""
        return f"""
        Generate {num_questions} multiple-choice questions on "{topic_name}" at {difficulty} level.
        
        For each question, provide:
        1. The question
        2. Four options (A, B, C, D)
        3. The correct answer (letter only: A, B, C, or D)
        4. A brief explanation
        """

    def _default_lesson_prompt(self, topic_name, difficulty, knowledge_level):
        """Default lesson prompt structure with curriculum alignment safeguards"""
        
        # Inject explicit sub-concepts to guarantee lesson matches the requested difficulty and topic
        tone_and_depth = ""
        if difficulty == "beginner":
            tone_and_depth = (
                "- Focus on foundational definitions and basic syntax.\n"
                "- Use simple, encouraging, and accessible language.\n"
                "- Keep examples very simple and isolated to the core concept."
            )
        elif difficulty == "intermediate":
            tone_and_depth = (
                "- Focus on behavioral properties, common edge cases, and best practices.\n"
                "- Assume basic understanding and use proper technical terminology.\n"
                "- Provide more complex examples that show typical use cases and standard conventions."
            )
        elif difficulty == "advanced":
            tone_and_depth = (
                "- Explore under-the-hood mechanics, memory management, and performance implications if applicable.\n"
                "- Assume highly proficient knowledge and dive deep into complex architectures.\n"
                "- Use complex, real-world examples and advanced patterns."
            )

        return f"""
        Create a comprehensive lesson on "{topic_name}" for a student at {difficulty} level 
        with current knowledge level of {knowledge_level*100:.0f}%.
        
        CRITICAL CONTENT BOUNDS:
        To prepare the student for upcoming adaptive testing assessments, you MUST ensure the lesson is perfectly suited for a {difficulty} level student by following these guidelines:
        {tone_and_depth}
        
        Structure the lesson as follows:
        
        ## Introduction
        Brief overview (2-3 sentences)
        
        ## Core Concepts
        Main ideas explained clearly with examples
        
        ## Practical Examples
        Real code or scenarios (use proper formatting)
        
        ## Real-World Applications
        Where this is used in industry
        
        ## Key Takeaways
        3-5 bullet points summarizing main ideas
        
        ## Practice Challenge
        ONE simple coding exercise that students can solve.
        Format: "Write a Python program that [task description]. Expected output: [example]"
        Make it achievable for {difficulty} level students.
        
        FORMATTING RULES:
        - Return ONLY valid, clean HTML code wrapped inside structured divs matching these targets:
          * Wrap headers in `<div class="lesson-header"><h2>...</h2></div>`
          * Wrap each module topic block in `<div class="lesson-section"><h3>...</h3><p>...</p></div>`
          * Wrap key takeaways inside `<div class="lesson-section key-takeaways"><h3>🔑 Key Takeaways</h3><ul>...</ul></div>`
        - Keep paragraphs SHORT (2-3 sentences max)
        - Use code blocks wrapped inside `<pre><code class="language-python">...</code></pre>` for syntax examples.
        - Do NOT wrap your layout inside markdown backticks (e.g., ```html). Return raw text strings.
        """
    
    def _get_fallback_lesson(self, topic_name, difficulty):
        """Fallback lesson content when API fails"""
        return f"""
        <div class="lesson-header">
        <h2>Introduction to {topic_name}</h2>
        </div>
        <div class="lesson-section">
        <p>Welcome to this {difficulty} level lesson on {topic_name}. This is an important topic that will help you build your knowledge.</p>
        <h3>Core Concepts</h3>
        <p>{topic_name} is a fundamental concept that requires understanding and practice. Let's break it down into manageable parts.</p>
        </div>
        <div class="lesson-section key-takeaways">
        <h3>Key Points to Remember</h3>
        <ul>
            <li>Start with the basics and build gradually</li>
            <li>Practice regularly to reinforce learning</li>
            <li>Apply concepts to real-world scenarios</li>
            <li>Review and revise frequently</li>
        </ul>
        </div>
        <p><em>Note: This is a basic lesson. For detailed content, please check your internet connection and API settings.</em></p>
        """
    
    def _get_fallback_quiz(self, topic_name, difficulty, num_questions):
        """Fallback quiz when API fails"""
        fallback_quizzes = {
            "Python Basics": [
                {
                    "question": "What is the correct way to create a list in Python?",
                    "options": [
                        "my_list = [1, 2, 3]",
                        "my_list = (1, 2, 3)",
                        "my_list = {1, 2, 3}",
                        "my_list = <1, 2, 3>"
                    ],
                    "correct_answer": "my_list = [1, 2, 3]",
                    "explanation": "Lists in Python are created using square brackets [].",
                    "difficulty": "beginner",
                    "topic_area": "Data Structures"
                },
                {
                    "question": "What does the len() function return?",
                    "options": [
                        "The length of a string or collection",
                        "A random number",
                        "The first element of a list",
                        "The type of an object"
                    ],
                    "correct_answer": "The length of a string or collection",
                    "explanation": "The len() function returns the number of items in an object.",
                    "difficulty": "beginner",
                    "topic_area": "Built-in Functions"
                },
                {
                    "question": "Which keyword is used to define a function in Python?",
                    "options": [
                        "function",
                        "def",
                        "define",
                        "func"
                    ],
                    "correct_answer": "def",
                    "explanation": "The 'def' keyword is used to define a function in Python.",
                    "difficulty": "beginner",
                    "topic_area": "Functions"
                }
            ]
        }
        
        if topic_name in fallback_quizzes:
            return fallback_quizzes[topic_name][:num_questions]
        
        questions = []
        for i in range(min(num_questions, 3)):
            questions.append({
                "question": f"What is a key concept in {topic_name}?",
                "options": [
                    "Concept A",
                    "Concept B",
                    "Concept C",
                    "Concept D"
                ],
                "correct_answer": "Concept A",
                "explanation": f"This is a fallback question for {topic_name}. The API may be experiencing issues."
            })
        return questions

    def identify_misconception(self, question, user_answer, correct_answer):
        """Identifies why a user might have chosen a specific wrong answer"""
        prompt = f"""
        A student answered a multiple-choice programming question incorrectly.
        
        Question: {question}
        Correct Answer: {correct_answer}
        Student's Wrong Answer: {user_answer}
        
        Analyze the student's wrong answer and identify the core misconception in exactly ONE short, concise sentence.
        Do not preach or give the correct answer. Just diagnose the cognitive error.
        Example: "The student confused the assignment operator (=) with the equality operator (==)."
        """
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Error generating misconception: {e}")
            
        return "The student lacks fundamental understanding of this specific concept."