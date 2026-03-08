"""
Models package — import all models here so Alembic can detect them.
"""
from .user import User
from .student import Student
from .faculty import Faculty, faculty_subjects
from .subject import Subject
from .enrollment import Enrollment
from .grade import Grade
from .schedule import Schedule
from .audit import GradeAudit
from .academic_settings import AcademicSettings

__all__ = [
    'User', 'Student', 'Faculty', 'faculty_subjects',
    'Subject', 'Enrollment', 'Grade', 'Schedule', 'GradeAudit',
    'AcademicSettings',
]
