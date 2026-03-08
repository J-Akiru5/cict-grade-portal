from app.extensions import db
from datetime import datetime, timezone

# Association table: Faculty (many) <-> Subject (many)
faculty_subjects = db.Table(
    'faculty_subjects',
    db.Column('faculty_id', db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True),
)


class Faculty(db.Model):
    """
    Faculty profile — linked 1:1 to a User record with role='faculty' or 'admin'.
    Stores academic identity and teaching assignment data.
    """
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True, nullable=False
    )
    full_name = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    department = db.Column(db.String(100), nullable=True, default='CICT')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship('User', back_populates='faculty_profile')
    subjects = db.relationship(
        'Subject', secondary=faculty_subjects,
        back_populates='faculty', lazy='select'
    )
    schedules = db.relationship('Schedule', back_populates='faculty', lazy='dynamic')

    def __repr__(self):
        return f'<Faculty {self.employee_id} — {self.full_name}>'
