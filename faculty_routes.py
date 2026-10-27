
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from database import db
from models.user import User
from models.student import Student
from models.intervention_tracking import InterventionTracking


faculty_bp = Blueprint('faculty', __name__)


# ============================================================
# GET ALL FACULTY MEMBERS
# ============================================================

@faculty_bp.route('/api/admin/faculty', methods=['GET'])
def get_faculty_members():
    faculty_users = User.query.filter_by(role='Faculty').all()

    results = []

    for faculty in faculty_users:
        student_count = Student.query.filter_by(
            created_by=faculty.id
        ).count()

        # If no students are assigned, count students in same department
        if student_count == 0 and faculty.department:
            student_count = Student.query.filter_by(
                department=faculty.department
            ).count()

        results.append({
            'id': faculty.id,
            'name': faculty.full_name,
            'email': faculty.email,
            'department': faculty.department or 'Computer Science',
            'student_count': student_count,
            'status': 'Active',
            'created_at': (
                faculty.created_at.strftime('%Y-%m-%d')
                if faculty.created_at else '2026-01-15'
            )
        })

    return jsonify(results), 200


# ============================================================
# ADD FACULTY MEMBER
# ============================================================

@faculty_bp.route('/api/admin/faculty', methods=['POST'])
def add_faculty_member():
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    department = (
        data.get('department') or 'Computer Science'
    ).strip()
    password = data.get('password', 'faculty@123')

    if not name or not email:
        return jsonify({
            'error': 'Name and Email are required'
        }), 400

    existing = User.query.filter(
        (User.email.ilike(email)) |
        (User.username.ilike(email.split('@')[0]))
    ).first()

    if existing:
        return jsonify({
            'error': 'User already exists with this email'
        }), 409

    new_faculty = User(
        username=email.split('@')[0],
        email=email,
        full_name=name,
        role='Faculty',
        department=department
    )

    new_faculty.set_password(password)

    try:
        db.session.add(new_faculty)
        db.session.commit()

        return jsonify({
            'message': 'Faculty added successfully',
            'faculty': new_faculty.to_dict()
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            'error': 'Could not add faculty member'
        }), 500


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def get_authorized_faculty():
    user_id = session.get('user_id')

    if not user_id:
        return None, (
            jsonify({'error': 'Please log in first'}),
            401
        )

    user = db.session.get(User, user_id)

    if not user or user.role not in ['Faculty', 'Admin']:
        return None, (
            jsonify({'error': 'Access denied'}),
            403
        )

    return user, None


# ============================================================
# GET PENDING INTERVENTIONS
# ============================================================

@faculty_bp.route(
    '/api/faculty/interventions/pending',
    methods=['GET']
)
def get_pending_interventions():
    user, error_response = get_authorized_faculty()

    if error_response:
        return error_response

    records = InterventionTracking.query.filter_by(
        faculty_approval_status='PENDING'
    ).order_by(
        InterventionTracking.created_at.desc()
    ).all()

    return jsonify([
        record.to_dict() for record in records
    ]), 200


# ============================================================
# APPROVE OR REJECT AN INTERVENTION
# ============================================================

@faculty_bp.route(
    '/api/faculty/interventions/<int:tracking_id>/decision',
    methods=['POST']
)
def decide_intervention(tracking_id):
    user, error_response = get_authorized_faculty()

    if error_response:
        return error_response

    data = request.get_json() or {}

    decision = (
        data.get('decision') or ''
    ).strip().upper()

    if decision not in ['APPROVED', 'REJECTED']:
        return jsonify({
            'error': "decision must be 'APPROVED' or 'REJECTED'"
        }), 400

    record = db.session.get(
        InterventionTracking,
        tracking_id
    )

    if not record:
        return jsonify({
            'error': 'Intervention not found'
        }), 404

    if record.faculty_approval_status != 'PENDING':
        return jsonify({
            'error': 'This intervention already has a decision',
            'current_status': record.faculty_approval_status
        }), 409

    # Save the faculty decision.
    # Publishing must happen through a separate protected route.
    record.faculty_approval_status = decision
    record.faculty_approved_by = user.id
    record.faculty_approved_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            'error': 'Could not save the decision'
        }), 500

    return jsonify({
        'message': (
            f'Intervention {decision.lower()} successfully'
        ),
        'tracking_id': record.id,
        'faculty_approval_status': record.faculty_approval_status,
        'faculty_approved_by': record.faculty_approved_by,
        'faculty_approved_at': (
            record.faculty_approved_at.strftime('%Y-%m-%d %H:%M')
            if record.faculty_approved_at else None
        )
    }), 200
