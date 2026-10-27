import os

from flask import Blueprint, redirect, request, session, jsonify

from google_auth_oauthlib.flow import Flow

from config import Config
from services.google_classroom.classroom_service import classroom_service


classroom_bp = Blueprint(
    'classroom',
    __name__,
    url_prefix='/api/google-classroom'
)


SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
]


CLIENT_SECRETS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'credentials.json'
)


@classroom_bp.route('/status', methods=['GET'])
def classroom_status():
    return jsonify(classroom_service.get_status())


@classroom_bp.route('/auth', methods=['GET'])
def classroom_auth():

    if not os.path.exists(CLIENT_SECRETS_FILE):
        return jsonify({
            'success': False,
            'error': 'credentials.json not found.'
        }), 500

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # IMPORTANT
        session['google_oauth_state'] = state

        # PKCE verifier
        if getattr(flow, 'code_verifier', None):
            session['google_code_verifier'] = flow.code_verifier

        session.modified = True

        print("OAuth State Saved:", state)
        print("OAuth Code Verifier Saved:",
              bool(session.get('google_code_verifier')))

        return redirect(authorization_url)

    except Exception as e:
        print("Google OAuth Start Error:", e)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@classroom_bp.route('/oauth2callback', methods=['GET'])
def google_oauth_callback():

    try:
        print("\n========== GOOGLE OAUTH CALLBACK ==========")
        print("Callback URL:", request.url)
        print("Received State:", request.args.get('state'))
        print("Session State:", session.get('google_oauth_state'))

        google_state = request.args.get('state')
        saved_state = session.get('google_oauth_state')

        if not google_state:
            return jsonify({
                'success': False,
                'error': 'Google did not return OAuth state.'
            }), 400

        if not saved_state:
            return jsonify({
                'success': False,
                'error': 'OAuth state was lost from Flask session. Please start Google Classroom authentication again.'
            }), 400

        if google_state != saved_state:
            return jsonify({
                'success': False,
                'error': 'OAuth state mismatch. Please start authentication again.'
            }), 400

        if 'error' in request.args:
            return jsonify({
                'success': False,
                'error': request.args.get('error'),
                'description': request.args.get('error_description')
            }), 400

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=saved_state,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        # Restore PKCE verifier
        code_verifier = session.get('google_code_verifier')

        if code_verifier:
            flow.code_verifier = code_verifier

        flow.fetch_token(
            authorization_response=request.url
        )

        credentials = flow.credentials

        classroom_service.set_credentials(credentials)

        # Clear temporary OAuth data
        session.pop('google_oauth_state', None)
        session.pop('google_code_verifier', None)
        session.modified = True

        print("Google Classroom OAuth SUCCESS")

        return jsonify({
            'success': True,
            'message': 'Google Classroom connected successfully.'
        })

    except Exception as e:

        print("Google OAuth Callback Error:", e)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@classroom_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        courses = classroom_service.get_courses()

        return jsonify({
            'success': True,
            'courses': courses
        })

    except Exception as e:
        print("Get Courses Error:", e)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@classroom_bp.route('/students', methods=['GET'])
def get_students():
    course_id = request.args.get('course_id')

    if not course_id:
        return jsonify({
            'success': False,
            'error': 'course_id is required.'
        }), 400

    try:
        students = classroom_service.get_course_students(
            course_id=course_id
        )

        student_list = []

        for student in students:
            profile = student.get('profile', {})

            student_list.append({
                'student_id': student.get('userId'),
                'name': profile.get('name', {}).get('fullName', ''),
                'email': profile.get('emailAddress', '')
            })

        return jsonify({
            'success': True,
            'course_id': course_id,
            'student_count': len(student_list),
            'students': student_list
        })

    except Exception as e:
        print("Get Students Error:", e)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

   

