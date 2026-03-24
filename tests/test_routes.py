"""
Integration tests for API routes.
"""
import json
import pytest
from flask_login import current_user

from conftest import login_user, logout_user


class TestValidationAPI:

    def test_validate_email_endpoint_unauthenticated(self, client):
        """Test validation endpoint requires authentication."""
        response = client.post('/api/v1/validate/email',
                             json={'email': 'test@example.com'})
        assert response.status_code == 401

    def test_validate_email_endpoint_admin(self, client, app, admin_user):
        """Test email validation endpoint as admin."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            # Valid available email
            response = client.post('/api/v1/validate/email',
                                 json={'email': 'new@example.com'})
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['valid'] is True
            assert data['available'] is True

            # Existing email
            response = client.post('/api/v1/validate/email',
                                 json={'email': admin_user.email})
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['valid'] is True
            assert data['available'] is False

    def test_validate_email_endpoint_student_forbidden(self, client, app, student_user):
        """Test that students cannot access validation endpoints."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            response = client.post('/api/v1/validate/email',
                                 json={'email': 'test@example.com'})
            assert response.status_code == 403  # Forbidden for students

    def test_validate_student_id_endpoint(self, client, app, admin_user, student_profile):
        """Test student ID validation endpoint."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            # Valid available student ID
            response = client.post('/api/v1/validate/student-id',
                                 json={'student_id': '2022001234'})
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['valid'] is True
            assert data['available'] is True

            # Existing student ID
            response = client.post('/api/v1/validate/student-id',
                                 json={'student_id': student_profile.student_id})
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['valid'] is True
            assert data['available'] is False

    def test_validate_batch_endpoint(self, client, app, admin_user):
        """Test batch validation endpoint."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            response = client.post('/api/v1/validate/batch',
                                 json={
                                     'fields': {
                                         'email': 'test@example.com',
                                         'student_id': '2022001234',
                                         'age': '20'
                                     }
                                 })
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'results' in data
            assert 'email' in data['results']
            assert 'student_id' in data['results']
            assert 'age' in data['results']

            # All should be valid
            assert data['results']['email']['valid'] is True
            assert data['results']['student_id']['valid'] is True
            assert data['results']['age']['valid'] is True

    def test_api_rate_limiting(self, client, app, admin_user):
        """Test API rate limiting (basic test)."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            # Make multiple requests quickly
            responses = []
            for _ in range(5):
                response = client.post('/api/v1/validate/email',
                                     json={'email': 'test@example.com'})
                responses.append(response)

            # First few should succeed
            assert responses[0].status_code == 200
            assert responses[1].status_code == 200

    def test_invalid_json_request(self, client, app, admin_user):
        """Test handling of invalid JSON requests."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            response = client.post('/api/v1/validate/email',
                                 data='invalid json',
                                 content_type='application/json')
            assert response.status_code == 400

    def test_missing_field_validation(self, client, app, admin_user):
        """Test validation with missing fields."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            # Missing email field
            response = client.post('/api/v1/validate/email',
                                 json={})
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['valid'] is False


class TestStudentRoutes:

    def test_student_dashboard_authenticated(self, client, app, student_user, student_profile):
        """Test student dashboard requires authentication."""
        with app.test_request_context():
            # Without authentication
            response = client.get('/student/dashboard')
            assert response.status_code == 302  # Redirect to login

            # With authentication
            login_user(client, student_user.email, 'student')
            response = client.get('/student/dashboard')
            assert response.status_code == 200

    def test_student_grades_view(self, client, app, student_user, student_profile, grade):
        """Test student grades view."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            response = client.get('/student/grades')
            assert response.status_code == 200
            # Should not see unreleased grades
            assert b'1.75' not in response.data

            # Release the grade
            grade.is_released = True
            from app.extensions import db
            db.session.commit()

            response = client.get('/student/grades')
            assert response.status_code == 200
            # Should now see the grade
            assert b'1.75' in response.data

    def test_student_grade_history(self, client, app, student_user, student_profile, grade):
        """Test student grade history view."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            # Release the grade
            grade.is_released = True
            from app.extensions import db
            db.session.commit()

            response = client.get('/student/grade-history')
            assert response.status_code == 200
            assert b'Grade History' in response.data

    def test_student_cannot_access_admin_routes(self, client, app, student_user):
        """Test that students cannot access admin routes."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            response = client.get('/panel/admin/students')
            assert response.status_code == 403  # Forbidden

    def test_htmx_requests(self, client, app, student_user, student_profile):
        """Test HTMX partial responses."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            headers = {'HX-Request': 'true'}
            response = client.get('/student/dashboard', headers=headers)
            assert response.status_code == 200
            # Should return partial template, not full page
            assert b'<!DOCTYPE html>' not in response.data


class TestAuthenticationRoutes:

    def test_login_page_accessible(self, client):
        """Test login page is accessible."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_login_redirect_when_authenticated(self, client, app, student_user):
        """Test login redirects when already authenticated."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            response = client.get('/auth/login')
            assert response.status_code == 302  # Redirect

    def test_logout_functionality(self, client, app, student_user):
        """Test logout functionality."""
        with app.test_request_context():
            login_user(client, student_user.email, 'student')

            # Should be able to access protected route
            response = client.get('/student/dashboard')
            assert response.status_code == 200

            # Logout
            response = client.get('/auth/logout')
            assert response.status_code == 302  # Redirect

            # Should no longer be able to access protected route
            response = client.get('/student/dashboard')
            assert response.status_code == 302  # Redirect to login

    def test_register_page_accessible(self, client):
        """Test registration page is accessible."""
        response = client.get('/auth/register')
        assert response.status_code == 200


class TestPanelRoutes:

    def test_faculty_dashboard(self, client, app, faculty_user, faculty_profile):
        """Test faculty panel dashboard."""
        with app.test_request_context():
            login_user(client, faculty_user.email, 'faculty')

            response = client.get('/panel/dashboard')
            assert response.status_code == 200

    def test_admin_students_list(self, client, app, admin_user, student_profile):
        """Test admin students list."""
        with app.test_request_context():
            login_user(client, admin_user.email, 'admin')

            response = client.get('/panel/admin/students')
            assert response.status_code == 200
            assert student_profile.full_name.encode() in response.data

    def test_faculty_cannot_access_admin_routes(self, client, app, faculty_user):
        """Test that faculty cannot access admin-only routes."""
        with app.test_request_context():
            login_user(client, faculty_user.email, 'faculty')

            response = client.get('/panel/admin/students')
            assert response.status_code == 403  # Forbidden