
from flask import Blueprint, jsonify, session, request
from database import db
from models.student import Student
from models.user import User
from models.risk_alert import RiskAlert
from sqlalchemy import func

statistics_bp = Blueprint('statistics', __name__)


# ============================================================
# FACULTY STATISTICS
# ============================================================
@statistics_bp.route('/api/statistics', methods=['GET'])
def get_faculty_statistics():
    """Faculty Dashboard statistics and chart data from database."""

    total_students = Student.query.count()

    low_risk = Student.query.filter_by(
        risk_level='Low Risk'
    ).count()

    medium_risk = Student.query.filter_by(
        risk_level='Medium Risk'
    ).count()

    high_risk = Student.query.filter_by(
        risk_level='High Risk'
    ).count()

    risk_distribution = {
        'labels': ['Low Risk', 'Medium Risk', 'High Risk'],
        'data': [low_risk, medium_risk, high_risk],
        'colors': ['#285743', '#D9A36C', '#B84A2B']
    }

    # Student count by department
    dept_rows = db.session.query(
        Student.department,
        func.count(Student.id)
    ).group_by(
        Student.department
    ).all()

    dept_labels = []
    dept_counts = []

    for dept, count in dept_rows:
        dept_labels.append(dept or 'Unknown')
        dept_counts.append(count)

    risk_by_department = {
        'labels': dept_labels,
        'data': dept_counts,
        'colors': [
            '#B84A2B',
            '#D9A36C',
            '#285743',
            '#16382C',
            '#6B7280'
        ]
    }

    return jsonify({
        'total_students': total_students,
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk,
        'risk_distribution': risk_distribution,
        'risk_by_department': risk_by_department
    }), 200


# ============================================================
# STUDENT PERSONAL STATISTICS
# ============================================================
@statistics_bp.route('/api/student/statistics', methods=['GET'])
def get_student_statistics():
    """
    Returns personal performance metrics for the authenticated student.
    Students can only see their own data.
    Faculty/Admin can request a specific student by email or ID.
    """

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    student = None

    if user and user.role == 'Student':
        # Match only the authenticated student's own record.
        conditions = []

        if user.email:
            conditions.append(Student.email.ilike(user.email))

        if user.username:
            conditions.append(
                Student.register_number.ilike(user.username)
            )
            conditions.append(
                Student.student_name.ilike(user.username)
            )

        if user.full_name:
            conditions.append(
                Student.student_name.ilike(user.full_name)
            )

        if conditions:
            from sqlalchemy import or_
            student = Student.query.filter(or_(*conditions)).first()

    elif user and user.role in ['Faculty', 'Admin']:
        email_param = request.args.get('email')
        id_param = request.args.get('id')

        if id_param:
            student = Student.query.get(id_param)
        elif email_param:
            student = Student.query.filter(
                Student.email.ilike(email_param)
            ).first()

    if not student:
        return jsonify({
            'has_data': False,
            'student': None,
            'overall_performance': 0,
            'attendance': 0,
            'current_risk': 'No Evaluation Yet',
            'risk_probability': 0,
            'pending_alerts': 0,
            'performance_breakdown': [],
            'message': (
                'No academic evaluation records found for your account. '
                'Please wait until your faculty mentor submits your '
                'semester academic metrics.'
            )
        }), 200

    # Performance breakdown for this student.
    performance_breakdown = [
        {
            'subject': 'Attendance',
            'score': round(float(student.attendance_percentage or 0), 1),
            'benchmark': 75.0
        },
        {
            'subject': 'CGPA (scaled)',
            'score': round(
                float(student.previous_semester_cgpa or 0) * 10, 1
            ),
            'benchmark': 70.0
        },
        {
            'subject': 'Assignments',
            'score': round(float(student.assignment_score or 0), 1),
            'benchmark': 75.0
        },
        {
            'subject': 'CIA Marks',
            'score': round(float(student.cia_marks or 0), 1),
            'benchmark': 60.0
        },
        {
            'subject': 'Lab Performance',
            'score': round(
                float(student.laboratory_performance or 0), 1
            ),
            'benchmark': 65.0
        },
        {
            'subject': 'Subject Marks',
            'score': round(
                float(student.subject_wise_marks or 0), 1
            ),
            'benchmark': 60.0
        }
    ]

    pending_alerts_count = RiskAlert.query.filter_by(
        student_id=student.id
    ).count()

    return jsonify({
        'has_data': True,
        'student': student.to_dict(),
        'overall_performance': student.overall_performance,
        'attendance': student.attendance_percentage,
        'current_risk': student.risk_level,
        'risk_probability': student.risk_probability,
        'pending_alerts': pending_alerts_count,
        'performance_breakdown': performance_breakdown
    }), 200


