"""
API routes for real-time validation.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.utils.security import role_required
from app.services import validation_service
from app.extensions import limiter

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/validate/email', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
@limiter.limit("60 per minute")  # Rate limit validation calls
def validate_email():
    """Validate email address in real-time."""
    email = request.json.get('email', '').strip().lower()
    result = validation_service.validate_email(email)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'available': result['available'],
        'field': 'email'
    })


@api_bp.route('/validate/student-id', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_student_id():
    """Validate student ID in real-time."""
    student_id = request.json.get('student_id', '').strip()
    exclude_id = request.json.get('exclude_id')  # For editing existing records

    result = validation_service.validate_student_id(student_id, exclude_id)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'available': result['available'],
        'field': 'student_id'
    })


@api_bp.route('/validate/employee-id', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_employee_id():
    """Validate employee ID in real-time."""
    employee_id = request.json.get('employee_id', '').strip()
    exclude_user_id = request.json.get('exclude_user_id')  # For editing existing records

    result = validation_service.validate_employee_id(employee_id, exclude_user_id)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'available': result['available'],
        'field': 'employee_id'
    })


@api_bp.route('/validate/subject-code', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_subject_code():
    """Validate subject code in real-time."""
    subject_code = request.json.get('subject_code', '').strip()
    exclude_id = request.json.get('exclude_id')

    result = validation_service.validate_subject_code(subject_code, exclude_id)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'available': result['available'],
        'field': 'subject_code'
    })


@api_bp.route('/validate/section-name', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_section_name():
    """Validate section name in real-time."""
    section_name = request.json.get('section_name', '').strip()
    exclude_id = request.json.get('exclude_id')

    result = validation_service.validate_section_name(section_name, exclude_id)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'available': result['available'],
        'field': 'section_name'
    })


@api_bp.route('/validate/phone', methods=['POST'])
@login_required
@role_required('admin', 'faculty', 'student')
def validate_phone():
    """Validate phone number format."""
    phone = request.json.get('phone', '').strip()

    result = validation_service.validate_phone_number(phone)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'field': 'phone'
    })


@api_bp.route('/validate/age', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_age():
    """Validate age value."""
    age = request.json.get('age', '').strip()

    result = validation_service.validate_age(age)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'field': 'age'
    })


@api_bp.route('/validate/year-level', methods=['POST'])
@login_required
@role_required('admin', 'faculty')
def validate_year_level():
    """Validate year level value."""
    year_level = request.json.get('year_level', '').strip()

    result = validation_service.validate_year_level(year_level)

    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'field': 'year_level'
    })


@api_bp.route('/validate/batch', methods=['POST'])
@login_required
@role_required('admin', 'faculty', 'student')
@limiter.limit("30 per minute")  # Lower limit for batch operations
def validate_batch():
    """Validate multiple fields at once."""
    fields = request.json.get('fields', {})
    results = {}

    for field, value in fields.items():
        if field == 'email':
            results[field] = validation_service.validate_email(value)
        elif field == 'student_id':
            exclude_id = fields.get('exclude_student_id')
            results[field] = validation_service.validate_student_id(value, exclude_id)
        elif field == 'employee_id':
            exclude_user_id = fields.get('exclude_user_id')
            results[field] = validation_service.validate_employee_id(value, exclude_user_id)
        elif field == 'subject_code':
            exclude_id = fields.get('exclude_subject_id')
            results[field] = validation_service.validate_subject_code(value, exclude_id)
        elif field == 'section_name':
            exclude_id = fields.get('exclude_section_id')
            results[field] = validation_service.validate_section_name(value, exclude_id)
        elif field == 'phone':
            results[field] = validation_service.validate_phone_number(value)
        elif field == 'age':
            results[field] = validation_service.validate_age(value)
        elif field == 'year_level':
            results[field] = validation_service.validate_year_level(value)
        else:
            results[field] = {'valid': True, 'message': 'No validation available'}

        results[field]['field'] = field

    return jsonify({'results': results})