"""
Validation Service for Grade Portal.

Provides real-time validation utilities for forms.
"""
import re
from app.models.user import User
from app.models.student import Student
from app.models.subject import Subject
from app.models.section import Section
from app.extensions import db


def validate_email(email: str) -> dict:
    """
    Validate email format and uniqueness.
    Returns: {'valid': bool, 'message': str, 'available': bool}
    """
    if not email:
        return {'valid': False, 'message': 'Email is required', 'available': False}

    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {'valid': False, 'message': 'Please enter a valid email address', 'available': False}

    # Check if email already exists
    existing_user = User.query.filter_by(email=email.lower()).first()
    if existing_user:
        return {'valid': True, 'message': 'Email is already registered', 'available': False}

    return {'valid': True, 'message': 'Email is available', 'available': True}


def validate_student_id(student_id: str, exclude_id: int = None) -> dict:
    """
    Validate student ID format and uniqueness.
    Returns: {'valid': bool, 'message': str, 'available': bool}
    """
    if not student_id:
        return {'valid': False, 'message': 'Student ID is required', 'available': False}

    # Remove spaces and convert to uppercase
    student_id = re.sub(r'\s+', '', student_id.upper())

    # Basic format validation (alphanumeric, 6-12 characters)
    if not re.match(r'^[A-Z0-9]{6,12}$', student_id):
        return {'valid': False, 'message': 'Student ID must be 6-12 alphanumeric characters', 'available': False}

    # Check uniqueness
    query = Student.query.filter_by(student_id=student_id)
    if exclude_id:
        query = query.filter(Student.id != exclude_id)

    existing_student = query.first()
    if existing_student:
        return {'valid': True, 'message': 'Student ID is already taken', 'available': False}

    return {'valid': True, 'message': 'Student ID is available', 'available': True}


def validate_employee_id(employee_id: str, exclude_user_id: str = None) -> dict:
    """
    Validate employee ID format and uniqueness.
    Returns: {'valid': bool, 'message': str, 'available': bool}
    """
    if not employee_id:
        return {'valid': False, 'message': 'Employee ID is required', 'available': False}

    # Remove spaces and convert to uppercase
    employee_id = re.sub(r'\s+', '', employee_id.upper())

    # Basic format validation (alphanumeric, 4-10 characters)
    if not re.match(r'^[A-Z0-9]{4,10}$', employee_id):
        return {'valid': False, 'message': 'Employee ID must be 4-10 alphanumeric characters', 'available': False}

    # Check uniqueness in faculty profiles
    from app.models.faculty import Faculty
    query = Faculty.query.filter_by(employee_id=employee_id)
    if exclude_user_id:
        query = query.filter(Faculty.user_id != exclude_user_id)

    existing_faculty = query.first()
    if existing_faculty:
        return {'valid': True, 'message': 'Employee ID is already taken', 'available': False}

    return {'valid': True, 'message': 'Employee ID is available', 'available': True}


def validate_subject_code(subject_code: str, exclude_id: int = None) -> dict:
    """
    Validate subject code format and uniqueness.
    Returns: {'valid': bool, 'message': str, 'available': bool}
    """
    if not subject_code:
        return {'valid': False, 'message': 'Subject code is required', 'available': False}

    # Clean and normalize
    subject_code = re.sub(r'\s+', ' ', subject_code.upper()).strip()

    # Basic format validation (letters, numbers, spaces, 3-15 chars)
    if not re.match(r'^[A-Z0-9\s]{3,15}$', subject_code):
        return {'valid': False, 'message': 'Subject code must be 3-15 characters (letters, numbers, spaces)', 'available': False}

    # Check uniqueness
    query = Subject.query.filter(
        (Subject.subject_code == subject_code) | (Subject.code == subject_code)
    )
    if exclude_id:
        query = query.filter(Subject.id != exclude_id)

    existing_subject = query.first()
    if existing_subject:
        return {'valid': True, 'message': 'Subject code is already taken', 'available': False}

    return {'valid': True, 'message': 'Subject code is available', 'available': True}


def validate_section_name(section_name: str, exclude_id: int = None) -> dict:
    """
    Validate section name format and uniqueness.
    Returns: {'valid': bool, 'message': str, 'available': bool}
    """
    if not section_name:
        return {'valid': False, 'message': 'Section name is required', 'available': False}

    # Clean and normalize
    section_name = re.sub(r'\s+', ' ', section_name.upper()).strip()

    # Basic format validation (letters, numbers, hyphens, 2-10 chars)
    if not re.match(r'^[A-Z0-9\-]{2,10}$', section_name):
        return {'valid': False, 'message': 'Section name must be 2-10 characters (letters, numbers, hyphens)', 'available': False}

    # Check uniqueness
    query = Section.query.filter_by(display_name=section_name)
    if exclude_id:
        query = query.filter(Section.id != exclude_id)

    existing_section = query.first()
    if existing_section:
        return {'valid': True, 'message': 'Section name is already taken', 'available': False}

    return {'valid': True, 'message': 'Section name is available', 'available': True}


def validate_phone_number(phone: str) -> dict:
    """
    Validate phone number format.
    Returns: {'valid': bool, 'message': str}
    """
    if not phone:
        return {'valid': True, 'message': 'Phone number is optional'}  # Optional field

    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)

    # Must be 10-15 digits
    if len(clean_phone) < 10 or len(clean_phone) > 15:
        return {'valid': False, 'message': 'Phone number must be 10-15 digits'}

    return {'valid': True, 'message': 'Valid phone number'}


def validate_age(age_str: str) -> dict:
    """
    Validate age value.
    Returns: {'valid': bool, 'message': str}
    """
    if not age_str:
        return {'valid': True, 'message': 'Age is optional'}  # Optional field

    try:
        age = int(age_str)
        if age < 16 or age > 65:
            return {'valid': False, 'message': 'Age must be between 16 and 65'}
        return {'valid': True, 'message': 'Valid age'}
    except ValueError:
        return {'valid': False, 'message': 'Age must be a number'}


def validate_year_level(year_str: str) -> dict:
    """
    Validate year level value.
    Returns: {'valid': bool, 'message': str}
    """
    if not year_str:
        return {'valid': False, 'message': 'Year level is required'}

    try:
        year = int(year_str)
        if year not in [1, 2, 3, 4]:
            return {'valid': False, 'message': 'Year level must be 1, 2, 3, or 4'}
        return {'valid': True, 'message': 'Valid year level'}
    except ValueError:
        return {'valid': False, 'message': 'Year level must be a number'}