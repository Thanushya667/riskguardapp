
import imaplib
import re
import secrets
from models.student import Student

from datetime import datetime
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr

from flask import (
    Blueprint,
    jsonify,
    request,
    render_template_string,
    session,
)

from database import db
from config import Config
from models.user import User
from models.intervention_tracking import InterventionTracking
from services.google_classroom.classroom_service import classroom_service


intervention_bp = Blueprint(
    "intervention",
    __name__,
    url_prefix="/api/interventions"
)


# --------------------------------------------------
# AUTHORIZATION
# --------------------------------------------------

def get_authorized_faculty():
    user_id = session.get("user_id")

    if not user_id:
        return None, (
            jsonify({
                "success": False,
                "message": "Please log in first."
            }),
            401
        )

    user = db.session.get(User, user_id)

    if not user or user.role not in ["Faculty", "Admin"]:
        return None, (
            jsonify({
                "success": False,
                "message": "Faculty or Admin access required."
            }),
            403
        )

    return user, None


# --------------------------------------------------
# 1. EMAIL ACKNOWLEDGEMENT
# Public endpoint: requires a valid, unguessable token
# --------------------------------------------------

@intervention_bp.route("/acknowledge/<token>", methods=["GET"])
def acknowledge_intervention(token):
    try:
        record = InterventionTracking.query.filter_by(
            acknowledgement_token=token
        ).first()

        if not record:
            return render_template_string("""
                <html>
                <body style="font-family:Arial;text-align:center;padding:40px">
                    <h2>Invalid acknowledgement link</h2>
                    <p>This link is invalid or unavailable.</p>
                </body>
                </html>
            """), 404

        if not record.email_acknowledged:
            record.email_acknowledged = True
            record.email_acknowledged_at = datetime.utcnow()
            db.session.commit()

        return render_template_string("""
            <html>
            <head><title>RiskGuard Acknowledgement</title></head>
            <body style="font-family:Arial;text-align:center;padding:40px">
                <h2>Thank you!</h2>
                <p>Your acknowledgement has been recorded successfully.</p>
                <p>You may close this page.</p>
            </body>
            </html>
        """), 200

    except Exception as error:
        db.session.rollback()
        print("Acknowledgement error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to record acknowledgement."
        }), 500


# --------------------------------------------------
# 2. CHECK A SINGLE CLASSROOM ASSIGNMENT
# Faculty/Admin only
# --------------------------------------------------

@intervention_bp.route("/classroom-status", methods=["GET"])
def get_classroom_status():
    _, auth_error = get_authorized_faculty()

    if auth_error:
        return auth_error

    course_id = request.args.get("course_id")
    coursework_id = request.args.get("coursework_id")
    student_id = request.args.get("student_id")

    if not all([course_id, coursework_id, student_id]):
        return jsonify({
            "success": False,
            "message": (
                "course_id, coursework_id and student_id are required."
            )
        }), 400

    try:
        result = classroom_service.get_student_assignment_status(
            course_id=course_id,
            coursework_id=coursework_id,
            classroom_student_id=student_id
        )

        return jsonify(result), (
            200 if result.get("success") else 502
        )

    except Exception as error:
        print("Classroom status error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve Classroom status."
        }), 500


# --------------------------------------------------
# 3. FACULTY DASHBOARD STATUS
# Faculty/Admin only
# --------------------------------------------------

@intervention_bp.route("/faculty-status", methods=["GET"])
def get_faculty_intervention_status():
    _, auth_error = get_authorized_faculty()

    if auth_error:
        return auth_error

    try:
        records = (
            InterventionTracking.query
            .order_by(InterventionTracking.created_at.desc())
            .all()
        )

        rows = [record.to_dict() for record in records]

        summary = {
            "total_interventions": len(rows),

            "pending_faculty_approval": sum(
                1 for row in rows
                if row.get("faculty_approval_status", "PENDING")
                == "PENDING"
            ),

            "approved_interventions": sum(
                1 for row in rows
                if row.get("faculty_approval_status") == "APPROVED"
            ),

            "rejected_interventions": sum(
                1 for row in rows
                if row.get("faculty_approval_status") == "REJECTED"
            ),

            "emails_sent": sum(
                1 for row in rows
                if row.get("email_status") == "SENT"
            ),

            "emails_failed": sum(
                1 for row in rows
                if row.get("email_status") == "FAILED"
            ),

            "awaiting_acknowledgement": sum(
                1 for row in rows
                if row.get("email_status") == "SENT"
                and not row.get("email_acknowledged")
            ),

            "awaiting_email_reply": sum(
                1 for row in rows
                if row.get("email_status") == "SENT"
                and row.get("email_reply_status") != "REPLIED"
            ),

            "assignments_submitted": sum(
                1 for row in rows
                if row.get("assignment_submitted")
            ),

            "assignments_pending": sum(
                1 for row in rows
                if row.get("classroom_status") == "PUBLISHED"
                and not row.get("assignment_submitted")
            )
        }

        return jsonify({
            "success": True,
            "count": len(rows),
            "summary": summary,
            "interventions": rows
        }), 200

    except Exception as error:
        print("Faculty status error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve faculty intervention status."
        }), 500


