from app.extensions import db
from datetime import datetime, timezone


class Section(db.Model):
    """
    An academic section — e.g. BSIT-2A.
    Students and schedules are linked to sections via FK.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    program = db.Column(db.String(20), nullable=False, default='BSIT')     # e.g. 'BSIT'
    year_level = db.Column(db.Integer, nullable=False)                      # 1, 2, 3, 4
    section_letter = db.Column(db.String(5), nullable=False)                # 'A', 'B', etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('program', 'year_level', 'section_letter', name='uq_section_combo'),
    )

    # Relationships
    students = db.relationship('Student', back_populates='section_obj', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='section_obj', lazy='dynamic')

    @property
    def display_name(self) -> str:
        return f'{self.program}-{self.year_level}{self.section_letter}'

    def __repr__(self):
        return f'<Section {self.display_name}>'
