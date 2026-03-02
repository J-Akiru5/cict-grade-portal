from app.extensions import db


class Subject(db.Model):
    """
    A course/subject offered by the college.
    Instructors are stored here as a denormalized string for simplicity; 
    a Faculty model can be linked later in Phase 2.
    """
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)   # e.g. IT 211
    subject_title = db.Column(db.String(255), nullable=False)
    units = db.Column(db.Integer, nullable=False, default=3)
    instructor_name = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(100), nullable=True, default='CICT')

    # Relationships
    enrollments = db.relationship('Enrollment', back_populates='subject', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.subject_code}: {self.subject_title}>'
