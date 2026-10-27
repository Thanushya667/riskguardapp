from datetime import datetime
from database import db

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    risk_level = db.Column(db.String(50), nullable=False)
    risk_probability = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else 'Unknown',
            'register_number': self.student.register_number if self.student else 'Unknown',
            'risk_level': self.risk_level,
            'risk_probability': round(self.risk_probability, 1),
            'prediction_date': self.prediction_date.strftime('%Y-%m-%d %H:%M') if self.prediction_date else None,
            'details': self.details
        }
