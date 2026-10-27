from datetime import datetime
from database import db

class RiskAlert(db.Model):
    __tablename__ = 'risk_alerts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    risk_level = db.Column(db.String(50), nullable=False)
    alert_message = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_status = db.Column(db.String(50), default='NOT_CONFIGURED', nullable=False)
    # email_status values: 'PENDING', 'SENT', 'FAILED', 'NOT_CONFIGURED'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else 'Unknown',
            'student_email': self.student.email if self.student else 'Unknown',
            'student_reg_no': self.student.register_number if self.student else 'Unknown',
            'department': self.student.department if self.student else 'Unknown',
            'risk_level': self.risk_level,
            'alert_message': self.alert_message,
            'recommendation': self.recommendation,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'email_status': self.email_status
        }
