"""
Unit tests for student service.
"""
import pytest
from datetime import datetime, timezone

from app.services import student_service
from app.models.student import Student
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.subject import Subject


class TestStudentService:

    def test_get_student_profile_exists(self, db_session, student_profile, student_user):
        """Test getting existing student profile."""
        result = student_service.get_student_profile(student_user.id)
        assert result is not None
        assert result.id == student_profile.id
        assert result.full_name == student_profile.full_name

    def test_get_student_profile_not_exists(self, db_session):
        """Test getting non-existent student profile."""
        result = student_service.get_student_profile('non-existent-id')
        assert result is None

    def test_get_grades_with_released_only(self, db_session, grade, student_profile):
        """Test getting grades with released filter."""
        # Grade is not released by default
        result = student_service.get_grades(student_profile.id, include_unreleased=False)
        assert len(result) == 0

        # Release the grade
        grade.is_released = True
        db_session.commit()

        result = student_service.get_grades(student_profile.id, include_unreleased=False)
        assert len(result) == 1
        assert result[0]['grade_value'] == 1.75

    def test_get_grades_include_unreleased(self, db_session, grade, student_profile):
        """Test getting grades including unreleased."""
        result = student_service.get_grades(student_profile.id, include_unreleased=True)
        assert len(result) == 1
        assert result[0]['grade_value'] == 1.75

    def test_get_grades_with_filters(self, db_session, student_profile, subject, faculty_user):
        """Test getting grades with semester and year filters."""
        # Create enrollment and grade for different semester
        enrollment2 = Enrollment(
            student_id=student_profile.id,
            subject_id=subject.id,
            semester='2nd',
            academic_year='2025-2026',
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(enrollment2)
        db_session.commit()

        grade2 = Grade(
            enrollment_id=enrollment2.id,
            grade_value=2.0,
            date_encoded=datetime.now(timezone.utc),
            encoded_by_id=faculty_user.id,
            is_released=True
        )
        db_session.add(grade2)
        db_session.commit()

        # Test semester filter
        result = student_service.get_grades(
            student_profile.id,
            semester='2nd',
            include_unreleased=True
        )
        assert len(result) == 1
        assert result[0]['grade_value'] == 2.0

    def test_get_grade_history(self, db_session, student_profile, subject, faculty_user):
        """Test getting grade history grouped by semester."""
        # Create multiple grades across different semesters
        enrollments = []
        for sem in ['1st', '2nd']:
            enrollment = Enrollment(
                student_id=student_profile.id,
                subject_id=subject.id,
                semester=sem,
                academic_year='2025-2026',
                created_at=datetime.now(timezone.utc)
            )
            db_session.add(enrollment)
            enrollments.append(enrollment)

        db_session.commit()

        grades = []
        for i, enrollment in enumerate(enrollments):
            grade = Grade(
                enrollment_id=enrollment.id,
                grade_value=1.5 + (i * 0.25),
                date_encoded=datetime.now(timezone.utc),
                encoded_by_id=faculty_user.id,
                is_released=True
            )
            db_session.add(grade)
            grades.append(grade)

        db_session.commit()

        history = student_service.get_grade_history(student_profile.id)

        assert len(history) == 2
        assert '2025-2026 - 1st Semester' in history
        assert '2025-2026 - 2nd Semester' in history

        # Check GWA calculation
        sem1 = history['2025-2026 - 1st Semester']
        assert sem1['gwa'] == 1.5  # First grade
        assert len(sem1['grades']) == 1

    def test_get_grade_history_empty(self, db_session, student_profile):
        """Test getting grade history for student with no grades."""
        history = student_service.get_grade_history(student_profile.id)
        assert history == {}

    def test_get_dashboard_summary(self, db_session, grade, student_profile):
        """Test getting dashboard summary."""
        # Release the grade
        grade.is_released = True
        db_session.commit()

        summary = student_service.get_dashboard_summary(student_profile.id)

        assert 'current_gwa' in summary
        assert 'total_subjects' in summary
        assert 'completed_subjects' in summary
        assert 'pending_subjects' in summary
        assert summary['current_gwa'] == 1.75
        assert summary['total_subjects'] == 1
        assert summary['completed_subjects'] == 1
        assert summary['pending_subjects'] == 0

    def test_search_students(self, db_session, student_profile):
        """Test student search functionality."""
        # Search by name
        results = student_service.search_students('Jane')
        assert len(results) == 1
        assert results[0].id == student_profile.id

        # Search by student ID
        results = student_service.search_students('2021-001')
        assert len(results) == 1
        assert results[0].id == student_profile.id

        # Search with no results
        results = student_service.search_students('NonExistent')
        assert len(results) == 0

    def test_get_enrollment_status(self, db_session, enrollment, student_profile):
        """Test getting enrollment status."""
        result = student_service.get_enrollment_status(
            student_profile.id,
            '1st',
            '2025-2026'
        )

        assert 'enrolled_subjects' in result
        assert 'total_units' in result
        assert result['total_units'] == 3  # Subject has 3 units
        assert len(result['enrolled_subjects']) == 1