@classroom_bp.route('/create-assignment', methods=['POST'])
def create_assignment():
    data = request.get_json(silent=True) or {}

    course_id = data.get('course_id')
    student_id = data.get('student_id')
    student_email = data.get('student_email')
    student_name = data.get('student_name', 'Test Student')

    if not course_id or not (student_id or student_email):
        return jsonify({
            'success': False,
            'error': 'course_id and either student_id or student_email are required.'
        }), 400

    try:
        result = classroom_service.create_high_risk_assignment(
            course_id=str(course_id),
            student_name=student_name,
            risk_factors=data.get('risk_factors', []),
            recommendations=data.get('recommendations', []),
            student_email=student_email,
            student_id=str(student_id) if student_id else None
        )

        return jsonify(result), (
            201 if result.get('success') else 400
        )

    except Exception as e:
        print("Create Assignment Route Error:", e)
        return jsonify({
            'success': False,
            'error': 'Unable to create assignment.'
        }), 500
    
@classroom_bp.route('/assignment-status', methods=['GET'])
def get_assignment_status():
    course_id = request.args.get('course_id')
    coursework_id = request.args.get('coursework_id')
    student_id = request.args.get('student_id')

    if not course_id or not coursework_id or not student_id:
        return jsonify({
            'success': False,
            'error': (
                'course_id, coursework_id and student_id '
                'are required.'
            )
        }), 400

    try:
        result = classroom_service.get_student_assignment_status(
            course_id=course_id,
            coursework_id=coursework_id,
            classroom_student_id=student_id
        )

        return jsonify(result), (
            200 if result.get('success') else 400
        )

    except Exception as e:
        print("Assignment Status Error:", e)
        return jsonify({
            'success': False,
            'error': 'Unable to check assignment status.'
        }), 500


@classroom_bp.route('/publish-assignment', methods=['POST'])
def publish_assignment():
    from flask import session
    from datetime import datetime
    from models.user import User
    from models.intervention_tracking import InterventionTracking
    from database import db

    # 1. Check faculty login
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            'success': False,
            'error': 'Please log in first.'
        }), 401

    user = db.session.get(User, user_id)

    if not user or user.role not in ['Faculty', 'Admin']:
        return jsonify({
            'success': False,
            'error': 'Faculty or Admin access required.'
        }), 403

    data = request.get_json(silent=True) or {}

    tracking_id = data.get('tracking_id')
    course_id = data.get('course_id')
    coursework_id = data.get('coursework_id')

    if not tracking_id or not course_id or not coursework_id:
        return jsonify({
            'success': False,
            'error': 'tracking_id, course_id and coursework_id are required.'
        }), 400

    # 2. Find the intervention
    record = db.session.get(InterventionTracking, tracking_id)

    if not record:
        return jsonify({
            'success': False,
            'error': 'Intervention record not found.'
        }), 404

    # 3. Only approved assignments can be published
    if record.faculty_approval_status != 'APPROVED':
        return jsonify({
            'success': False,
            'error': 'Faculty approval is required before publishing.',
            'approval_status': record.faculty_approval_status
        }), 403

    # 4. Only the approving faculty or an Admin can publish
    if (
        user.role != 'Admin'
        and record.faculty_approved_by != user.id
    ):
        return jsonify({
            'success': False,
            'error': 'Only the approving faculty or an Admin can publish.'
        }), 403

    # 5. Verify the assignment belongs to this intervention
    if (
        str(record.classroom_course_id or '') != str(course_id)
        or str(record.classroom_coursework_id or '') != str(coursework_id)
    ):
        return jsonify({
            'success': False,
            'error': 'Assignment IDs do not match this intervention.'
        }), 400

    try:
        result = classroom_service.publish_assignment(
            course_id=str(course_id),
            coursework_id=str(coursework_id)
        )

        if result.get('success'):
            record.classroom_status = 'PUBLISHED'
            db.session.commit()

        return jsonify(result), (
            200 if result.get('success') else 400
        )

    except Exception as error:
        db.session.rollback()
        print("Publish Assignment Error:", error)

        return jsonify({
            'success': False,
            'error': 'Unable to publish assignment.'
        }), 500