# --------------------------------------------------
# 4. SYNC GOOGLE CLASSROOM SUBMISSION STATUS
# Faculty/Admin only
# Checks published assignments, not drafts
# --------------------------------------------------

@intervention_bp.route("/sync-classroom-status", methods=["POST"])
def sync_classroom_status():
    _, auth_error = get_authorized_faculty()

    if auth_error:
        return auth_error

    try:
        records = InterventionTracking.query.filter(
            InterventionTracking.classroom_status.in_(
                ["PUBLISHED", "SUBMITTED"]
            ),
            InterventionTracking.classroom_course_id.isnot(None),
            InterventionTracking.classroom_coursework_id.isnot(None),
            InterventionTracking.classroom_student_id.isnot(None)
        ).all()

        newly_submitted = 0
        checked = 0
        errors = []

        for record in records:
            try:
                status = classroom_service.get_student_assignment_status(
                    course_id=record.classroom_course_id,
                    coursework_id=record.classroom_coursework_id,
                    classroom_student_id=record.classroom_student_id
                )

                checked += 1

                if not status.get("success"):
                    errors.append({
                        "intervention_id": record.id,
                        "message": status.get(
                            "error",
                            "Classroom status unavailable."
                        )
                    })
                    continue

                submitted = bool(status.get("submitted"))

                if submitted:
                    if not record.assignment_submitted:
                        record.assignment_submitted_at = datetime.utcnow()
                        newly_submitted += 1

                    record.assignment_submitted = True
                    record.classroom_status = "SUBMITTED"

                else:
                    record.assignment_submitted = False
                    record.assignment_submitted_at = None
                    record.classroom_status = "PUBLISHED"

            except Exception as error:
                errors.append({
                    "intervention_id": record.id,
                    "message": str(error)
                })

        db.session.commit()

        return jsonify({
            "success": True,
            "records_found": len(records),
            "checked": checked,
            "newly_submitted": newly_submitted,
            "errors": errors
        }), 200

    except Exception as error:
        db.session.rollback()
        print("Classroom sync error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to sync Classroom submission status."
        }), 500


# --------------------------------------------------
# 5. SYNC EMAIL REPLIES THROUGH IMAP
# Faculty/Admin only
# --------------------------------------------------

@intervention_bp.route("/sync-email-replies", methods=["POST"])
def sync_email_replies():
    _, auth_error = get_authorized_faculty()

    if auth_error:
        return auth_error

    host = getattr(Config, "IMAP_HOST", None)
    port = getattr(Config, "IMAP_PORT", 993)
    username = getattr(Config, "IMAP_USERNAME", None)
    password = getattr(Config, "IMAP_PASSWORD", None)

    if not all([host, username, password]):
        return jsonify({
            "success": False,
            "message": "IMAP mailbox settings are not configured."
        }), 503

    mailbox = None
    updated = 0
    scanned = 0

    try:
        mailbox = imaplib.IMAP4_SSL(host, int(port))
        mailbox.login(username, password)

        result, _ = mailbox.select("INBOX", readonly=True)

        if result != "OK":
            return jsonify({
                "success": False,
                "message": "Unable to open the inbox."
            }), 502

        result, data = mailbox.search(None, "ALL")

        if result != "OK" or not data or not data[0]:
            return jsonify({
                "success": True,
                "messages_scanned": 0,
                "replies_detected": 0
            }), 200

        message_ids = data[0].split()

        for message_id in message_ids[-500:]:
            result, parts = mailbox.fetch(
                message_id,
                "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])"
            )

            if result != "OK":
                continue

            raw_header = next(
                (
                    part[1]
                    for part in parts
                    if isinstance(part, tuple) and part[1]
                ),
                None
            )

            if not raw_header:
                continue

            msg = message_from_bytes(raw_header)
            scanned += 1

            try:
                subject = str(
                    make_header(
                        decode_header(msg.get("Subject", ""))
                    )
                )
            except Exception:
                subject = msg.get("Subject", "")

            sender_email = parseaddr(
                msg.get("From", "")
            )[1].strip().lower()

            match = re.search(
                r"\[RiskGuard Ref:\s*(\d+)\]",
                subject,
                re.IGNORECASE
            )

            if not match:
                continue

            record = db.session.get(
                InterventionTracking,
                int(match.group(1))
            )

            if not record:
                continue

            if record.email_reply_status == "REPLIED":
                continue

            expected_email = ""

            if record.student and record.student.email:
                expected_email = record.student.email.strip().lower()

            if not expected_email or sender_email != expected_email:
                continue

            record.email_reply_status = "REPLIED"
            record.email_reply_at = datetime.utcnow()
            updated += 1

        db.session.commit()

        return jsonify({
            "success": True,
            "messages_scanned": scanned,
            "replies_detected": updated,
            "message": "Inbox reply scan completed."
        }), 200

    except Exception as error:
        db.session.rollback()
        print("Email reply sync error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to check email replies."
        }), 500

    finally:
        if mailbox is not None:
            try:
                mailbox.logout()
            except Exception:
                pass
            
