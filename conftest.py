"""
Test configuration and fixtures for the Grade Portal.
"""
import os
import tempfile
import pytest
from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.section import Section
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.academic_settings import AcademicSettings


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Test configuration
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-anon-key',
    }

    # Create app with test config
    app = create_app('testing')
    app.config.update(test_config)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Create default academic settings
        settings = AcademicSettings(
            current_semester='1st',
            current_year='2025-2026',
            updated_at=datetime.now(timezone.utc)
        )
        db.session.add(settings)
        db.session.commit()

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        # Begin transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Configure session to use transaction
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        db.session = session

        yield session

        # Rollback transaction
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture(scope='function')
def clean_db(app):
    """Clean database for each test."""
    with app.app_context():
        # Clear all tables except academic settings
        db.session.query(Grade).delete()
        db.session.query(Enrollment).delete()
        db.session.query(Subject).delete()
        db.session.query(Faculty).delete()
        db.session.query(Student).delete()
        db.session.query(User).delete()
        db.session.commit()
        yield
        # Cleanup happens automatically with transaction rollback


# User fixtures
@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""
    user = User(
        id='admin-123',
        email='admin@test.com',
        role='admin',
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def faculty_user(db_session):
    """Create faculty user for testing."""
    user = User(
        id='faculty-123',
        email='faculty@test.com',
        role='faculty',
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def student_user(db_session):
    """Create student user for testing."""
    user = User(
        id='student-123',
        email='student@test.com',
        role='student',
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def faculty_profile(db_session, faculty_user):
    """Create faculty profile for testing."""
    faculty = Faculty(
        user_id=faculty_user.id,
        employee_id='EMP001',
        full_name='John Faculty',
        department='Computer Science',
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(faculty)
    db_session.commit()
    return faculty


@pytest.fixture
def student_profile(db_session, student_user):
    """Create student profile for testing."""
    section = Section(
        program='BSIT',
        year_level=3,
        section_letter='A',
        display_name='BSIT-3A',
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(section)
    db_session.commit()

    student = Student(
        user_id=student_user.id,
        student_id='2021-001',
        full_name='Jane Student',
        year_level=3,
        section_id=section.id,
        gmail='student@test.com',
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def subject(db_session, faculty_profile):
    """Create subject for testing."""
    subject = Subject(
        subject_code='CS101',
        code='CS101',
        title='Introduction to Computer Science',
        units=3,
        created_at=datetime.now(timezone.utc)
    )
    # Associate with faculty
    subject.assigned_faculty = [faculty_profile]
    db_session.add(subject)
    db_session.commit()
    return subject


@pytest.fixture
def enrollment(db_session, student_profile, subject):
    """Create enrollment for testing."""
    enrollment = Enrollment(
        student_id=student_profile.id,
        subject_id=subject.id,
        semester='1st',
        academic_year='2025-2026',
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(enrollment)
    db_session.commit()
    return enrollment


@pytest.fixture
def grade(db_session, enrollment, faculty_user):
    """Create grade for testing."""
    grade = Grade(
        enrollment_id=enrollment.id,
        grade_value=1.75,
        remarks=None,
        date_encoded=datetime.now(timezone.utc),
        encoded_by_id=faculty_user.id,
        is_released=False
    )
    db_session.add(grade)
    db_session.commit()
    return grade


# Authentication helpers
@pytest.fixture
def auth_headers():
    """Create authentication headers for API testing."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


def login_user(client, email, role='student'):
    """Helper function to login a user for testing."""
    with client.session_transaction() as sess:
        sess['user_id'] = f'{role}-123'
        sess['_fresh'] = True


def logout_user(client):
    """Helper function to logout user for testing."""
    with client.session_transaction() as sess:
        sess.clear()


# Mock data factories
class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create_user(db_session, role='student', **kwargs):
        """Create a user with given role."""
        defaults = {
            'id': f'{role}-{datetime.now().timestamp()}',
            'email': f'{role}@test.com',
            'role': role,
            'is_active': True,
            'created_at': datetime.now(timezone.utc)
        }
        defaults.update(kwargs)

        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        return user


class StudentFactory:
    """Factory for creating test students."""

    @staticmethod
    def create_student(db_session, **kwargs):
        """Create a student with profile."""
        # Create user first
        user = UserFactory.create_user(db_session, role='student')

        # Create section if not provided
        if 'section_id' not in kwargs:
            section = Section(
                program='BSIT',
                year_level=3,
                section_letter='A',
                display_name='BSIT-3A',
                created_at=datetime.now(timezone.utc)
            )
            db_session.add(section)
            db_session.commit()
            kwargs['section_id'] = section.id

        defaults = {
            'user_id': user.id,
            'student_id': f'2021-{int(datetime.now().timestamp()) % 1000:03d}',
            'full_name': 'Test Student',
            'year_level': 3,
            'gmail': user.email,
            'created_at': datetime.now(timezone.utc)
        }
        defaults.update(kwargs)

        student = Student(**defaults)
        db_session.add(student)
        db_session.commit()
        return student, user


class SubjectFactory:
    """Factory for creating test subjects."""

    @staticmethod
    def create_subject(db_session, **kwargs):
        """Create a subject."""
        defaults = {
            'subject_code': f'CS{int(datetime.now().timestamp()) % 1000}',
            'code': f'CS{int(datetime.now().timestamp()) % 1000}',
            'title': 'Test Subject',
            'units': 3,
            'created_at': datetime.now(timezone.utc)
        }
        defaults.update(kwargs)

        subject = Subject(**defaults)
        db_session.add(subject)
        db_session.commit()
        return subject