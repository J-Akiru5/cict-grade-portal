from app.extensions import db
from datetime import datetime, timezone


class AcademicSettings(db.Model):
    """
    System-wide academic period settings.
    Only one row is expected; use get_current() to retrieve/create it.
    """
    __tablename__ = 'academic_settings'

    id = db.Column(db.Integer, primary_key=True)
    current_semester = db.Column(
        db.Enum('1st', '2nd', 'Summer', name='settings_semester_enum'),
        nullable=False,
        default='1st',
    )
    current_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    updated_by_id = db.Column(
        db.String(36), db.ForeignKey('users.id'), nullable=True
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    @classmethod
    def get_current(cls):
        """Return the single settings row, creating defaults if none exist."""
        settings = cls.query.first()
        if settings is None:
            settings = cls(current_semester='1st', current_year='2025-2026')
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self):
        return f'<AcademicSettings {self.current_year} {self.current_semester}>'
