"""
Seed Advanced Tier Quiz Questions
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, QuizQuestion

def seed_advanced_questions():
    with app.app_context():
        print("\nChecking database model attributes for QuizQuestion...")
        
        text_column = 'question_text'
        if not hasattr(QuizQuestion, 'question_text'):
            for possible_name in ['text', 'content', 'body']:
                if hasattr(QuizQuestion, possible_name):
                    text_column = possible_name
                    break

        advanced_questions = [
            {
                "subtopic_id": 1,
                "question": "Which of the following describes the underlying mechanism of a Python variable assignment like x = [1, 2]?",
                "option_1": "It creates a deeply cloned value segment in separate system stack bounds.",
                "option_2": "It binds a variable name pointer to a mutable object reference in the heap memory segment.",
                "option_3": "It forces immutable value caching directly within primary CPU cash lanes.",
                "option_4": "It statically allocates sequential memory blocks matching an array structure.",
                "correct_answer": "It binds a variable name pointer to a mutable object reference in the heap memory segment.",
                "difficulty": "advanced",
                "explanation": "In Python, variables are names that reference objects residing dynamically in heap memory. Assignment sets the reference pointer, it does not copy values."
            },
            {
                "subtopic_id": 1,
                "question": "What is the primary operational scope behavior of a variable declared inside a Python list comprehension like [val for val in range(3)] in Python 3?",
                "option_1": "The tracking iteration variable leaks globally into the outer enclosing scope boundary.",
                "option_2": "The variable is dynamically bound to the system global frame context.",
                "option_3": "The variable is localized strictly within the temporary function block scope of the comprehension loop.",
                "option_4": "The variable is kept alive within memory pools until a structural system garbage collect cycle completes.",
                "correct_answer": "The variable is localized strictly within the temporary function block scope of the comprehension loop.",
                "difficulty": "advanced",
                "explanation": "Python 3 completely fixed list comprehension variable leaking. The iteration loop variables are bound cleanly inside an independent inline function block scope layer."
            },
            {
                "subtopic_id": 1,
                "question": "How does the Python runtime process variable evaluation namespaces under the standard LEGB structural resolution rule?",
                "option_1": "Global -> Enclosing -> Local -> Built-in",
                "option_2": "Local -> Enclosing -> Global -> Built-in",
                "option_3": "Local -> Built-in -> Global -> Enclosing",
                "option_4": "Built-in -> Global -> Enclosing -> Local",
                "correct_answer": "Local -> Enclosing -> Global -> Built-in",
                "difficulty": "advanced",
                "explanation": "The LEGB rule dictates that the runtime searches scopes sequentially starting locally (L), moving outward to enclosing closures (E), checking global modules (G), and checking built-ins (B) last."
            }
        ]
        
        added_count = 0
        for q_data in advanced_questions:
            filter_kwargs = {text_column: q_data["question"]}
            exists = QuizQuestion.query.filter_by(**filter_kwargs).first()
            
            if not exists:
                new_q = QuizQuestion()
                setattr(new_q, 'subtopic_id', q_data["subtopic_id"])
                setattr(new_q, text_column, q_data["question"])
                setattr(new_q, 'option_1', q_data["option_1"])
                setattr(new_q, 'option_2', q_data["option_2"])
                setattr(new_q, 'option_3', q_data["option_3"])
                setattr(new_q, 'option_4', q_data["option_4"])
                setattr(new_q, 'correct_answer', q_data["correct_answer"])
                setattr(new_q, 'difficulty', q_data["difficulty"])
                setattr(new_q, 'explanation', q_data["explanation"])
                
                db.session.add(new_q)
                added_count += 1
                
        if added_count > 0:
            db.session.commit()
            print(f"\n--- SUCCESS: Successfully populated {added_count} advanced tier questions into your schema! ---\n")
        else:
            print("\nAdvanced tier questions are already registered.\n")

if __name__ == '__main__':
    seed_advanced_questions()
