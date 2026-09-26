"""
Database seeding service for initial curriculum, demo students, and admin accounts.
"""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from models import db, User, Course, Topic, Subtopic, UserProgress

def create_topics_and_subtopics(course_id, topics_data):
    """Helper function to create topics and subtopics for a course"""
    for topic_index, topic_data in enumerate(topics_data, start=1):
        topic = Topic(
            course_id=course_id,
            name=topic_data['name'],
            description=topic_data['description'],
            order_index=topic_index
        )
        db.session.add(topic)
        db.session.flush()
        
        for subtopic_index, subtopic_data in enumerate(topic_data['subtopics'], start=1):
            subtopic = Subtopic(
                topic_id=topic.id,
                name=subtopic_data['name'],
                description=subtopic_data['description'],
                order_index=subtopic_index,
                passing_score=70
            )
            db.session.add(subtopic)

def init_database_data():
    """Initializes tables and seeds baseline admin, students, and Python curriculum"""
    db.create_all()
    
    # 1. Admin User
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user is None:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('password123'),
            role='admin',
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()

    # 2. Sample Students
    if User.query.filter_by(role='student').count() == 0:
        sample_students = [
            {'username': 'alex_student', 'email': 'alex@example.com', 'xp': 250, 'current_streak': 3},
            {'username': 'sarah_learner', 'email': 'sarah@example.com', 'xp': 480, 'current_streak': 5},
            {'username': 'john_coder', 'email': 'john@example.com', 'xp': 120, 'current_streak': 1},
        ]
        for s in sample_students:
            s_user = User(
                username=s['username'],
                email=s['email'],
                password_hash=generate_password_hash('password123'),
                role='student',
                is_verified=True,
                xp=s['xp'],
                current_streak=s['current_streak'],
                has_completed_preassessment=True
            )
            db.session.add(s_user)
        db.session.commit()

        first_subtopic = Subtopic.query.order_by(Subtopic.order_index).first()
        if first_subtopic:
            for student in User.query.filter_by(role='student').all():
                existing_p = UserProgress.query.filter_by(user_id=student.id, subtopic_id=first_subtopic.id).first()
                if not existing_p:
                    p = UserProgress(
                        user_id=student.id,
                        subtopic_id=first_subtopic.id,
                        is_unlocked=True,
                        is_completed=True,
                        best_score=85,
                        knowledge_level=0.75,
                        started_at=datetime.now(timezone.utc),
                        completed_at=datetime.now(timezone.utc),
                        last_accessed=datetime.now(timezone.utc)
                    )
                    db.session.add(p)
            db.session.commit()

    # 3. Comprehensive Course Curriculum
    if Course.query.count() == 0:
        print("Creating comprehensive course structure...")
        
        # Course 1: Python Basics
        python_course = Course(
            name="Python Basics",
            description="Complete introduction to Python programming",
            difficulty="beginner",
            order_index=1
        )
        db.session.add(python_course)
        db.session.flush()
        
        python_topics = [
            {
                'name': 'Variables and Data Types',
                'description': 'Learn about variables, data types, and basic operations',
                'subtopics': [
                    {'name': 'Introduction to Variables', 'description': 'What are variables and how to use them'},
                    {'name': 'Numeric Data Types', 'description': 'Integers, floats, and complex numbers'},
                    {'name': 'Strings and Text', 'description': 'Working with strings and text data'},
                    {'name': 'Type Conversion', 'description': 'Converting between different data types'},
                ]
            },
            {
                'name': 'Control Flow',
                'description': 'Conditional statements and loops',
                'subtopics': [
                    {'name': 'If-Else Statements', 'description': 'Making decisions in code'},
                    {'name': 'For Loops', 'description': 'Iterating with for loops'},
                    {'name': 'While Loops', 'description': 'Conditional iteration'},
                    {'name': 'Loop Control', 'description': 'Break, continue, and pass statements'},
                ]
            },
            {
                'name': 'Functions',
                'description': 'Creating and using functions',
                'subtopics': [
                    {'name': 'Defining Functions', 'description': 'How to create functions'},
                    {'name': 'Function Parameters', 'description': 'Passing arguments to functions'},
                    {'name': 'Return Values', 'description': 'Getting values back from functions'},
                    {'name': 'Lambda Functions', 'description': 'Anonymous functions'},
                ]
            },
            {
                'name': 'Data Structures',
                'description': 'Lists, tuples, dictionaries, and sets',
                'subtopics': [
                    {'name': 'Lists', 'description': 'Working with lists'},
                    {'name': 'Tuples', 'description': 'Immutable sequences'},
                    {'name': 'Dictionaries', 'description': 'Key-value pairs'},
                    {'name': 'Sets', 'description': 'Unique collections'},
                ]
            },
        ]
        
        create_topics_and_subtopics(python_course.id, python_topics)
        db.session.commit()
        print("✅ Course structure created successfully!")
