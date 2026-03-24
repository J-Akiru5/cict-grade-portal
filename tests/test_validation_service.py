"""
Unit tests for validation service.
"""
import pytest

from app.services import validation_service
from app.models.user import User
from app.models.student import Student
from app.models.subject import Subject
from app.models.section import Section
from app.models.faculty import Faculty


class TestValidationService:

    def test_validate_email_format(self, db_session):
        """Test email format validation."""
        # Valid email
        result = validation_service.validate_email('test@example.com')
        assert result['valid'] is True
        assert result['available'] is True

        # Invalid format
        result = validation_service.validate_email('invalid-email')
        assert result['valid'] is False
        assert result['available'] is False

        # Empty email
        result = validation_service.validate_email('')
        assert result['valid'] is False
        assert result['available'] is False

    def test_validate_email_uniqueness(self, db_session, student_user):
        """Test email uniqueness validation."""
        result = validation_service.validate_email(student_user.email)
        assert result['valid'] is True
        assert result['available'] is False  # Email already exists

    def test_validate_student_id_format(self, db_session):
        """Test student ID format validation."""
        # Valid format
        result = validation_service.validate_student_id('202101234')
        assert result['valid'] is True
        assert result['available'] is True

        # Too short
        result = validation_service.validate_student_id('12345')
        assert result['valid'] is False

        # Too long
        result = validation_service.validate_student_id('1234567890123')
        assert result['valid'] is False

        # Invalid characters
        result = validation_service.validate_student_id('2021-ABC!')
        assert result['valid'] is False

    def test_validate_student_id_uniqueness(self, db_session, student_profile):
        """Test student ID uniqueness validation."""
        result = validation_service.validate_student_id(student_profile.student_id)
        assert result['valid'] is True
        assert result['available'] is False  # Already exists

        # Test with exclude_id
        result = validation_service.validate_student_id(
            student_profile.student_id,
            exclude_id=student_profile.id
        )
        assert result['valid'] is True
        assert result['available'] is True  # Excluded from check

    def test_validate_employee_id_format(self, db_session):
        """Test employee ID format validation."""
        # Valid format
        result = validation_service.validate_employee_id('EMP001')
        assert result['valid'] is True
        assert result['available'] is True

        # Too short
        result = validation_service.validate_employee_id('E1')
        assert result['valid'] is False

        # Too long
        result = validation_service.validate_employee_id('EMPLOYEE001')
        assert result['valid'] is False

        # Invalid characters
        result = validation_service.validate_employee_id('EMP-001!')
        assert result['valid'] is False

    def test_validate_employee_id_uniqueness(self, db_session, faculty_profile):
        """Test employee ID uniqueness validation."""
        result = validation_service.validate_employee_id(faculty_profile.employee_id)
        assert result['valid'] is True
        assert result['available'] is False  # Already exists

    def test_validate_subject_code_format(self, db_session):
        """Test subject code format validation."""
        # Valid format
        result = validation_service.validate_subject_code('CS101')
        assert result['valid'] is True
        assert result['available'] is True

        # With spaces (should be normalized)
        result = validation_service.validate_subject_code('CS 101')
        assert result['valid'] is True

        # Too short
        result = validation_service.validate_subject_code('CS')
        assert result['valid'] is False

        # Too long
        result = validation_service.validate_subject_code('COMPUTER SCIENCE 101')
        assert result['valid'] is False

        # Invalid characters
        result = validation_service.validate_subject_code('CS101!')
        assert result['valid'] is False

    def test_validate_subject_code_uniqueness(self, db_session, subject):
        """Test subject code uniqueness validation."""
        result = validation_service.validate_subject_code(subject.subject_code)
        assert result['valid'] is True
        assert result['available'] is False  # Already exists

    def test_validate_section_name_format(self, db_session):
        """Test section name format validation."""
        # Valid format
        result = validation_service.validate_section_name('BSIT-3A')
        assert result['valid'] is True
        assert result['available'] is True

        # Too short
        result = validation_service.validate_section_name('A')
        assert result['valid'] is False

        # Too long
        result = validation_service.validate_section_name('BSIT-3A-SPECIAL')
        assert result['valid'] is False

        # Invalid characters
        result = validation_service.validate_section_name('BSIT_3A!')
        assert result['valid'] is False

    def test_validate_phone_number(self, db_session):
        """Test phone number validation."""
        # Valid formats
        result = validation_service.validate_phone_number('09123456789')
        assert result['valid'] is True

        result = validation_service.validate_phone_number('+639123456789')
        assert result['valid'] is True

        result = validation_service.validate_phone_number('123-456-7890')
        assert result['valid'] is True

        # Too short
        result = validation_service.validate_phone_number('123456789')
        assert result['valid'] is False

        # Too long
        result = validation_service.validate_phone_number('1234567890123456')
        assert result['valid'] is False

        # Empty (should be valid as optional)
        result = validation_service.validate_phone_number('')
        assert result['valid'] is True

    def test_validate_age(self, db_session):
        """Test age validation."""
        # Valid ages
        result = validation_service.validate_age('20')
        assert result['valid'] is True

        result = validation_service.validate_age('45')
        assert result['valid'] is True

        # Too young
        result = validation_service.validate_age('15')
        assert result['valid'] is False

        # Too old
        result = validation_service.validate_age('70')
        assert result['valid'] is False

        # Invalid format
        result = validation_service.validate_age('twenty')
        assert result['valid'] is False

        # Empty (should be valid as optional)
        result = validation_service.validate_age('')
        assert result['valid'] is True

    def test_validate_year_level(self, db_session):
        """Test year level validation."""
        # Valid levels
        for level in ['1', '2', '3', '4']:
            result = validation_service.validate_year_level(level)
            assert result['valid'] is True

        # Invalid levels
        result = validation_service.validate_year_level('5')
        assert result['valid'] is False

        result = validation_service.validate_year_level('0')
        assert result['valid'] is False

        # Invalid format
        result = validation_service.validate_year_level('first')
        assert result['valid'] is False

        # Empty
        result = validation_service.validate_year_level('')
        assert result['valid'] is False