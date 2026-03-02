from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import event


class Grade(db.Model):
    """
    Philippine academic grade for a student's enrollment.
    Scale: 1.0 (Excellent) → 5.0 (Failed)
    Passing threshold: ≤ 3.0
    """
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(
        db.Integer, db.ForeignKey('enrollments.id'), unique=True, nullable=False, index=True
    )
    grade_value = db.Column(db.Float, nullable=True)   # None = not yet encoded
    remarks = db.Column(db.String(10), nullable=True)  # PASSED, FAILED, INC, DRP
    date_encoded = db.Column(db.DateTime, nullable=True)
    encoded_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    enrollment = db.relationship('Enrollment', back_populates='grade')
    encoded_by = db.relationship('User', foreign_keys=[encoded_by_id])

    @property
    def computed_remarks(self) -> str:
        """Derive remarks from grade value using Philippine standard."""
        if self.grade_value is None:
            return 'NOT YET ENCODED'
        if self.remarks in ('INC', 'DRP'):
            return self.remarks
        return 'PASSED' if self.grade_value <= 3.0 else 'FAILED'

    @property
    def grade_display(self) -> str:
        if self.grade_value is None:
            return '—'
        return f'{self.grade_value:.2f}'

    def __repr__(self):
        return f'<Grade enrollment={self.enrollment_id} value={self.grade_value}>'


# ─── Audit Trail Event Listener ───────────────────────────────────────────────
@event.listens_for(Grade, 'after_update')
def grade_after_update(mapper, connection, target):
    """Automatically writes a GradeAudit record after every grade change."""
    from app.models.audit import GradeAudit
    from flask_login import current_user
    import ipaddress

    history = db.inspect(target).attrs.grade_value.history
    if not history.has_changes():
        return

    old_val = history.deleted[0] if history.deleted else None
    new_val = history.added[0] if history.added else None

    audit = GradeAudit(
        grade_id=target.id,
        actor_id=current_user.id if current_user and current_user.is_authenticated else None,
        target_student_id=target.enrollment.student_id if target.enrollment else None,
        old_grade=old_val,
        new_grade=new_val,
    )
    db.session.add(audit)
