from app.extensions import db


class Schedule(db.Model):
    """
    A student's class schedule entry.
    Many-to-one with Student and Subject.
    The weekly matrix is built by grouping these records by day_of_week.
    """
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
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
    subject = db.relationship('Subject', back_populates='schedules')

    def __repr__(self):
        return (
            f'<Schedule student={self.student_id} '
            f'{self.day_of_week} {self.time_start}-{self.time_end}>'
        )
