"""
Seed Quiz Question Pool for Section 2 (IDs 5-8)
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from models import db, QuizQuestion

section_2_pool = [
    # ID 5: If-Else Statements
    {
        "subtopic_id": 5,
        "difficulty": "beginner",
        "question_text": "Which keyword is used in Python to test a secondary conditional expression if the initial 'if' statement evaluates to False?",
        "options": ["else if", "elseif", "elif", "otherwise"],
        "correct_answer": "elif",
        "explanation": "Python uses 'elif' (short for else if) to check multiple conditions sequentially after an initial 'if'."
    },
    {
        "subtopic_id": 5,
        "difficulty": "intermediate",
        "question_text": "What happens if multiple conditions evaluate to True within an 'if-elif-else' chain block?",
        "options": [
            "Every single matching True code block executes simultaneously.",
            "Only the first condition that evaluates to True executes; the rest are skipped.",
            "The program crashes immediately and throws a RuntimeCondition Error.",
            "The system defaults strictly to the 'else' fallback block code."
        ],
        "correct_answer": "Only the first condition that evaluates to True executes; the rest are skipped.",
        "explanation": "An if-elif-else structure executes sequentially. As soon as one condition satisfies, its block runs, and the rest of the chain is entirely bypassed."
    },

    # ID 6: For Loops
    {
        "subtopic_id": 6,
        "difficulty": "beginner",
        "question_text": "What is the primary operational focus of a 'for' loop statement block in Python?",
        "options": ["To repeat execution indefinitely until memory crashes", "To iterate across a sequence layout like a list, tuple, or string", "To declare local private variables within a class", "To import multiple external framework objects"],
        "correct_answer": "To iterate across a sequence layout like a list, tuple, or string",
        "explanation": "A for loop in Python is used for iterating over a sequence (such as a list, a tuple, a dictionary, a set, or a string)."
    },
    {
        "subtopic_id": 6,
        "difficulty": "intermediate",
        "question_text": "What sequence values are produced by the native expression: range(1, 5)?",
        "options": ["[1, 2, 3, 4, 5]", "[1, 2, 3, 4]", "[0, 1, 2, 3, 4]", "[2, 3, 4, 5]"],
        "correct_answer": "[1, 2, 3, 4]",
        "explanation": "The range(start, stop) function generates numbers starting from the 'start' value up to, but NOT including, the 'stop' value."
    },

    # ID 7: While Loops
    {
        "subtopic_id": 7,
        "difficulty": "beginner",
        "question_text": "A 'while' loop continues executing its interior block as long as its guiding conditional statement remains:",
        "options": ["False", "True", "Null", "Equal to zero"],
        "correct_answer": "True",
        "explanation": "A while loop repeatedly executes its target block statement as long as the given test condition evaluates to True."
    },
    {
        "subtopic_id": 7,
        "difficulty": "intermediate",
        "question_text": "What critical system error occurs if a 'while' loop conditional tracker statement never evaluates to False?",
        "options": ["An Infinite Loop that runs forever", "A Compilation Syntax Error", "An automatic forced computer restart", "A global variable type change"],
        "correct_answer": "An Infinite Loop that runs forever",
        "explanation": "If the condition of a while loop remains True permanently, the loop never terminates, creating an infinite loop that can freeze or crash the program."
    },

    # ID 8: Loop Control
    {
        "subtopic_id": 8,
        "difficulty": "beginner",
        "question_text": "Which control keyword is used to terminate a loop entirely and jump execution directly out of it?",
        "options": ["continue", "exit", "break", "skip"],
        "correct_answer": "break",
        "explanation": "The 'break' statement terminates the loop containing it immediately. Program control resumes at the next statement outside the loop."
    },
    {
        "subtopic_id": 8,
        "difficulty": "intermediate",
        "question_text": "What does the 'continue' statement do inside a loop structure block?",
        "options": [
            "It ends the loop completely and closes the application execution pipeline.",
            "It skips the rest of the current iteration and jumps directly to the next loop pass.",
            "It restarts the entire loop back from its index zero state.",
            "It pauses execution for a designated number of seconds."
        ],
        "correct_answer": "It skips the rest of the current iteration and jumps directly to the next loop pass.",
        "explanation": "The 'continue' statement rejects all the remaining statements in the current iteration of the loop and moves the control back to the top for the next iteration."
    }
]

def seed_quiz_questions():
    print("Loading Master Question Pool for Section 2 (IDs 5-8)...")
    with app.app_context():
        db.session.query(QuizQuestion).filter(QuizQuestion.subtopic_id.in_([5, 6, 7, 8])).delete(synchronize_session=False)
        for q in section_2_pool:
            db_question = QuizQuestion(
                subtopic_id=q["subtopic_id"],
                difficulty=q["difficulty"],
                question_text=q["question_text"],
                option_1=q["options"][0],
                option_2=q["options"][1],
                option_3=q["options"][2],
                option_4=q["options"][3],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            )
            db.session.add(db_question)
        db.session.commit()
        print("✅ Section 2 (IDs 5-8) successfully loaded and synchronized!")

if __name__ == '__main__':
    seed_quiz_questions()
