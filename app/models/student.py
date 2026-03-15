from app.extensions import db
from datetime import datetime, timezone


class Student(db.Model):
    """
    Student profile — linked 1:1 to a User record.
    Stores academic identity and personal contact info.
    """
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    section = db.Column(db.String(50), nullable=True)       # e.g. BSIT-2A
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.Text, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    gmail = db.Column(db.String(255), nullable=True)
    curriculum_year = db.Column(db.String(20), nullable=True)  # e.g. 2024-2025
    year_level = db.Column(db.Integer, nullable=True)          # 1, 2, 3, 4
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = db.relationship('User', back_populates='student_profile')
    enrollments = db.relationship('Enrollment', back_populates='student', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.student_id} — {self.full_name}>'
