from flask import Blueprint, request, jsonify, session
from database import db
from models.student import Student
from models.user import User
from models.risk_alert import RiskAlert
from models.prediction_history import PredictionHistory
from services.prediction.predictor import predictor
from services.email.email_service import email_service


student_bp = Blueprint('students', __name__)


# ============================================================
# GET ALL STUDENTS / OWN STUDENT DATA
# ============================================================

@student_bp.route('/api/students', methods=['GET'])
def get_students():

    """
    Returns student list.

    STRICT PRIVACY:
    A logged-in student can ONLY see their own student record.

    Faculty and Admin can view all students.
    """

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    # --------------------------------------------------------
    # STUDENT LOGIN - ONLY OWN DATA
    # --------------------------------------------------------

    if user and user.role == 'Student':

        student = Student.query.filter(
            (Student.email.ilike(user.email)) |
            (Student.register_number.ilike(user.username)) |
            (Student.student_name.ilike(user.full_name)) |
            (Student.student_name.ilike(user.username))
        ).first()

        if student:
            return jsonify([student.to_dict()]), 200

        return jsonify([]), 200

    # --------------------------------------------------------
    # FACULTY / ADMIN VIEW
    # --------------------------------------------------------

    search = request.args.get('search', '').strip().lower()
    risk_filter = request.args.get('risk_level', '').strip()
    dept_filter = request.args.get('department', '').strip()

    query = Student.query

    if search:

        query = query.filter(
            (Student.student_name.ilike(f'%{search}%')) |
            (Student.register_number.ilike(f'%{search}%')) |
            (Student.department.ilike(f'%{search}%'))
        )

    if risk_filter and risk_filter.lower() != 'all':

        query = query.filter(
            Student.risk_level.ilike(f'%{risk_filter}%')
        )

    if dept_filter and dept_filter.lower() != 'all':

        query = query.filter(
            Student.department.ilike(f'%{dept_filter}%')
        )

    students = query.order_by(Student.id.asc()).all()

    return jsonify(
        [s.to_dict() for s in students]
    ), 200


# ============================================================
# GET SINGLE STUDENT
# ============================================================

@student_bp.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):

    student = Student.query.get_or_404(id)

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    # --------------------------------------------------------
    # STUDENT PRIVACY CHECK
    # --------------------------------------------------------

    if user and user.role == 'Student':

        is_own_record = (

            student.email.lower() == user.email.lower()

            or

            student.register_number.lower() == user.username.lower()

            or

            student.student_name.lower() == user.full_name.lower()

            or

            student.student_name.lower() == user.username.lower()
        )

        if not is_own_record:

            return jsonify({
                'error':
                'Unauthorized. You can only view your own academic records.'
            }), 403

    # --------------------------------------------------------
    # GET ALERTS AND HISTORY
    # --------------------------------------------------------

    alerts = [
        a.to_dict()
        for a in student.alerts
    ]

    history = [
        h.to_dict()
        for h in student.history
    ]

    data = student.to_dict()

    data['alerts'] = alerts
    data['history'] = history

    return jsonify(data), 200


# ============================================================
# ADD STUDENT
# ============================================================

