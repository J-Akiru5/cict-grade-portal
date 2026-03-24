"""
Email notification service for grade release and other system events.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timezone
from typing import List, Optional
import logging

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.subject import Subject

logger = logging.getLogger(__name__)


class EmailNotificationService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.from_name = os.getenv('FROM_NAME', 'CICT Grade Portal')

    def _create_smtp_connection(self):
        """Create and return authenticated SMTP connection."""
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables.")

        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.smtp_username, self.smtp_password)
        return server

    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """
        Send an email to the specified recipient.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add plain text version if provided
            if text_body:
                msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

            # Add HTML version
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Send email
            with self._create_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def notify_grade_release(self, student_id: int, subject_id: int, semester: str, academic_year: str) -> bool:
        """
        Send grade release notification to a student.

        Args:
            student_id: Student database ID
            subject_id: Subject database ID
            semester: Academic semester
            academic_year: Academic year

        Returns:
            bool: True if notification sent successfully
        """
        try:
            # Get student and subject information
            student = Student.query.get(student_id)
            subject = Subject.query.get(subject_id)

            if not student or not subject:
                logger.error(f"Student {student_id} or subject {subject_id} not found for grade notification")
                return False

            # Check if student has an associated user account with email
            if not student.user_id:
                logger.info(f"Student {student.student_id} has no user account - skipping email notification")
                return False

            user = User.query.get(student.user_id)
            if not user or not user.email:
                logger.info(f"Student {student.student_id} has no email - skipping notification")
                return False

            # Get the released grades for this student and subject
            enrollment = Enrollment.query.filter_by(
                student_id=student.id,
                subject_id=subject.id,
                semester=semester,
                academic_year=academic_year
            ).first()

            if not enrollment or not enrollment.grade:
                logger.error(f"No enrollment or grade found for student {student.student_id} in {subject.subject_code}")
                return False

            grade = enrollment.grade
            if not grade.is_released:
                logger.error(f"Grade for student {student.student_id} in {subject.subject_code} is not released")
                return False

            # Generate email content
            subject_line = f"Grade Released: {subject.subject_code} - {subject.title}"

            html_body = self._generate_grade_notification_html(
                student, subject, grade, semester, academic_year
            )

            text_body = self._generate_grade_notification_text(
                student, subject, grade, semester, academic_year
            )

            # Send email
            return self.send_email(user.email, subject_line, html_body, text_body)

        except Exception as e:
            logger.error(f"Error sending grade notification: {str(e)}")
            return False

    def notify_bulk_grade_release(self, subject_id: int, semester: str, academic_year: str, released_by_user) -> int:
        """
        Send grade release notifications to all students in a subject.

        Returns:
            int: Number of notifications sent successfully
        """
        try:
            subject = Subject.query.get(subject_id)
            if not subject:
                logger.error(f"Subject {subject_id} not found for bulk notification")
                return 0

            # Get all students with released grades for this subject
            enrollments = (
                db.session.query(Enrollment)
                .join(Grade)
                .join(Student)
                .filter(
                    Enrollment.subject_id == subject_id,
                    Enrollment.semester == semester,
                    Enrollment.academic_year == academic_year,
                    Grade.is_released == True,
                    Grade.released_by_id == released_by_user.id
                )
                .all()
            )

            successful_notifications = 0

            for enrollment in enrollments:
                if self.notify_grade_release(
                    enrollment.student_id, subject_id, semester, academic_year
                ):
                    successful_notifications += 1

            logger.info(f"Sent {successful_notifications}/{len(enrollments)} grade release notifications for {subject.subject_code}")
            return successful_notifications

        except Exception as e:
            logger.error(f"Error sending bulk grade notifications: {str(e)}")
            return 0

    def _generate_grade_notification_html(self, student: Student, subject: Subject, grade: Grade, semester: str, academic_year: str) -> str:
        """Generate HTML email body for grade notification."""
        grade_display = f"{grade.grade_value:.2f}" if grade.grade_value else grade.remarks or "Not Encoded"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background-color: #800000; color: white; padding: 30px 40px; text-align: center; }}
                .content {{ padding: 40px; }}
                .grade-card {{ background-color: #f8fafc; border: 2px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center; }}
                .grade-value {{ font-size: 36px; font-weight: bold; color: #1e293b; font-family: monospace; }}
                .footer {{ background-color: #f8fafc; padding: 20px 40px; text-align: center; font-size: 14px; color: #64748b; }}
                .button {{ display: inline-block; background-color: #800000; color: white; text-decoration: none; padding: 12px 24px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Grade Released</h1>
                    <p>CICT Grade Portal - ISUFST Dingle</p>
                </div>

                <div class="content">
                    <p>Dear <strong>{student.full_name}</strong>,</p>

                    <p>Your grade for the following subject has been released:</p>

                    <div class="grade-card">
                        <h2 style="margin: 0 0 10px 0; color: #1e293b;">{subject.subject_code}</h2>
                        <h3 style="margin: 0 0 20px 0; color: #64748b; font-weight: normal;">{subject.title}</h3>
                        <div class="grade-value">{grade_display}</div>
                        <p style="margin: 10px 0 0 0; color: #64748b;">{semester} Semester, {academic_year}</p>
                    </div>

                    <p>You can view your complete grade record by logging into the CICT Grade Portal.</p>

                    <p style="text-align: center;">
                        <a href="#" class="button">View Grade Portal</a>
                    </p>

                    <p style="font-size: 14px; color: #64748b; margin-top: 30px;">
                        <strong>Note:</strong> This is an automated notification from the CICT Grade Portal system.
                        If you have questions about your grade, please contact your instructor or the registrar's office.
                    </p>
                </div>

                <div class="footer">
                    <p>© 2026 ISUFST Dingle - College of Information and Communications Technology</p>
                    <p>This email was sent to {student.user.email if student.user else 'your registered email'}</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_grade_notification_text(self, student: Student, subject: Subject, grade: Grade, semester: str, academic_year: str) -> str:
        """Generate plain text email body for grade notification."""
        grade_display = f"{grade.grade_value:.2f}" if grade.grade_value else grade.remarks or "Not Encoded"

        return f"""
Grade Released - CICT Grade Portal

Dear {student.full_name},

Your grade for the following subject has been released:

Subject: {subject.subject_code} - {subject.title}
Grade: {grade_display}
Semester: {semester} Semester, {academic_year}

You can view your complete grade record by logging into the CICT Grade Portal.

Note: This is an automated notification from the CICT Grade Portal system.
If you have questions about your grade, please contact your instructor or the registrar's office.

---
© 2026 ISUFST Dingle - College of Information and Communications Technology
This email was sent to {student.user.email if student.user else 'your registered email'}
        """.strip()


# Global service instance
email_service = EmailNotificationService()