
import os
import secrets
from datetime import datetime
from urllib.parse import urljoin

from flask import current_app

from database import db
from models.intervention_tracking import InterventionTracking
from services.email.email_service import email_service
from services.google_classroom.classroom_service import classroom_service


class InterventionService:

    @staticmethod
    def create_high_risk_intervention(
        student,
        prediction_result,
        course_id=None,
        prediction_date=None
    ):
        risk_level = prediction_result.get("risk_level")

        if risk_level != "High Risk":
            return {
                "success": True,
                "intervention_created": False,
                "message": "Intervention is created only for High Risk students."
            }

        risk_factors = prediction_result.get("risk_factors", [])
        recommendations = prediction_result.get("recommendations", [])

        # Create a unique reference for email acknowledgement and reply matching.
        token = secrets.token_urlsafe(32)

        intervention = InterventionTracking(
            student_id=student.id,
            risk_level=risk_level,
            email_status="PENDING",
            email_acknowledged=False,
            acknowledgement_token=token,
            email_reply_status="AWAITING_REPLY",
            classroom_status="NOT_CREATED",
            assignment_submitted=False
        )

        try:
            db.session.add(intervention)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        # Build the public base URL. Set APP_BASE_URL in .env for deployment.
        base_url = (
            os.getenv("APP_BASE_URL")
            or current_app.config.get("BASE_URL")
            or "http://127.0.0.1:5000"
        ).rstrip("/") + "/"

        acknowledgement_url = urljoin(
            base_url,
            f"api/interventions/acknowledge/{token}"
        )

        result = {
            "success": True,
            "intervention_created": True,
            "intervention_id": intervention.id,
            "student_id": student.id,
            "student_name": student.student_name,
            "risk_level": risk_level,
            "email_status": "NOT_ATTEMPTED",
            "email_message": None,
            "classroom_status": "NOT_ATTEMPTED",
            "classroom_result": None
        }

        # Send email with acknowledgement URL and tracking reference.
        try:
            status, message = email_service.send_risk_alert_email(
                student_name=student.student_name,
                student_email=student.email,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                prediction_date=(
                    prediction_date
                    or datetime.utcnow().strftime("%Y-%m-%d")
                ),
                acknowledgement_url=acknowledgement_url,
                tracking_reference=str(intervention.id)
            )

            intervention.email_status = status
            if status == "SENT":
                intervention.email_sent_at = datetime.utcnow()

            result["email_status"] = status
            result["email_message"] = message

        except Exception as error:
            intervention.email_status = "FAILED"
            result["email_status"] = "FAILED"
            result["email_message"] = str(error)

        # Create the Classroom assignment and persist its IDs.
        if not course_id:
            intervention.classroom_status = "COURSE_NOT_SELECTED"
            result["classroom_status"] = "COURSE_NOT_SELECTED"
            result["classroom_result"] = {
                "success": False,
                "message": "Select a Google Classroom course."
            }
        else:
            try:
                classroom_result = classroom_service.create_high_risk_assignment(
                    course_id=course_id,
                    student_email=student.email,
                    student_name=student.student_name,
                    risk_factors=risk_factors,
                    recommendations=recommendations
                )

                result["classroom_result"] = classroom_result

                if classroom_result.get("success"):
                    intervention.classroom_status = "CREATED"
                    intervention.classroom_course_id = str(
                        classroom_result.get("course_id") or course_id
                    )
                    intervention.classroom_coursework_id = str(
                        classroom_result.get("coursework_id") or ""
                    ) or None
                    intervention.classroom_student_id = str(
                        classroom_result.get("student_id") or ""
                    ) or None
                    result["classroom_status"] = "CREATED"
                else:
                    intervention.classroom_status = "FAILED"
                    result["classroom_status"] = "FAILED"

            except Exception as error:
                intervention.classroom_status = "FAILED"
                result["classroom_status"] = "FAILED"
                result["classroom_result"] = {
                    "success": False,
                    "message": str(error)
                }

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            result["success"] = False
            result["database_error"] = "Could not save final intervention status."

        return result


intervention_service = InterventionService()
