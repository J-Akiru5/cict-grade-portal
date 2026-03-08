from app.extensions import db


class Schedule(db.Model):
    """
    A class schedule entry — either student-owned (student_id set) or
    faculty-owned (faculty_id set, student_id null).
    The weekly matrix is built by grouping records by day_of_week.
    """
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    # One of student_id or faculty_id must be set
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True, index=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    day_of_week = db.Column(
        db.Enum('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', name='day_enum'),
        nullable=False
    )
    time_start = db.Column(db.Time, nullable=False)
    time_end = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    semester = db.Column(
        db.Enum('1st', '2nd', 'Summer', name='schedule_semester_enum'),
        nullable=True
    )

    # Relationships
    student = db.relationship('Student', back_populates='schedules')
    faculty = db.relationship('Faculty', back_populates='schedules')
    subject = db.relationship('Subject', back_populates='schedules')

    def __repr__(self):
        owner = f'student={self.student_id}' if self.student_id else f'faculty={self.faculty_id}'
        return (
            f'<Schedule {owner} '
            f'{self.day_of_week} {self.time_start}-{self.time_end}>'
        )
