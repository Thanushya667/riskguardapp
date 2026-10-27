import pandas as pd

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename

from database import db
from models.student import Student
from models.risk_alert import RiskAlert

from services.prediction.predictor import predictor
from services.email.email_service import email_service


# =========================================================
# Dataset Blueprint
# =========================================================

dataset_bp = Blueprint(
    'dataset',
    __name__,
    url_prefix='/api/dataset'
)


# =========================================================
# Allowed File Extensions
# =========================================================

ALLOWED_EXTENSIONS = {
    'csv',
    'xlsx'
}


# =========================================================
# Required Dataset Columns
# =========================================================

REQUIRED_COLUMNS = {
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
}


# =========================================================
# Check Allowed File
# =========================================================

def allowed_file(filename):

    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# Upload Dataset
# =========================================================

@dataset_bp.route('/upload', methods=['POST'])
def upload_dataset():

    try:

        # =================================================
        # Check Login
        # =================================================

        user_id = session.get('user_id')

        if not user_id:

            return jsonify({
                'success': False,
                'message': 'Please login first.'
            }), 401


        # =================================================
        # Check Uploaded File
        # =================================================

        if 'file' not in request.files:

            return jsonify({
                'success': False,
                'message': 'No dataset file uploaded.'
            }), 400


        file = request.files['file']


        if file.filename == '':

            return jsonify({
                'success': False,
                'message': 'Please select a dataset file.'
            }), 400


        # =================================================
        # Secure Filename
        # =================================================

        filename = secure_filename(file.filename)


        # =================================================
        # Check File Type
        # =================================================

        if not allowed_file(filename):

            return jsonify({
                'success': False,
                'message': (
                    'Only CSV and Excel (.xlsx) files are allowed.'
                )
            }), 400


        # =================================================
        # Read Dataset
        # =================================================

        try:

            if filename.lower().endswith('.csv'):

                df = pd.read_csv(file)

            else:

                df = pd.read_excel(file)

        except Exception as file_error:

            return jsonify({
                'success': False,
                'message': 'Unable to read the uploaded dataset.',
                'error': str(file_error)
            }), 400


        # =================================================
        # Remove Completely Empty Rows
        # =================================================

        df = df.dropna(how='all')


        if df.empty:

            return jsonify({
                'success': False,
                'message': 'The uploaded dataset is empty.'
            }), 400


        # =================================================
        # Clean Column Names
        # =================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )


        # =================================================
        # Check Required Columns
        # =================================================

        missing_columns = (
            REQUIRED_COLUMNS - set(df.columns)
        )


        if missing_columns:

            return jsonify({
                'success': False,
                'message': 'Required columns are missing.',
                'missing_columns': sorted(
                    list(missing_columns)
                )
            }), 400


        # =================================================
        # Counters / Results
        # =================================================

        added_students = []
        skipped_students = []
        errors = []

        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0


        # =================================================
        # Process Each Student
        # =================================================

        for index, row in df.iterrows():

            row_number = index + 2

            try:

                # =========================================
                # Basic Student Information
                # =========================================

                student_name = str(
                    row['student_name']
                ).strip()

                register_number = str(
                    row['register_number']
                ).strip()

                email = str(
                    row['email']
                ).strip()

                department = str(
                    row['department']
                ).strip()


                # =========================================
                # Check Empty Values
                # =========================================

                if (
                    not student_name
                    or not register_number
                    or not email
                    or not department
                ):

                    errors.append({
                        'row': row_number,
                        'message': (
                            'Student name, register number, '
                            'email and department are required.'
                        )
                    })

                    continue


                # =========================================
                # Check Duplicate Register Number
                # =========================================

                existing_student = Student.query.filter_by(
                    register_number=register_number
                ).first()


                if existing_student:

                    skipped_students.append({
                        'row': row_number,
                        'register_number': register_number,
                        'student_name': student_name,
                        'reason': 'Student already exists.'
                    })

                    continue


                # =========================================
                # Convert Academic Values
                # =========================================

                attendance = float(
                    row['attendance_percentage']
                )

                cgpa = float(
                    row['previous_semester_cgpa']
                )

                assignment = float(
                    row['assignment_score']
                )

                cia = float(
                    row['cia_marks']
                )

                laboratory = float(
                    row['laboratory_performance']
                )

                subject_marks = float(
                    row['subject_wise_marks']
                )


                # =========================================
                # Validate Numeric Values
                # =========================================

                if not 0 <= attendance <= 100:

                    raise ValueError(
                        'Attendance must be between 0 and 100.'
                    )


                if not 0 <= cgpa <= 10:

                    raise ValueError(
                        'CGPA must be between 0 and 10.'
                    )


                if not 0 <= assignment <= 100:

                    raise ValueError(
                        'Assignment score must be between 0 and 100.'
                    )


                if not 0 <= cia <= 100:

                    raise ValueError(
                        'CIA marks must be between 0 and 100.'
                    )


                if not 0 <= laboratory <= 100:

                    raise ValueError(
                        'Laboratory performance must be between 0 and 100.'
                    )


                if not 0 <= subject_marks <= 100:

                    raise ValueError(
                        'Subject-wise marks must be between 0 and 100.'
                    )


                # =========================================
                # AI Risk Prediction
                # =========================================

                pred_result = predictor.predict(
                    attendance,
                    cgpa,
                    assignment,
                    cia,
                    laboratory,
                    subject_marks
                )


                overall_performance = (
                    pred_result['overall_performance']
                )

                risk_level = (
                    pred_result['risk_level']
                )

                risk_probability = (
                    pred_result['risk_probability']
                )


                # =========================================
                # Create Student
                # =========================================

                student = Student(

                    student_name=student_name,

                    register_number=register_number,

                    email=email,

                    department=department,

                    attendance_percentage=attendance,

                    previous_semester_cgpa=cgpa,

                    assignment_score=assignment,

                    cia_marks=cia,

                    laboratory_performance=laboratory,

                    subject_wise_marks=subject_marks,

                    overall_performance=overall_performance,

                    risk_level=risk_level,

                    risk_probability=risk_probability,

                    created_by=user_id
                )


                db.session.add(student)

                # Get generated student ID
                db.session.flush()


                # =========================================
                # Risk Based Message
                # =========================================

                if risk_level == 'High Risk':

                    high_risk_count += 1

                    alert_message = (
                        'Your current academic performance '
                        'indicates that you are at High Risk. '
                        'Immediate academic attention is recommended.'
                    )


                elif risk_level == 'Medium Risk':

                    medium_risk_count += 1

                    alert_message = (
                        'Your current academic performance '
                        'indicates Medium Risk. '
                        'Please improve your academic performance '
                        'and maintain consistent progress.'
                    )


                else:

                    low_risk_count += 1

                    alert_message = (
                        'Congratulations! You are currently '
                        'at Low Risk. Good job! Keep maintaining '
                        'your academic performance.'
                    )


                # =========================================
                # Recommendations
                # =========================================

                recommendations = pred_result[
                    'recommendations'
                ]


                if risk_level == 'Low Risk':

                    recommendations = [

                        'Good job! Keep maintaining your academic performance.',

                        'Continue attending classes regularly.',

                        'Keep submitting assignments on time.',

                        'Continue maintaining good marks and consistent progress.'

                    ]


                recommendation_text = ' • '.join(
                    recommendations
                )


                # =========================================
                # Send Email
                # =========================================

                email_status, email_message = (
                    email_service.send_risk_alert_email(

                        student_name=student_name,

                        student_email=email,

                        risk_level=risk_level,

                        risk_factors=pred_result[
                            'risk_factors'
                        ],

                        recommendations=recommendations
                    )
                )


                # =========================================
                # Create Risk Alert
                # =========================================

                alert_record = RiskAlert(

                    student_id=student.id,

                    risk_level=risk_level,

                    alert_message=alert_message,

                    recommendation=recommendation_text,

                    email_status=email_status
                )


                db.session.add(alert_record)


                # =========================================
                # Store Successful Result
                # =========================================

                added_students.append({

                    'student_name': student_name,

                    'register_number': register_number,

                    'email': email,

                    'risk_level': risk_level,

                    'risk_probability': risk_probability,

                    'overall_performance':
                        overall_performance,

                    'email_status': email_status,

                    'email_message': email_message

                })


            # =============================================
            # Row Processing Error
            # =============================================

            except Exception as row_error:

                errors.append({

                    'row': row_number,

                    'student_name':
                        str(row.get(
                            'student_name',
                            ''
                        )),

                    'register_number':
                        str(row.get(
                            'register_number',
                            ''
                        )),

                    'message': str(row_error)

                })


        # =================================================
        # Commit Database
        # =================================================

        db.session.commit()


        # =================================================
        # Final Response
        # =================================================

        return jsonify({

            'success': True,

            'message':
                'Dataset uploaded and processed successfully.',

            'total_rows':
                len(df),

            'added_students':
                len(added_students),

            'skipped_students':
                len(skipped_students),

            'errors':
                len(errors),

            'high_risk':
                high_risk_count,

            'medium_risk':
                medium_risk_count,

            'low_risk':
                low_risk_count,

            'students':
                added_students,

            'skipped':
                skipped_students,

            'error_details':
                errors

        }), 200


    # =====================================================
    # General Error
    # =====================================================

    except Exception as e:

        db.session.rollback()

        print(
            f'Dataset Upload Error: {e}'
        )

        return jsonify({

            'success': False,

            'message':
                'Failed to process dataset.',

            'error':
                str(e)

        }), 500