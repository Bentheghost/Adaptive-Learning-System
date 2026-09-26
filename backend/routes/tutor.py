"""
Tutor Assistance, Interactive Code Checking, Telemetry, and Chatbot Routes
"""
import io
import json
from contextlib import redirect_stdout
from flask import Blueprint, request, jsonify, session
from models import db, TelemetryCache, ChatMessage
from extensions import coordinator
from routes.auth import get_current_user_id

tutor_bp = Blueprint('tutor', __name__)

@tutor_bp.route('/api/hint', methods=['POST'])
def get_hint():
    """Get pedagogical hints from the TutorAgent"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    try:
        result = coordinator.perceive({
            'task': 'provide_hint',
            'user_id': user_id,
            'context': {
                'question': data.get('question', ''),
                'challenge': data.get('challenge', ''),
                'attempt_count': data.get('attempt_count', 1)
            }
        }).decide().act()
        
        if result.get('success'):
            tutor_result = result['results'].get('TutorAgent', {})
            hint = tutor_result.get('hint', "Try breaking down the problem into smaller steps.")
            return jsonify({'hint': hint})
        else:
            return jsonify({'hint': "Consider reviewing the lesson material."})
    except Exception as e:
        print(f"Hint error: {e}")
        return jsonify({'hint': "Try thinking about the basic principles."})

@tutor_bp.route('/api/check-code', methods=['POST'])
def check_code():
    """Safely execute Python code from interactive code playground"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    user_code = data.get('code', '')
    
    try:
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            exec(user_code, {'__builtins__': {'print': print, 'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict, 'set': set, 'tuple': tuple}})
        
        return jsonify({
            'success': True,
            'output': output_buffer.getvalue() or 'Code executed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Error: {str(e)}'
        })

@tutor_bp.route('/api/telemetry', methods=['POST'])
def save_telemetry():
    """Save learner interaction telemetry from the frontend"""
    data = request.json or {}
    try:
        user_id = session.get('user_id') or data.get('user_id') or get_current_user_id()
        event_type = data.get('event_type')
        context = data.get('context', '')
        payload = data.get('data', {})
        
        telemetry = TelemetryCache(
            event_type=event_type,
            user_id=user_id,
            context=context,
            data=json.dumps(payload)
        )
        
        db.session.add(telemetry)
        db.session.commit()
        return jsonify({'message': 'Telemetry saved successfully', 'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@tutor_bp.route('/api/chat', methods=['POST'])
def chat():
    """Process a message and return the TutorAgent conversational response"""
    data = request.json or {}
    user_id = session.get('user_id') or data.get('user_id') or get_current_user_id()
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
        
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
        
    try:
        user_msg = ChatMessage(user_id=user_id, role='user', content=message)
        db.session.add(user_msg)
        db.session.commit()
        
        history = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
        history_list = [{'role': msg.role, 'content': msg.content} for msg in history[:-1]]
        
        result = coordinator.perceive({
            'task': 'chat',
            'user_id': user_id,
            'message': message,
            'history': history_list
        }).decide().act()
        
        if result.get('success') and 'TutorAgent' in result.get('results', {}):
            agent_result = result['results']['TutorAgent']
            if agent_result.get('success'):
                reply = agent_result.get('response')
                ast_msg = ChatMessage(user_id=user_id, role='assistant', content=reply)
                db.session.add(ast_msg)
                db.session.commit()
                return jsonify({'reply': reply})
        
        return jsonify({'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tutor_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Retrieve chat history for the current user"""
    user_id = session.get('user_id') or request.args.get('user_id') or get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        history = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
        return jsonify([{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.isoformat() if msg.created_at else ''
        } for msg in history])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
