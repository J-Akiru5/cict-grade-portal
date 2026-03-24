"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.section import Section
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.extensions import db


class TestUserModel:

    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            id='test-123',
            email='test@example.com',
            role='student',
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user)
        db_session.commit()

        assert user.id == 'test-123'
        assert user.email == 'test@example.com'
        assert user.role == 'student'
        assert user.is_active is True

    def test_user_email_unique(self, db_session):
        """Test that user emails are unique."""
        user1 = User(
            id='test-1',
            email='test@example.com',
            role='student',
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            id='test-2',
            email='test@example.com',  # Same email
            role='faculty',
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            id='test-123',
            email='test@example.com',
            role='student',
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        assert 'test@example.com' in repr(user)


class TestStudentModel:

    def test_create_student(self, db_session, student_user):
        """Test creating a student."""
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
            full_name='Jane Doe',
            year_level=3,
            section_id=section.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(student)
        db_session.commit()

        assert student.student_id == '2021-001'
        assert student.full_name == 'Jane Doe'
        assert student.year_level == 3
        assert student.section.display_name == 'BSIT-3A'

    def test_student_id_unique(self, db_session, student_user):
        """Test that student IDs are unique."""
        section = Section(
            program='BSIT',
            year_level=3,
            section_letter='A',
            display_name='BSIT-3A',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(section)
        db_session.commit()

        student1 = Student(
            user_id=student_user.id,
            student_id='2021-001',
            full_name='Jane Doe',
            year_level=3,
            section_id=section.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(student1)
        db_session.commit()

        # Create another user for second student
        user2 = User(
            id='user-2',
            email='user2@example.com',
            role='student',
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user2)
        db_session.commit()

        student2 = Student(
            user_id=user2.id,
            student_id='2021-001',  # Same student ID
            full_name='John Doe',
            year_level=3,
            section_id=section.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(student2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_student_without_user(self, db_session):
        """Test creating student without user account."""
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
            user_id=None,  # No user account
            student_id='2021-002',
            full_name='No Account Student',
            year_level=3,
            section_id=section.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(student)
        db_session.commit()

        assert student.user_id is None
        assert student.user is None


class TestSubjectModel:

    def test_create_subject(self, db_session):
        """Test creating a subject."""
        subject = Subject(
            subject_code='CS101',
            code='CS101',
            title='Introduction to Computer Science',
            units=3,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(subject)
        db_session.commit()

        assert subject.subject_code == 'CS101'
        assert subject.title == 'Introduction to Computer Science'
        assert subject.units == 3

    def test_subject_faculty_relationship(self, db_session, faculty_profile):
        """Test subject-faculty many-to-many relationship."""
        subject = Subject(
            subject_code='CS101',
            code='CS101',
            title='Introduction to Computer Science',
            units=3,
            created_at=datetime.now(timezone.utc)
        )
        subject.assigned_faculty = [faculty_profile]
        db_session.add(subject)
        db_session.commit()

        assert len(subject.assigned_faculty) == 1
        assert faculty_profile in subject.assigned_faculty
        assert subject in faculty_profile.subjects


class TestEnrollmentModel:

    def test_create_enrollment(self, db_session, student_profile, subject):
        """Test creating an enrollment."""
        enrollment = Enrollment(
            student_id=student_profile.id,
            subject_id=subject.id,
            semester='1st',
            academic_year='2025-2026',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(enrollment)
        db_session.commit()

        assert enrollment.student_id == student_profile.id
        assert enrollment.subject_id == subject.id
        assert enrollment.semester == '1st'
        assert enrollment.student == student_profile
        assert enrollment.subject == subject

    def test_enrollment_unique_constraint(self, db_session, student_profile, subject):
        """Test enrollment uniqueness constraint."""
        enrollment1 = Enrollment(
            student_id=student_profile.id,
            subject_id=subject.id,
            semester='1st',
            academic_year='2025-2026',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(enrollment1)
        db_session.commit()

        # Try to create duplicate enrollment
        enrollment2 = Enrollment(
            student_id=student_profile.id,
            subject_id=subject.id,
            semester='1st',
            academic_year='2025-2026',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(enrollment2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestGradeModel:

    def test_create_grade(self, db_session, enrollment, faculty_user):
        """Test creating a grade."""
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

        assert grade.enrollment_id == enrollment.id
        assert grade.grade_value == 1.75
        assert grade.is_released is False
        assert grade.enrollment == enrollment

    def test_grade_with_remarks(self, db_session, enrollment, faculty_user):
        """Test creating grade with remarks."""
        grade = Grade(
            enrollment_id=enrollment.id,
            grade_value=None,
            remarks='INC',
            date_encoded=datetime.now(timezone.utc),
            encoded_by_id=faculty_user.id,
            is_released=False
        )
        db_session.add(grade)
        db_session.commit()

        assert grade.grade_value is None
        assert grade.remarks == 'INC'

    def test_grade_release(self, db_session, enrollment, faculty_user, admin_user):
        """Test grade release functionality."""
        grade = Grade(
            enrollment_id=enrollment.id,
            grade_value=2.0,
            date_encoded=datetime.now(timezone.utc),
            encoded_by_id=faculty_user.id,
            is_released=False
        )
        db_session.add(grade)
        db_session.commit()

        # Release grade
        grade.is_released = True
        grade.released_at = datetime.now(timezone.utc)
        grade.released_by_id = admin_user.id
        db_session.commit()

        assert grade.is_released is True
        assert grade.released_at is not None
        assert grade.released_by_id == admin_user.id


class TestSectionModel:

    def test_create_section(self, db_session):
        """Test creating a section."""
        section = Section(
            program='BSIT',
            year_level=3,
            section_letter='A',
            display_name='BSIT-3A',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(section)
        db_session.commit()

        assert section.program == 'BSIT'
        assert section.year_level == 3
        assert section.section_letter == 'A'
        assert section.display_name == 'BSIT-3A'

    def test_section_students_relationship(self, db_session, student_profile):
        """Test section-students relationship."""
        section = student_profile.section
        assert student_profile in section.students
        assert len(section.students) >= 1