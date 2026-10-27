from datetime import datetime
from database import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    register_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    department = db.Column(db.String(100), nullable=False, index=True)
    
    # Academic parameters
    attendance_percentage = db.Column(db.Float, nullable=False)
    previous_semester_cgpa = db.Column(db.Float, nullable=False)
    assignment_score = db.Column(db.Float, nullable=False)
    cia_marks = db.Column(db.Float, nullable=False)
    laboratory_performance = db.Column(db.Float, nullable=False)
    subject_wise_marks = db.Column(db.Float, nullable=False)
    
    # Calculated / ML metrics
    overall_performance = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(50), nullable=False, index=True)  # 'Low Risk', 'Medium Risk', 'High Risk'
    risk_probability = db.Column(db.Float, nullable=False)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = db.relationship('RiskAlert', backref='student', cascade='all, delete-orphan', lazy=True)
    history = db.relationship('PredictionHistory', backref='student', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'register_number': self.register_number,
            'email': self.email,
            'department': self.department,
            'attendance_percentage': round(self.attendance_percentage, 1),
            'previous_semester_cgpa': round(self.previous_semester_cgpa, 2),
            'assignment_score': round(self.assignment_score, 1),
            'cia_marks': round(self.cia_marks, 1),
            'laboratory_performance': round(self.laboratory_performance, 1),
            'subject_wise_marks': round(self.subject_wise_marks, 1),
            'overall_performance': round(self.overall_performance, 1),
            'risk_level': self.risk_level,
            'risk_probability': round(self.risk_probability, 1),
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None
        }
