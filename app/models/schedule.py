from app.extensions import db


class Schedule(db.Model):
    """
    A class schedule entry.
    - section_id set: admin-created section-level schedule (visible to all students in that section + the assigned faculty)
    - faculty_id only (no section_id): faculty personal schedule entry
    - student_id set: individual student schedule (legacy)
    """
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    # Owner: section_id (admin), faculty_id (personal), or student_id (individual)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True, index=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True, index=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True, index=True)
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
    section_obj = db.relationship('Section', back_populates='schedules', foreign_keys=[section_id])
    subject = db.relationship('Subject', back_populates='schedules')

    def __repr__(self):
        if self.section_id:
            owner = f'section={self.section_id}'
        elif self.faculty_id:
            owner = f'faculty={self.faculty_id}'
        else:
            owner = f'student={self.student_id}'
        return f'<Schedule {owner} {self.day_of_week} {self.time_start}-{self.time_end}>'