@student_bp.route('/api/students', methods=['POST'])
def add_student():

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    # Students cannot create student records
    if user and user.role == 'Student':

        return jsonify({
            'error':
            'Students are not authorized to create student records.'
        }), 403

    data = request.get_json() or {}

    # --------------------------------------------------------
    # REQUIRED FIELDS
    # --------------------------------------------------------

    required_fields = [

        'student_name',
        'register_number',
        'email',
        'department',

        'attendance_percentage',
        'previous_semester_cgpa',
        'assignment_score',
        'cia_marks',
        'laboratory_performance',
        'subject_wise_marks'
    ]

    for f in required_fields:

        if f not in data or data[f] is None or data[f] == '':

            return jsonify({
                'error': f"Field '{f}' is required."
            }), 400

    # --------------------------------------------------------
    # CONVERT NUMERICAL VALUES
    # --------------------------------------------------------

    try:

        attendance = float(
            data['attendance_percentage']
        )

        cgpa = float(
            data['previous_semester_cgpa']
        )

        assignment = float(
            data['assignment_score']
        )

        cia = float(
            data['cia_marks']
        )

        lab = float(
            data['laboratory_performance']
        )

        subject = float(
            data['subject_wise_marks']
        )

    except ValueError:

        return jsonify({
            'error':
            'Academic numerical parameters must be valid numbers.'
        }), 400

    # --------------------------------------------------------
    # RANGE VALIDATION
    # --------------------------------------------------------

    if not (0 <= attendance <= 100):

        return jsonify({
            'error':
            'Attendance percentage must be between 0 and 100.'
        }), 400

    if not (0 <= cgpa <= 10):

        return jsonify({
            'error':
            'CGPA must be between 0 and 10.'
        }), 400

    if not (0 <= assignment <= 100):

        return jsonify({
            'error':
            'Assignment score must be between 0 and 100.'
        }), 400

    if not (0 <= cia <= 100):

        return jsonify({
            'error':
            'CIA marks must be between 0 and 100.'
        }), 400

    if not (0 <= lab <= 100):

        return jsonify({
            'error':
            'Laboratory performance must be between 0 and 100.'
        }), 400

    if not (0 <= subject <= 100):

        return jsonify({
            'error':
            'Subject-wise marks must be between 0 and 100.'
        }), 400

    # --------------------------------------------------------
    # CHECK DUPLICATE REGISTER NUMBER
    # --------------------------------------------------------

    existing = Student.query.filter_by(
        register_number=data['register_number'].strip()
    ).first()

    if existing:

        return jsonify({
            'error':
            f"Student with register number "
            f"'{data['register_number']}' already exists."
        }), 409

    # --------------------------------------------------------
    # AI RISK PREDICTION
    # --------------------------------------------------------

    pred_result = predictor.predict(

        attendance=attendance,

        cgpa=cgpa,

        assignment=assignment,

        cia=cia,

        lab=lab,

        subject=subject
    )

    # --------------------------------------------------------
    # CREATOR
    # --------------------------------------------------------

    creator_id = session.get('user_id')

    # --------------------------------------------------------
    # CREATE STUDENT
    # --------------------------------------------------------

    student = Student(

        student_name=data['student_name'].strip(),

        register_number=data['register_number'].strip(),

        email=data['email'].strip(),

        department=data['department'].strip(),

        attendance_percentage=attendance,

        previous_semester_cgpa=cgpa,

        assignment_score=assignment,

        cia_marks=cia,

        laboratory_performance=lab,

        subject_wise_marks=subject,

        overall_performance=
        pred_result['overall_performance'],

        risk_level=
        pred_result['risk_level'],

        risk_probability=
        pred_result['risk_probability'],

        created_by=creator_id
    )

    db.session.add(student)

    # Get student.id
    db.session.flush()

    # --------------------------------------------------------
    # PREDICTION HISTORY
    # --------------------------------------------------------

    history = PredictionHistory(

        student_id=student.id,

        risk_level=
        pred_result['risk_level'],

        risk_probability=
        pred_result['risk_probability'],

        details=", ".join(
            pred_result['risk_factors']
        )
    )

    db.session.add(history)

    # ========================================================
    # EMAIL ALERT FOR ALL RISK LEVELS
    # ========================================================

    alert_record = None

    email_status = 'NOT_CONFIGURED'

    risk_level = pred_result['risk_level']

    # --------------------------------------------------------
    # HIGH RISK MESSAGE
    # --------------------------------------------------------

    if risk_level == 'High Risk':

        alert_msg = (
            'Your academic performance indicates that '
            'you are currently identified as a High Risk student. '
            'Immediate academic attention and intervention '
            'are recommended.'
        )

        email_recommendations = pred_result['recommendations']

    # --------------------------------------------------------
    # MEDIUM RISK MESSAGE
    # --------------------------------------------------------

    elif risk_level == 'Medium Risk':

        alert_msg = (
            'Your academic performance indicates that '
            'you are currently identified as a Medium Risk student. '
            'Please focus on improving your academic performance '
            'and maintain regular progress.'
        )

        email_recommendations = pred_result['recommendations']

    # --------------------------------------------------------
    # LOW RISK MESSAGE
    # --------------------------------------------------------

    else:

        alert_msg = (
            'Congratulations! You are currently at Low Risk. '
            'Good job! Keep maintaining your excellent '
            'academic performance.'
        )

        email_recommendations = [
            'Good job! Keep maintaining your academic performance.',
            'Continue attending classes regularly.',
            'Keep submitting assignments on time.',
            'Continue maintaining good marks and consistent progress.'
        ]

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    status, _ = email_service.send_risk_alert_email(

        student_name=student.student_name,

        student_email=student.email,

        risk_level=risk_level,

        risk_factors=pred_result['risk_factors'],

        recommendations=email_recommendations
    )

    email_status = status

    # --------------------------------------------------------
    # SAVE ALERT
    # --------------------------------------------------------

    recommendation_str = " • ".join(
        email_recommendations
    )

    alert_record = RiskAlert(

        student_id=student.id,

        risk_level=risk_level,

        alert_message=alert_msg,

        recommendation=recommendation_str,

        email_status=email_status
    )

    db.session.add(alert_record)

    # --------------------------------------------------------
    # COMMIT EVERYTHING
    # --------------------------------------------------------

    db.session.commit()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return jsonify({

        'message':
        'Student added and risk analyzed successfully.',

        'student':
        student.to_dict(),

        'prediction':
        pred_result,

        'email_status':
        email_status

    }), 201


