"""
Unit tests for email notification service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.services.email_notification_service import EmailNotificationService
from app.models.grade import Grade


class TestEmailNotificationService:

    @pytest.fixture
    def email_service(self):
        """Create email service for testing."""
        with patch.dict('os.environ', {
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@example.com',
            'SMTP_PASSWORD': 'testpass',
            'FROM_EMAIL': 'noreply@test.com',
            'FROM_NAME': 'Test Portal'
        }):
            return EmailNotificationService()

    def test_email_service_initialization(self, email_service):
        """Test email service initialization."""
        assert email_service.smtp_server == 'smtp.test.com'
        assert email_service.smtp_port == 587
        assert email_service.smtp_username == 'test@example.com'
        assert email_service.from_email == 'noreply@test.com'

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, email_service):
        """Test successful email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_service.send_email(
            'recipient@test.com',
            'Test Subject',
            '<h1>Test HTML</h1>',
            'Test Plain Text'
        )

        assert result is True
        mock_smtp.assert_called_once_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'testpass')
        mock_server.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, email_service):
        """Test email sending failure."""
        mock_smtp.return_value.__enter__.side_effect = Exception('SMTP Error')

        result = email_service.send_email(
            'recipient@test.com',
            'Test Subject',
            '<h1>Test HTML</h1>'
        )

        assert result is False

    def test_send_email_missing_credentials(self):
        """Test email service with missing credentials."""
        with patch.dict('os.environ', {}, clear=True):
            service = EmailNotificationService()

            with pytest.raises(ValueError):
                service.send_email('test@test.com', 'Subject', 'Body')

    @patch.object(EmailNotificationService, 'send_email')
    def test_notify_grade_release_success(self, mock_send_email, email_service, db_session,
                                        grade, student_profile, subject):
        """Test successful grade release notification."""
        mock_send_email.return_value = True

        # Release the grade first
        grade.is_released = True
        db_session.commit()

        result = email_service.notify_grade_release(
            student_profile.id,
            subject.id,
            '1st',
            '2025-2026'
        )

        assert result is True
        mock_send_email.assert_called_once()

        # Check email parameters
        call_args = mock_send_email.call_args
        assert call_args[0][0] == student_profile.user.email  # to_email
        assert 'Grade Released' in call_args[0][1]  # subject
        assert subject.subject_code in call_args[0][2]  # html_body

    def test_notify_grade_release_no_user_account(self, email_service, db_session,
                                                grade, student_profile, subject):
        """Test grade notification for student without user account."""
        # Remove user account
        student_profile.user_id = None
        grade.is_released = True
        db_session.commit()

        result = email_service.notify_grade_release(
            student_profile.id,
            subject.id,
            '1st',
            '2025-2026'
        )

        assert result is False

    def test_notify_grade_release_unreleased_grade(self, email_service, db_session,
                                                 grade, student_profile, subject):
        """Test notification for unreleased grade."""
        # Grade is not released by default

        result = email_service.notify_grade_release(
            student_profile.id,
            subject.id,
            '1st',
            '2025-2026'
        )

        assert result is False

    def test_generate_grade_notification_html(self, email_service, student_profile,
                                            subject, grade):
        """Test HTML email generation."""
        html = email_service._generate_grade_notification_html(
            student_profile, subject, grade, '1st', '2025-2026'
        )

        assert student_profile.full_name in html
        assert subject.subject_code in html
        assert subject.title in html
        assert '1.75' in html  # Grade value
        assert 'CICT Grade Portal' in html
        assert '1st Semester, 2025-2026' in html

    def test_generate_grade_notification_text(self, email_service, student_profile,
                                            subject, grade):
        """Test plain text email generation."""
        text = email_service._generate_grade_notification_text(
            student_profile, subject, grade, '1st', '2025-2026'
        )

        assert student_profile.full_name in text
        assert subject.subject_code in text
        assert subject.title in text
        assert '1.75' in text
        assert 'Grade Released' in text

    def test_generate_notification_with_remarks(self, email_service, student_profile,
                                              subject, enrollment, faculty_user, db_session):
        """Test notification generation for grade with remarks."""
        grade = Grade(
            enrollment_id=enrollment.id,
            grade_value=None,
            remarks='INC',
            date_encoded=datetime.now(timezone.utc),
            encoded_by_id=faculty_user.id,
            is_released=True
        )
        db_session.add(grade)
        db_session.commit()

        html = email_service._generate_grade_notification_html(
            student_profile, subject, grade, '1st', '2025-2026'
        )

        assert 'INC' in html
        assert student_profile.full_name in html

    @patch.object(EmailNotificationService, 'notify_grade_release')
    def test_notify_bulk_grade_release(self, mock_notify, email_service, db_session,
                                     grade, student_profile, subject, faculty_user):
        """Test bulk grade release notifications."""
        mock_notify.return_value = True

        # Release the grade
        grade.is_released = True
        grade.released_by_id = faculty_user.id
        db_session.commit()

        result = email_service.notify_bulk_grade_release(
            subject.id, '1st', '2025-2026', faculty_user
        )

        assert result == 1
        mock_notify.assert_called_once_with(
            student_profile.id, subject.id, '1st', '2025-2026'
        )


class TestBackgroundTasks:

    def test_task_manager_initialization(self):
        """Test background task manager initialization."""
        from app.utils.background_tasks import BackgroundTaskManager

        manager = BackgroundTaskManager()
        assert not manager.is_running
        assert manager.stats['tasks_total'] == 0

    def test_task_manager_start_stop(self):
        """Test starting and stopping task manager."""
        from app.utils.background_tasks import BackgroundTaskManager

        manager = BackgroundTaskManager()
        manager.start()
        assert manager.is_running
        assert manager.worker_thread is not None

        manager.stop()
        assert not manager.is_running

    def test_add_task(self):
        """Test adding tasks to queue."""
        from app.utils.background_tasks import BackgroundTaskManager

        manager = BackgroundTaskManager()

        def dummy_task():
            return True

        manager.add_task(dummy_task)
        assert manager.stats['tasks_total'] == 1
        assert manager.task_queue.qsize() == 1

    def test_get_stats(self):
        """Test getting task manager statistics."""
        from app.utils.background_tasks import BackgroundTaskManager

        manager = BackgroundTaskManager()
        stats = manager.get_stats()

        assert 'tasks_total' in stats
        assert 'tasks_completed' in stats
        assert 'tasks_failed' in stats
        assert 'queue_size' in stats
        assert 'is_running' in stats