# ============================================================
# ADMIN / INSTITUTIONAL STATISTICS
# ============================================================
@statistics_bp.route('/api/admin/statistics', methods=['GET'])
def get_admin_statistics():
    """Institutional statistics and department-wise chart data."""

    total_students = Student.query.count()

    total_faculty = User.query.filter_by(
        role='Faculty'
    ).count()

    low_risk = Student.query.filter_by(
        risk_level='Low Risk'
    ).count()

    medium_risk = Student.query.filter_by(
        risk_level='Medium Risk'
    ).count()

    high_risk = Student.query.filter_by(
        risk_level='High Risk'
    ).count()

    # Institution-wide averages
    avg_att = db.session.query(
        func.avg(Student.attendance_percentage)
    ).scalar() or 0.0

    avg_perf = db.session.query(
        func.avg(Student.overall_performance)
    ).scalar() or 0.0

    avg_cgpa = db.session.query(
        func.avg(Student.previous_semester_cgpa)
    ).scalar() or 0.0

    # --------------------------------------------------------
    # Department-wise student count, performance and attendance
    # --------------------------------------------------------
    dept_stats_raw = db.session.query(
        Student.department,
        func.count(Student.id),
        func.avg(Student.overall_performance),
        func.avg(Student.attendance_percentage)
    ).group_by(
        Student.department
    ).all()

    dept_stats = []

    for department, count, performance, attendance in dept_stats_raw:
        dept_stats.append({
            'department': department or 'Unknown',
            'students_count': count,
            'avg_performance': round(
                float(performance or 0), 1
            ),
            'avg_attendance': round(
                float(attendance or 0), 1
            )
        })

    # --------------------------------------------------------
    # NEW: Department-wise Low / Medium / High Risk counts
    # --------------------------------------------------------
    dept_risk_raw = db.session.query(
        Student.department,
        Student.risk_level,
        func.count(Student.id)
    ).group_by(
        Student.department,
        Student.risk_level
    ).all()

    dept_risk_map = {}

    for department, risk_level, count in dept_risk_raw:
        department = department or 'Unknown'

        if department not in dept_risk_map:
            dept_risk_map[department] = {
                'department': department,
                'low_risk': 0,
                'medium_risk': 0,
                'high_risk': 0
            }

        if risk_level == 'Low Risk':
            dept_risk_map[department]['low_risk'] = count

        elif risk_level == 'Medium Risk':
            dept_risk_map[department]['medium_risk'] = count

        elif risk_level == 'High Risk':
            dept_risk_map[department]['high_risk'] = count

    department_risk_statistics = list(
        dept_risk_map.values()
    )

    # Overall risk distribution
    risk_distribution = {
        'labels': ['Low Risk', 'Medium Risk', 'High Risk'],
        'data': [low_risk, medium_risk, high_risk],
        'colors': ['#285743', '#D9A36C', '#B84A2B']
    }

    return jsonify({
        'total_students': total_students,
        'total_faculty': total_faculty,

        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk,

        'avg_attendance': round(float(avg_att), 1),
        'avg_performance': round(float(avg_perf), 1),
        'avg_cgpa': round(float(avg_cgpa), 2),

        'department_statistics': dept_stats,

        # NEW: Used by the department-wise risk chart in app.js
        'department_risk_statistics': department_risk_statistics,

        'risk_distribution': risk_distribution
    }), 200