# ============================================================
# UPDATE STUDENT
# ============================================================

@student_bp.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):

    student = Student.query.get_or_404(id)

    data = request.get_json() or {}

    # --------------------------------------------------------
    # UPDATE BASIC DETAILS
    # --------------------------------------------------------

    if 'student_name' in data:

        student.student_name = (
            data['student_name'].strip()
        )

    if 'email' in data:

        student.email = (
            data['email'].strip()
        )

    if 'department' in data:

        student.department = (
            data['department'].strip()
        )

    # --------------------------------------------------------
    # UPDATE ACADEMIC DATA
    # --------------------------------------------------------

    if any(
        k in data
        for k in [

            'attendance_percentage',

            'previous_semester_cgpa',

            'assignment_score',

            'cia_marks',

            'laboratory_performance',

            'subject_wise_marks'
        ]
    ):

        student.attendance_percentage = float(
            data.get(
                'attendance_percentage',
                student.attendance_percentage
            )
        )

        student.previous_semester_cgpa = float(
            data.get(
                'previous_semester_cgpa',
                student.previous_semester_cgpa
            )
        )

        student.assignment_score = float(
            data.get(
                'assignment_score',
                student.assignment_score
            )
        )

        student.cia_marks = float(
            data.get(
                'cia_marks',
                student.cia_marks
            )
        )

        student.laboratory_performance = float(
            data.get(
                'laboratory_performance',
                student.laboratory_performance
            )
        )

        student.subject_wise_marks = float(
            data.get(
                'subject_wise_marks',
                student.subject_wise_marks
            )
        )

        # ----------------------------------------------------
        # RE-PREDICT RISK
        # ----------------------------------------------------

        pred = predictor.predict(

            attendance=
            student.attendance_percentage,

            cgpa=
            student.previous_semester_cgpa,

            assignment=
            student.assignment_score,

            cia=
            student.cia_marks,

            lab=
            student.laboratory_performance,

            subject=
            student.subject_wise_marks
        )

        student.overall_performance = (
            pred['overall_performance']
        )

        student.risk_level = (
            pred['risk_level']
        )

        student.risk_probability = (
            pred['risk_probability']
        )

        # ----------------------------------------------------
        # SAVE NEW PREDICTION HISTORY
        # ----------------------------------------------------

        history = PredictionHistory(

            student_id=student.id,

            risk_level=pred['risk_level'],

            risk_probability=
            pred['risk_probability'],

            details=", ".join(
                pred['risk_factors']
            )
        )

        db.session.add(history)

    # --------------------------------------------------------
    # COMMIT UPDATE
    # --------------------------------------------------------

    db.session.commit()

    return jsonify({

        'message':
        'Student updated successfully',

        'student':
        student.to_dict()

    }), 200


# ============================================================
# DELETE STUDENT
# ============================================================

@student_bp.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)

    db.session.commit()

    return jsonify({

        'message':
        'Student deleted successfully'

    }), 200