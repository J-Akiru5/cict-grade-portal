from app.extensions import db, login_manager
from flask_login import UserMixin
import uuid
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    """
    Synced 1:1 with Supabase Auth users.
    The `id` is the Supabase Auth UUID — must match exactly.
    """
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(
        db.Enum('student', 'faculty', 'admin', name='user_role_enum'),
        nullable=False,
        default='student'
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    student_profile = db.relationship('Student', back_populates='user', uselist=False, lazy='select')
    faculty_profile = db.relationship('Faculty', back_populates='user', uselist=False, lazy='select')
    grade_audits_as_actor = db.relationship('GradeAudit', back_populates='actor', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, user_id)
