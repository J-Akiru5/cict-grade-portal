from app.extensions import db
from datetime import datetime, timezone


class GradeAudit(db.Model):
    """
    Immutable audit trail for every grade change.
    Populated automatically via SQLAlchemy after_update event on Grade.
    Never delete records from this table.
    """
    __tablename__ = 'grade_audits'

    id = db.Column(db.Integer, primary_key=True)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False, index=True)
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    target_student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    old_grade = db.Column(db.Float, nullable=True)
    new_grade = db.Column(db.Float, nullable=True)
    old_remarks = db.Column(db.String(10), nullable=True)
    new_remarks = db.Column(db.String(10), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)   # supports IPv6
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    actor = db.relationship('User', back_populates='grade_audits_as_actor',
                            foreign_keys=[actor_id])
    target_student = db.relationship('Student', foreign_keys=[target_student_id])
    grade = db.relationship('Grade', foreign_keys=[grade_id], lazy='select', viewonly=True)

    def __repr__(self):
        return (
            f'<GradeAudit grade={self.grade_id} '
            f'{self.old_grade}→{self.new_grade} '
            f'by={self.actor_id} at={self.timestamp}>'
        )
