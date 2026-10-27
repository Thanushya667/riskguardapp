
from datetime import datetime, timedelta

from config import Config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleClassroomService:
    """Google Classroom integration for RiskGuard."""

    def __init__(self):
        self.credentials = None

    # ---------------------------------------------------------
    # CONFIGURATION AND AUTHENTICATION
    # ---------------------------------------------------------

    @staticmethod
    def is_configured():
        return bool(
            Config.GOOGLE_CLIENT_ID
            and Config.GOOGLE_CLIENT_SECRET
        )

    def set_credentials(self, credentials):
        self.credentials = credentials

    def is_authenticated(self):
        return (
            self.credentials is not None
            and self.credentials.valid
        )

    def _get_service(self):
        if not self.is_authenticated():
            raise Exception(
                "Google Classroom is not authenticated. "
                "Please connect Google Classroom first."
            )

        return build(
            "classroom",
            "v1",
            credentials=self.credentials,
            cache_discovery=False
        )

    def get_status(self):
        configured = self.is_configured()
        authenticated = self.is_authenticated()

        return {
            "configured": configured,
            "authenticated": authenticated,
            "message": (
                "Google Classroom connected successfully."
                if authenticated
                else (
                    "Google Classroom is configured but not authenticated."
                    if configured
                    else "Google Classroom API is not configured."
                )
            ),
            "classroom_url": "https://classroom.google.com",
            "client_id": (
                Config.GOOGLE_CLIENT_ID if configured else None
            )
        }

    # ---------------------------------------------------------
    # GET ACTIVE COURSES
    # ---------------------------------------------------------

    def get_courses(self):
        service = self._get_service()

        courses = []
        page_token = None

        while True:
            params = {
                "courseStates": "ACTIVE",
                "pageSize": 100
            }

            if page_token:
                params["pageToken"] = page_token

            response = (
                service.courses()
                .list(**params)
                .execute()
            )

            courses.extend(response.get("courses", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return [
            {
                "id": course.get("id"),
                "name": course.get("name"),
                "section": course.get("section", ""),
                "room": course.get("room", ""),
                "course_state": course.get("courseState")
            }
            for course in courses
        ]

    # ---------------------------------------------------------
    # GET STUDENTS ENROLLED IN A COURSE
    # ---------------------------------------------------------

    def get_course_students(self, course_id):
        if not course_id:
            raise ValueError(
                "A Google Classroom course ID is required."
            )

        service = self._get_service()

        students = []
        page_token = None

        while True:
            params = {
                "courseId": str(course_id),
                "pageSize": 100
            }

            if page_token:
                params["pageToken"] = page_token

            response = (
                service.courses()
                .students()
                .list(**params)
                .execute()
            )

            students.extend(response.get("students", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return students

    # ---------------------------------------------------------
    # FIND STUDENT BY EMAIL
    # ---------------------------------------------------------

    def find_student_by_email(self, course_id, student_email):
        if not course_id or not student_email:
            return None

        target_email = student_email.strip().lower()
        students = self.get_course_students(course_id)

        for student in students:
            profile = student.get("profile", {})
            email = profile.get("emailAddress", "")

            if email and email.strip().lower() == target_email:
                return {
                    "student_id": student.get("userId"),
                    "email": email,
                    "name": profile.get("name", {}).get(
                        "fullName", ""
                    )
                }

        return None

    # ---------------------------------------------------------
    # FIND STUDENT BY CLASSROOM STUDENT ID
    # ---------------------------------------------------------

    def find_student_by_id(self, course_id, student_id):
        if not course_id or not student_id:
            return None

        students = self.get_course_students(course_id)

        for student in students:
            if str(student.get("userId")) == str(student_id):
                profile = student.get("profile", {})

                return {
                    "student_id": student.get("userId"),
                    "email": profile.get("emailAddress", ""),
                    "name": profile.get("name", {}).get(
                        "fullName", ""
                    )
                }

        return None

    # ---------------------------------------------------------
    # CREATE INDIVIDUAL DRAFT ASSIGNMENT
    # ---------------------------------------------------------

    def create_high_risk_assignment(
        self,
        course_id,
        student_name=None,
        risk_factors=None,
        recommendations=None,
        student_email=None,
        student_id=None
    ):
        """Create a draft assignment for one enrolled student."""

        if not course_id:
            return {
                "success": False,
                "message": "A Google Classroom course ID is required."
            }

        if not student_id and not student_email:
            return {
                "success": False,
                "message": "Student email or student ID is required."
            }

        try:
            service = self._get_service()

            # Prefer student ID when provided.
            if student_id:
                student = self.find_student_by_id(
                    course_id=course_id,
                    student_id=student_id
                )
            else:
                student = self.find_student_by_email(
                    course_id=course_id,
                    student_email=student_email
                )

            if not student:
                return {
                    "success": False,
                    "message": (
                        "Student was not found in the selected "
                        "Google Classroom course. Check the student "
                        "ID or email and course enrollment."
                    )
                }

            classroom_student_id = student.get("student_id")

            if not classroom_student_id:
                return {
                    "success": False,
                    "message": (
                        "A valid Classroom student ID was not returned."
                    )
                }

            # Due date: seven days from today.
            due_date = datetime.now().date() + timedelta(days=7)

            factors = risk_factors or []
            actions = recommendations or []

            risk_factor_text = (
                "\n".join(f"- {factor}" for factor in factors)
                if factors
                else "- Review your academic progress."
            )

            recommendation_text = (
                "\n".join(f"- {item}" for item in actions)
                if actions
                else (
                    "- Meet your faculty mentor.\n"
                    "- Follow a regular study schedule.\n"
                    "- Monitor your academic progress."
                )
            )

            display_name = (
                student_name or student.get("name") or "Student"
            )

            # Neutral test description.
            description = (
                f"Dear {display_name},\n\n"
                "This is an academic improvement activity created "
                "to test the RiskGuard system.\n\n"
                "Please review the following improvement activities.\n\n"
                f"AREAS TO IMPROVE\n{risk_factor_text}\n\n"
                f"RECOMMENDED ACTIONS\n{recommendation_text}\n\n"
                "Please discuss your progress with your faculty mentor.\n\n"
                "Created by the RiskGuard Academic Risk Prediction "
                "and Intervention System."
            )

            coursework = {
                "title": "Personalized Academic Improvement Plan",
                "description":"description",
                "workType": "ASSIGNMENT",
                "state": "DRAFT",
                "assigneeMode": "INDIVIDUAL_STUDENTS",
                "individualStudentsOptions": {
                    "studentIds": [str(classroom_student_id)]
                },
                "dueDate": {
                    "year": due_date.year,
                    "month": due_date.month,
                    "day": due_date.day
                },
                "dueTime": {
                    "hours": 23,
                    "minutes": 59,
                    "seconds": 0,
                    "nanos": 0
                },
                "maxPoints": 100,
                "submissionModificationMode": (
                    "MODIFIABLE_UNTIL_TURNED_IN"
                )
            }

            created = (
                service.courses()
                .courseWork()
                .create(
                    courseId=str(course_id),
                    body=coursework
                )
                .execute()
            )

            return {
                "success": True,
                "message": "Assignment created successfully.",
                "course_id": str(course_id),
                "coursework_id": created.get("id"),
                "student_id": classroom_student_id,
                "student_email": (
                    student.get("email") or student_email or ""
                ),
                "student_name": display_name,
                "title": created.get("title"),
                "state": created.get("state"),
                "due_date": due_date.isoformat(),
                "alternate_link": created.get("alternateLink")
            }

        except HttpError as error:
            print(f"Google Classroom API error: {error}")

            return {
                "success": False,
                "message": (
                    "Google Classroom API error while creating "
                    "the assignment."
                ),
                "error": str(error)
            }

        except Exception as error:
            print(f"Assignment creation error: {error}")

            return {
                "success": False,
                "message": (
                    "Failed to create the Google Classroom assignment."
                ),
                "error": str(error)
            }
        
    # ---------------------------------------------------------
    # PUBLISH AN EXISTING DRAFT ASSIGNMENT
    # ---------------------------------------------------------

    def publish_assignment(self, course_id, coursework_id):
        if not course_id or not coursework_id:
            return {
                "success": False,
                "message": "Course ID and coursework ID are required."
            }

        try:
            service = self._get_service()

            # Confirm the assignment exists and belongs to this course.
            assignment = (
                service.courses()
                .courseWork()
                .get(
                    courseId=str(course_id),
                    id=str(coursework_id)
                )
                .execute()
            )

            if assignment.get("state") == "PUBLISHED":
                return {
                    "success": True,
                    "message": "Assignment is already published.",
                    "course_id": str(course_id),
                    "coursework_id": str(coursework_id),
                    "state": "PUBLISHED"
                }

            if assignment.get("state") != "DRAFT":
                return {
                    "success": False,
                    "message": (
                        "Only a draft assignment can be published."
                    ),
                    "state": assignment.get("state")
                }

            updated = (
                service.courses()
                .courseWork()
                .patch(
                    courseId=str(course_id),
                    id=str(coursework_id),
                    updateMask="state",
                    body={"state": "PUBLISHED"}
                )
                .execute()
            )

            return {
                "success": updated.get("state") == "PUBLISHED",
                "message": (
                    "Assignment published successfully."
                    if updated.get("state") == "PUBLISHED"
                    else "Google Classroom did not confirm publication."
                ),
                "course_id": str(course_id),
                "coursework_id": str(coursework_id),
                "state": updated.get("state")
            }

        except HttpError as error:
            print(f"Publish Assignment API Error: {error}")
            return {
                "success": False,
                "message": "Google Classroom could not publish the assignment.",
                "error": str(error)
            }

        except Exception as error:
            print(f"Publish Assignment Error: {error}")
            return {
                "success": False,
                "message": "Failed to publish the assignment.",
                "error": str(error)
            }


    # ---------------------------------------------------------
    # CHECK STUDENT ASSIGNMENT SUBMISSION STATUS
    # ---------------------------------------------------------

    def get_student_assignment_status(
        self,
        course_id,
        coursework_id,
        classroom_student_id
    ):
        """Retrieve submission state, not whether the student viewed it."""

        if not course_id or not coursework_id:
            return {
                "success": False,
                "error": "Course ID and coursework ID are required."
            }

        if not classroom_student_id:
            return {
                "success": False,
                "error": "A Classroom student ID is required."
            }

        try:
            service = self._get_service()

            response = (
                service.courses()
                .courseWork()
                .studentSubmissions()
                .list(
                    courseId=str(course_id),
                    courseWorkId=str(coursework_id),
                    userId=str(classroom_student_id),
                    pageSize=100
                )
                .execute()
            )

            submissions = response.get("studentSubmissions", [])

            if not submissions:
                return {
                    "success": True,
                    "accessed": None,
                    "access_status_note": (
                        "Submission data cannot confirm whether "
                        "the student opened or viewed the assignment."
                    ),
                    "submitted": False,
                    "state": "NO_SUBMISSION_RECORD",
                    "update_time": None,
                    "submission_id": None,
                    "student_id": str(classroom_student_id),
                    "course_id": str(course_id),
                    "coursework_id": str(coursework_id)
                }

            submission = next(
                (
                    item for item in submissions
                    if str(item.get("userId"))
                    == str(classroom_student_id)
                ),
                submissions[0]
            )

            state = submission.get("state", "NEW")
            submitted = state in ("TURNED_IN", "RETURNED")

            return {
                "success": True,
                "accessed": None,
                "access_status_note": (
                    "Google Classroom submission state cannot "
                    "confirm whether the assignment was viewed."
                ),
                "submitted": submitted,
                "state": state,
                "update_time": submission.get("updateTime"),
                "submission_id": submission.get("id"),
                "student_id": submission.get("userId"),
                "course_id": str(course_id),
                "coursework_id": str(coursework_id)
            }

        except HttpError as error:
            print(f"Submission status API error: {error}")

            return {
                "success": False,
                "error": (
                    "Google Classroom API error while checking "
                    "assignment status."
                ),
                "details": str(error)
            }

        except Exception as error:
            print(f"Submission status error: {error}")

            return {
                "success": False,
                "error": (
                    "Unable to retrieve the student's assignment status."
                ),
                "details": str(error)
            }


# -------------------------------------------------------------
# GLOBAL SERVICE OBJECT
# -------------------------------------------------------------

classroom_service = GoogleClassroomService()

