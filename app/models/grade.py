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

    # Grade Release Control
    is_released = db.Column(db.Boolean, default=False, nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    released_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Relationships
    enrollment = db.relationship('Enrollment', back_populates='grade')
    encoded_by = db.relationship('User', foreign_keys=[encoded_by_id])
    released_by = db.relationship('User', foreign_keys=[released_by_id])

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


# ─── Audit Trail Event Listeners ─────────────────────────────────────────────
@event.listens_for(Grade, 'after_insert')
def grade_after_insert(mapper, connection, target):
    """Writes a GradeAudit record the first time a grade is encoded."""
    from app.models.audit import GradeAudit

    if target.grade_value is None and target.remarks is None:
        return

    try:
        from flask_login import current_user
        actor_id = current_user.id if current_user and current_user.is_authenticated else None
    except Exception:
        actor_id = None

    try:
        student_id = target.enrollment.student_id if target.enrollment else None
    except Exception:
        student_id = None

    try:
        audit = GradeAudit(
            grade_id=target.id,
            actor_id=actor_id,
            target_student_id=student_id,
            old_grade=None,
            new_grade=target.grade_value,
            old_remarks=None,
            new_remarks=target.remarks,
        )
        db.session.add(audit)
    except Exception:
        pass  # Skip audit in non-request contexts (e.g. CLI seed)


@event.listens_for(Grade, 'after_update')
def grade_after_update(mapper, connection, target):
    """Writes a GradeAudit record after every grade update."""
    from app.models.audit import GradeAudit

    insp = db.inspect(target).attrs
    grade_history = insp.grade_value.history
    remarks_history = insp.remarks.history

    if not grade_history.has_changes() and not remarks_history.has_changes():
        return

    old_val = grade_history.deleted[0] if grade_history.deleted else None
    new_val = grade_history.added[0] if grade_history.added else None
    old_rem = remarks_history.deleted[0] if remarks_history.deleted else None
    new_rem = remarks_history.added[0] if remarks_history.added else None

    try:
        from flask_login import current_user
        actor_id = current_user.id if current_user and current_user.is_authenticated else None
    except Exception:
        actor_id = None

    try:
        student_id = target.enrollment.student_id if target.enrollment else None
    except Exception:
        student_id = None

    try:
        audit = GradeAudit(
            grade_id=target.id,
            actor_id=actor_id,
            target_student_id=student_id,
            old_grade=old_val,
            new_grade=new_val,
            old_remarks=old_rem,
            new_remarks=new_rem,
        )
        db.session.add(audit)
    except Exception:
        pass  # Skip audit in non-request contexts (e.g. CLI seed)