# --------------------------------------------------
# 6. CREATE HIGH-RISK CLASSROOM DRAFT
# Faculty/Admin only; never publishes automatically
# --------------------------------------------------

@intervention_bp.route("/create-classroom-draft", methods=["POST"])
def create_classroom_draft():
    _, auth_error = get_authorized_faculty()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    classroom_student_id = data.get("classroom_student_id")

    if not all([student_id, course_id, classroom_student_id]):
        return jsonify({
            "success": False,
            "message": (
                "student_id, course_id and classroom_student_id "
                "are required."
            )
        }), 400

    try:
        student = db.session.get(Student, student_id)

        if not student:
            return jsonify({
                "success": False,
                "message": "RiskGuard student was not found."
            }), 404

        if student.risk_level != "High Risk":
            return jsonify({
                "success": False,
                "message": "Only High Risk students qualify."
            }), 400

        course_id = str(course_id).strip()
        classroom_student_id = str(classroom_student_id).strip()

        # Prevent duplicate drafts for the same student and course.
        existing = InterventionTracking.query.filter_by(
            student_id=student.id,
            classroom_course_id=course_id
        ).all()

        for record in existing:
            if record.classroom_coursework_id and record.classroom_status in (
                "CREATED", "PUBLISHED", "SUBMITTED"
            ):
                return jsonify({
                    "success": False,
                    "message": "An assignment already exists for this student and course.",
                    "intervention_id": record.id,
                    "coursework_id": record.classroom_coursework_id
                }), 409

        # Verify the supplied Classroom ID by creating an individual draft.
        # The Classroom service checks whether this student is enrolled.
        token = secrets.token_urlsafe(32)

        intervention = InterventionTracking(
            student_id=student.id,
            risk_level=student.risk_level,
            acknowledgement_token=token,
            email_status="NOT_SENT",
            email_acknowledged=False,
            email_reply_status="AWAITING_REPLY",
            classroom_status="CREATING",
            faculty_approval_status="PENDING",
            assignment_submitted=False,
            classroom_course_id=course_id,
            classroom_student_id=classroom_student_id
        )

        db.session.add(intervention)
        db.session.commit()

        risk_factors = []

        if student.attendance_percentage is not None and student.attendance_percentage < 75:
            risk_factors.append(
                f"Attendance: {student.attendance_percentage}%"
            )

        if student.assignment_score is not None and student.assignment_score < 50:
            risk_factors.append(
                f"Assignment score: {student.assignment_score}"
            )

        if student.cia_marks is not None and student.cia_marks < 50:
            risk_factors.append(
                f"CIA marks: {student.cia_marks}"
            )

        recommendations = [
            "Follow a regular study schedule.",
            "Complete pending assignments.",
            "Meet your faculty mentor to review progress."
        ]

        result = classroom_service.create_high_risk_assignment(
            course_id=course_id,
            student_id=classroom_student_id,
            student_name=student.student_name,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

        if not result.get("success"):
            intervention.classroom_status = "FAILED"
            db.session.commit()

            return jsonify({
                "success": False,
                "message": result.get(
                    "message",
                    "Could not create the Classroom draft."
                ),
                "intervention_id": intervention.id
            }), 400

        intervention.classroom_course_id = str(
            result.get("course_id") or course_id
        )
        intervention.classroom_coursework_id = str(
            result.get("coursework_id") or ""
        ) or None
        intervention.classroom_student_id = str(
            result.get("student_id") or classroom_student_id
        )
        intervention.classroom_status = "CREATED"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Draft created. Faculty approval is still required before publishing.",
            "intervention_id": intervention.id,
            "student_name": student.student_name,
            "course_id": intervention.classroom_course_id,
            "coursework_id": intervention.classroom_coursework_id,
            "classroom_student_id": intervention.classroom_student_id,
            "classroom_status": intervention.classroom_status,
            "faculty_approval_status": intervention.faculty_approval_status,
            "assignment": result
        }), 201

    except Exception as error:
        db.session.rollback()
        print("Create Classroom draft error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to create the Classroom draft. Check the server log."
        }), 500

