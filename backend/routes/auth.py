"""
Authentication and User Session Routes
"""
import os
import re
import random
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course, Topic, Subtopic, UserProgress

auth_bp = Blueprint('auth', __name__)

def get_current_user_id():
    """Extract authenticated user id from session or Authorization Bearer header"""
    if 'user_id' in session:
        return session['user_id']
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if token and token.isdigit():
            return int(token)
    user_id_param = request.args.get('user_id')
    if user_id_param and user_id_param.isdigit():
        return int(user_id_param)
    return None

def check_admin_or_lecturer_auth():
    """Verify that current caller is admin, lecturer, or teacher"""
    user_id = get_current_user_id()
    if not user_id:
        return None, (jsonify({'error': 'Unauthorized: Not logged in'}), 401)
    user = db.session.get(User, user_id)
    if not user or user.role not in ['admin', 'lecturer', 'teacher']:
        return None, (jsonify({'error': 'Unauthorized: Admin or Lecturer access required'}), 403)
    return user, None

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    
    password = data.get('password', '')
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[\d\W]', password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain both letters and numbers/special characters.'}), 400
    
    existing_user = User.query.filter_by(username=data.get('username')).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
        
    existing_email = User.query.filter_by(email=data.get('email')).first()
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(password)
    
    requires_verification = True
    otp = str(random.randint(100000, 999999))
    expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        is_verified=False,
        verification_otp=otp,
        otp_expiry=expiry
    )
    
    # Send verification email via SendGrid if configured
    sg_api_key = os.environ.get('SENDGRID_API_KEY')
    sg_from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@yourdomain.com')
    
    if sg_api_key and sg_api_key != 'YOUR_SENDGRID_API_KEY_HERE':
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=sg_from_email,
                to_emails=data['email'],
                subject='Verify your Adaptive Learning Account',
                html_content=f'<strong>Your verification code is: {otp}</strong><br>It expires in 15 minutes.'
            )
            sg = SendGridAPIClient(sg_api_key)
            sg.send(message)
            print(f"✅ SendGrid OTP sent successfully to {data['email']}")
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            print(f"Fallback OTP: {otp}")
    else:
        print("="*50)
        print(f"OTP FOR {data['email']}: {otp}")
        print("="*50)
        
    db.session.add(user)
    db.session.flush()
    
    # Automatically unlock first subtopic with phase tracking initialized
    first_course = Course.query.order_by(Course.order_index).first()
    if first_course:
        first_topic = Topic.query.filter_by(course_id=first_course.id).order_by(Topic.order_index).first()
        if first_topic:
            first_subtopic = Subtopic.query.filter_by(topic_id=first_topic.id).order_by(Subtopic.order_index).first()
            if first_subtopic:
                progress = UserProgress(
                    user_id=user.id,
                    subtopic_id=first_subtopic.id,
                    is_unlocked=True,
                    current_phase=1,
                    started_at=datetime.now(timezone.utc)
                )
                db.session.add(progress)
    
    db.session.commit()
    
    if requires_verification:
        return jsonify({
            'message': 'Verification required',
            'requires_verification': True,
            'email': user.email
        })
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'has_completed_preassessment': user.has_completed_preassessment,
        'xp': user.xp,
        'current_streak': user.current_streak,
        'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None
    })

@auth_bp.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json or {}
    email = data.get('email')
    otp = data.get('otp')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.is_verified:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({
            'message': 'User already verified',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'has_completed_preassessment': user.has_completed_preassessment,
            'xp': user.xp,
            'current_streak': user.current_streak,
            'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None
        })
        
    if user.verification_otp != otp:
        return jsonify({'error': 'Invalid OTP'}), 400
        
    now = datetime.now(timezone.utc)
    if user.otp_expiry:
        expiry = user.otp_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now > expiry:
            return jsonify({'error': 'OTP expired'}), 400
        
    user.is_verified = True
    user.verification_otp = None
    user.otp_expiry = None
    db.session.commit()
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    return jsonify({
        'message': 'Email verified and logged in successfully',
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'has_completed_preassessment': user.has_completed_preassessment,
        'xp': user.xp,
        'current_streak': user.current_streak,
        'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None
    })

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    identifier = data.get('username') or data.get('email', '')
    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
    
    if user and user.password_hash and check_password_hash(user.password_hash, data.get('password', '')):
        if not getattr(user, 'is_verified', True):
            return jsonify({'error': 'Please verify your email address before logging in.', 'requires_verification': True}), 401
            
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'has_completed_preassessment': user.has_completed_preassessment,
            'xp': user.xp,
            'current_streak': user.current_streak,
            'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None
        })
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@auth_bp.route('/api/current-user', methods=['GET'])
def current_user():
    user_id = get_current_user_id()
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'has_completed_preassessment': user.has_completed_preassessment,
                'xp': user.xp,
                'current_streak': user.current_streak,
                'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None
            })
    return jsonify({'error': 'Not logged in'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})
