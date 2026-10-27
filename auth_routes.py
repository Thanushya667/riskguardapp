from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identifier = (data.get('email') or data.get('username') or '').strip().lower()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Invalid Username or Password'}), 401

    # Look up user by username or email
    user = User.query.filter(
        (User.username.ilike(identifier)) | (User.email.ilike(identifier))
    ).first()

    if not user or not user.check_password(password):
        # Support fallback alias for admin demo
        if (identifier in ['admin', 'admin@university.edu'] and password in ['admin@123', 'admin123']) and user:
            pass  # If user exists, but password mismatch, user.check_password handled it
        return jsonify({'error': 'Invalid Username or Password'}), 401

    # Save to session
    session['user_id'] = user.id
    session['role'] = user.role
    session['username'] = user.username

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    full_name = (data.get('full_name') or '').strip()
    identifier = (data.get('email') or data.get('username') or '').strip()
    password = data.get('password', '')
    role_raw = (data.get('role') or 'Student').strip()

    # Normalize role
    if 'faculty' in role_raw.lower():
        role = 'Faculty'
    elif 'admin' in role_raw.lower():
        role = 'Admin'
    else:
        role = 'Student'

    if not identifier or not password or not full_name:
        return jsonify({'error': 'Please provide all required fields.'}), 400

    email = identifier if '@' in identifier else f"{identifier}@riskguard.edu"
    username = identifier.split('@')[0] if '@' in identifier else identifier

    # Check if user already exists
    existing = User.query.filter(
        (User.username.ilike(username)) | (User.email.ilike(email))
    ).first()

    if existing:
        return jsonify({'error': 'Account already exists.'}), 409

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        department=data.get('department', 'Computer Science')
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Account Created Successfully',
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 401

    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 401

    return jsonify({
        'authenticated': True,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200
