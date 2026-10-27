
from datetime import datetime
from database import db


class InterventionTracking(db.Model):
    __tablename__ = 'intervention_tracking'

    id = db.Column(db.Integer, primary_key=True)

    # RiskGuard student
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Risk information
    risk_level = db.Column(
        db.String(50),
        nullable=False
    )

    # Email tracking
    email_status = db.Column(
        db.String(50),
        default='PENDING'
    )

    email_sent_at = db.Column(
        db.DateTime,
        nullable=True
    )

    email_acknowledged = db.Column(
        db.Boolean,
        default=False
    )

    email_acknowledged_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Email reply tracking
    email_reply_status = db.Column(
        db.String(50),
        default='AWAITING_REPLY',
        nullable=False
    )

    email_reply_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Unique token used for email acknowledgement
    acknowledgement_token = db.Column(
        db.String(200),
        unique=True,
        nullable=False,
        index=True
    )

    # Faculty approval tracking
    faculty_approval_status = db.Column(
        db.String(30),
        nullable=False,
        default='PENDING'
    )

    faculty_approved_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    faculty_approved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Google Classroom
    classroom_course_id = db.Column(
        db.String(100),
        nullable=True
    )

    classroom_coursework_id = db.Column(
        db.String(100),
        nullable=True
    )

    classroom_student_id = db.Column(
        db.String(100),
        nullable=True
    )

    classroom_status = db.Column(
        db.String(50),
        default='NOT_CREATED'
    )

    classroom_accessed = db.Column(
        db.Boolean,
        default=False
    )

    classroom_accessed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Assignment submission tracking
    assignment_submitted = db.Column(
        db.Boolean,
        default=False
    )

    assignment_submitted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Reminder tracking
    reminder_sent = db.Column(
        db.Boolean,
        default=False
    )

    reminder_sent_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Student relationship
    student = db.relationship(
        'Student',
        backref=db.backref(
            'intervention_tracking',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    # Convert intervention record to JSON-compatible dictionary
    def to_dict(self):
        return {
            'id': self.id,

            # Student details
            'student_id': self.student_id,
            'student_name': (
                self.student.student_name if self.student else None
            ),
            'register_number': (
                self.student.register_number if self.student else None
            ),
            'email': (
                self.student.email if self.student else None
            ),

            # Risk information
            'risk_level': self.risk_level,

            # Email status
            'email_status': self.email_status,
            'email_sent_at': (
                self.email_sent_at.strftime('%Y-%m-%d %H:%M')
                if self.email_sent_at else None
            ),

            # Email acknowledgement
            'email_acknowledged': self.email_acknowledged,
            'email_acknowledged_at': (
                self.email_acknowledged_at.strftime('%Y-%m-%d %H:%M')
                if self.email_acknowledged_at else None
            ),

            # Email reply tracking
            'email_reply_status': self.email_reply_status,
            'email_reply_at': (
                self.email_reply_at.strftime('%Y-%m-%d %H:%M')
                if self.email_reply_at else None
            ),

            # Faculty approval tracking
            'faculty_approval_status': self.faculty_approval_status,
            'faculty_approved_by': self.faculty_approved_by,
            'faculty_approved_at': (
                self.faculty_approved_at.strftime('%Y-%m-%d %H:%M')
                if self.faculty_approved_at else None
            ),

            # Google Classroom details
            'classroom_course_id': self.classroom_course_id,
            'classroom_coursework_id': self.classroom_coursework_id,
            'classroom_student_id': self.classroom_student_id,

            # Classroom status
            'classroom_status': self.classroom_status,
            'classroom_accessed': self.classroom_accessed,
            'classroom_accessed_at': (
                self.classroom_accessed_at.strftime('%Y-%m-%d %H:%M')
                if self.classroom_accessed_at else None
            ),

            # Assignment submission
            'assignment_submitted': self.assignment_submitted,
            'assignment_submitted_at': (
                self.assignment_submitted_at.strftime('%Y-%m-%d %H:%M')
                if self.assignment_submitted_at else None
            ),

            # Reminder details
            'reminder_sent': self.reminder_sent,
            'reminder_sent_at': (
                self.reminder_sent_at.strftime('%Y-%m-%d %H:%M')
                if self.reminder_sent_at else None
            ),

            # Record timestamps
            'created_at': (
                self.created_at.strftime('%Y-%m-%d %H:%M')
                if self.created_at else None
            ),

            'updated_at': (
                self.updated_at.strftime('%Y-%m-%d %H:%M')
                if self.updated_at else None
            )
        }

