import logging

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from database import db
from models.student import Student
from services.prediction.predictor import predictor
from services.intervention_service import intervention_service

prediction_bp = Blueprint('prediction', __name__)

logger = logging.getLogger(__name__)


# =========================================================
# 1. ACADEMIC RISK PREDICTION
# =========================================================

@prediction_bp.route('/api/predict', methods=['POST'])
def predict_risk():
    data = request.get_json(silent=True) or {}

    # Validate numerical inputs
    try:
        attendance = float(data.get('attendance_percentage', 0))
        cgpa = float(data.get('previous_semester_cgpa', 0))
        assignment = float(data.get('assignment_score', 0))
        cia = float(data.get('cia_marks', 0))
        lab = float(data.get('laboratory_performance', 0))
        subject = float(data.get('subject_wise_marks', 0))

    except (TypeError, ValueError):
        return jsonify({
            'error': 'Invalid numerical inputs'
        }), 400

    # Validate input ranges
    if not 0 <= attendance <= 100:
        return jsonify({
            'error': 'Attendance must be between 0 and 100'
        }), 400

    if not 0 <= cgpa <= 10:
        return jsonify({
            'error': 'CGPA must be between 0 and 10'
        }), 400

    for field, value in [
        ('assignment_score', assignment),
        ('cia_marks', cia),
        ('laboratory_performance', lab),
        ('subject_wise_marks', subject)
    ]:
        if not 0 <= value <= 100:
            return jsonify({
                'error': f'{field} must be between 0 and 100'
            }), 400

    student_name = data.get('student_name', 'Student')
    student_email = data.get('student_email', '')

    # Run the existing prediction model
    result = predictor.predict(
        attendance,
        cgpa,
        assignment,
        cia,
        lab,
        subject
    )

    risk_level = result.get('risk_level', '')

    result['email_status'] = 'NOT_SENT'
    result['email_message'] = 'No email sent.'
    result['intervention_status'] = 'NOT_REQUIRED'
    result['intervention_details'] = None

    # Initiate intervention for high-risk students
    if risk_level == 'High Risk':
        if student_email:
            try:
                intervention_result = (
                    intervention_service.create_high_risk_intervention(
                        student={
                            'student_name': student_name,
                            'email': student_email
                        },
                        prediction_result=result,
                        course_id=data.get('course_id')
                    )
                )

                result['intervention_status'] = 'PROCESSED'
                result['intervention_details'] = intervention_result

                if isinstance(intervention_result, dict):
                    result['email_status'] = intervention_result.get(
                        'email_status', 'UNKNOWN'
                    )
                    result['email_message'] = intervention_result.get(
                        'email_message',
                        'Intervention service processed.'
                    )

            except Exception:
                logger.exception(
                    'High-risk intervention processing failed'
                )

                result['intervention_status'] = 'FAILED'
                result['intervention_details'] = {
                    'message': (
                        'Prediction succeeded, but intervention processing '
                        'failed. Check the backend logs.'
                    )
                }

        else:
            result['intervention_status'] = 'PENDING'
            result['intervention_details'] = {
                'message': (
                    'A student email is required to initiate intervention.'
                )
            }

    return jsonify(result), 200


# =========================================================
# 2. MODEL INSIGHTS
# =========================================================
@prediction_bp.route('/api/prediction/insights', methods=['GET'])
def model_insights():
    try:
        total_students = Student.query.count()

        averages = db.session.query(
            func.avg(Student.attendance_percentage),
            func.avg(Student.previous_semester_cgpa)
        ).first()

        avg_attendance = averages[0] if averages else None
        avg_cgpa = averages[1] if averages else None

        # Risk distribution from saved student records
        risk_rows = db.session.query(
            Student.risk_level,
            func.count(Student.id)
        ).group_by(Student.risk_level).all()

        risk_counts = {
            'High Risk': 0,
            'Medium Risk': 0,
            'Low Risk': 0
        }

        for risk_level, count in risk_rows:
            if risk_level in risk_counts:
                risk_counts[risk_level] = int(count)

        def percentage(count):
            if total_students == 0:
                return 0
            return round((count / total_students) * 100, 2)

        features = predictor.get_feature_importances()

        key_risk_drivers = [
            {
                'driver': 'Attendance',
                'threshold': 'Below 75%',
                'impact': 'Low attendance may affect academic progress.',
                'recommendation': 'Monitor attendance and provide follow-up support.'
            },
            {
                'driver': 'Previous Semester CGPA',
                'threshold': 'Below 6.5',
                'impact': 'Low CGPA may indicate difficulties with course outcomes.',
                'recommendation': 'Offer mentoring and subject-level academic support.'
            },
            {
                'driver': 'CIA Marks',
                'threshold': 'Below 60%',
                'impact': 'Low internal assessment marks can indicate learning gaps.',
                'recommendation': 'Arrange revision sessions and practice assessments.'
            },
            {
                'driver': 'Assignment Score',
                'threshold': 'Below 65%',
                'impact': 'Low assignment scores may reflect incomplete understanding.',
                'recommendation': 'Provide assignment feedback and completion support.'
            },
            {
                'driver': 'Laboratory Performance',
                'threshold': 'Below 60%',
                'impact': 'Low lab performance may indicate practical skill gaps.',
                'recommendation': 'Provide supervised practical sessions.'
            },
            {
                'driver': 'Subject-wise Marks',
                'threshold': 'Below 55%',
                'impact': 'Low subject marks may indicate topics needing attention.',
                'recommendation': 'Identify weak topics and provide targeted practice.'
            }
        ]

        return jsonify({
            'total_students': total_students,
            'summary': {
                'avg_attendance': (
                    round(float(avg_attendance), 2)
                    if avg_attendance is not None else None
                ),
                'avg_cgpa': (
                    round(float(avg_cgpa), 2)
                    if avg_cgpa is not None else None
                )
            },
            'risk_distribution': {
                'high': {
                    'count': risk_counts['High Risk'],
                    'percentage': percentage(risk_counts['High Risk'])
                },
                'medium': {
                    'count': risk_counts['Medium Risk'],
                    'percentage': percentage(risk_counts['Medium Risk'])
                },
                'low': {
                    'count': risk_counts['Low Risk'],
                    'percentage': percentage(risk_counts['Low Risk'])
                }
            },
            'features': features,
            'key_risk_drivers': key_risk_drivers,
            'accuracy': None,
            'evaluation_message': (
                'Model evaluation requires labelled test data.'
            )
        }), 200

    except Exception:
        logger.exception('Model Insights API failed')
        return jsonify({
            'message': 'Unable to calculate model insights.'
        }), 500
