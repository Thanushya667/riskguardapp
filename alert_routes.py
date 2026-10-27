from flask import Blueprint, request, jsonify, session
from database import db
from models.risk_alert import RiskAlert
from models.student import Student
from models.user import User
from services.email.email_service import email_service

alert_bp = Blueprint('alerts', __name__)

@alert_bp.route('/api/alerts', methods=['GET'])
def get_all_alerts():
    """
    Returns alerts.
    If logged in as Student: strictly returns ONLY that student's alerts.
    If Faculty or Admin: returns all institution alerts.
    """
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    # Privacy constraint: Students can NEVER see other students' alerts
    if user and user.role == 'Student':
        student = Student.query.filter(
            (Student.email.ilike(user.email)) |
            (Student.register_number.ilike(user.username)) |
            (Student.student_name.ilike(user.full_name)) |
            (Student.student_name.ilike(user.username))
        ).first()
        if student:
            alerts = RiskAlert.query.filter_by(student_id=student.id).order_by(RiskAlert.created_at.desc()).all()
            return jsonify([a.to_dict() for a in alerts]), 200
        return jsonify([]), 200

    alerts = RiskAlert.query.order_by(RiskAlert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts]), 200

@alert_bp.route('/api/student/alerts', methods=['GET'])
def get_student_alerts():
    """
    Returns alerts for the specific student.
    Strictly isolated: a student cannot view another student's alerts.
    """
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    
    student = None
    if user and user.role == 'Student':
        # Authenticated student strictly bounded to their own record
        student = Student.query.filter(
            (Student.email.ilike(user.email)) |
            (Student.register_number.ilike(user.username)) |
            (Student.student_name.ilike(user.full_name)) |
            (Student.student_name.ilike(user.username))
        ).first()
    elif user and user.role in ['Faculty', 'Admin']:
        # Faculty or admin querying specific student's alerts
        email_param = request.args.get('email', '')
        id_param = request.args.get('id')
        if id_param:
            student = Student.query.get(id_param)
        elif email_param:
            student = Student.query.filter(Student.email.ilike(email_param)).first()
    else:
        email_param = request.args.get('email', '')
        if email_param:
            student = Student.query.filter(Student.email.ilike(email_param)).first()

    if student:
        alerts = RiskAlert.query.filter_by(student_id=student.id).order_by(RiskAlert.created_at.desc()).all()
        return jsonify([a.to_dict() for a in alerts]), 200

    # If no student record found, return empty array (never fall through to all alerts)
    return jsonify([]), 200

@alert_bp.route('/api/alerts/<int:id>/send-email', methods=['POST'])
def retry_send_email(id):
    alert = RiskAlert.query.get_or_404(id)
    student = alert.student

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    status, msg = email_service.send_risk_alert_email(
        student_name=student.student_name,
        student_email=student.email,
        risk_level=alert.risk_level,
        risk_factors=alert.alert_message,
        recommendations=alert.recommendation,
        prediction_date=alert.created_at.strftime('%Y-%m-%d') if alert.created_at else None
    )

    alert.email_status = status
    db.session.commit()

    return jsonify({
        'status': status,
        'message': msg,
        'alert': alert.to_dict()
    }), 200
