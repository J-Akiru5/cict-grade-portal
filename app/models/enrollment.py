from app.extensions import db
from datetime import datetime, timezone


class Enrollment(db.Model):
    """
    Links a Student to a Subject for a given semester and academic year.
    This is the pivot table that Grade and Schedule reference.
    """
    __tablename__ = 'enrollments'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'semester', 'academic_year',
                            name='uq_enrollment'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    semester = db.Column(
        db.Enum('1st', '2nd', 'Summer', name='semester_enum'),
        nullable=False,
        default='1st'
    )
    academic_year = db.Column(db.String(20), nullable=False)  # e.g. 2024-2025
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student = db.relationship('Student', back_populates='enrollments')
    subject = db.relationship('Subject', back_populates='enrollments')
    grade = db.relationship('Grade', back_populates='enrollment', uselist=False, lazy='select')

    def __repr__(self):
        return f'<Enrollment student={self.student_id} subject={self.subject_id} {self.semester} {self.academic_year}>'
