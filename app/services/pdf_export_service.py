"""
PDF Export Service for Grade Portal.

Generates branded PDF reports for grades using ReportLab.
Report types: Semester grades, Subject grades, Student transcript
"""
import io
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

from flask import current_app

from app.extensions import db
from app.models.student import Student
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services import gwa_service


# Brand colors
MAROON = colors.HexColor('#800000')
GOLD = colors.HexColor('#D4AF37')
DARK_GRAY = colors.HexColor('#374151')
LIGHT_GRAY = colors.HexColor('#F3F4F6')


def _get_logo_path():
    """Get the path to the CICT logo."""
    # Try different possible paths
    possible_paths = [
        os.path.join(current_app.root_path, 'static', 'img', 'cict-logo.png'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'cict-logo.png'),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def _create_styles():
    """Create custom paragraph styles for reports."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=MAROON,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_GRAY,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=MAROON,
        spaceBefore=12,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='InfoText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK_GRAY,
    ))

    styles.add(ParagraphStyle(
        name='FooterText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER,
    ))

    return styles


def _create_header(title, subtitle=None):
    """Create branded header with CICT logo."""
    elements = []
    styles = _create_styles()

    logo_path = _get_logo_path()

    # Header table with logo and text
    header_data = []

    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
            header_data.append([
                logo,
                [
                    Paragraph("COLLEGE OF INFORMATION AND<br/>COMMUNICATIONS TECHNOLOGY", styles['ReportTitle']),
                    Paragraph("Isabela State University - Echague Campus", styles['ReportSubtitle']),
                ]
            ])
        except Exception:
            header_data.append([
                '',
                [
                    Paragraph("COLLEGE OF INFORMATION AND<br/>COMMUNICATIONS TECHNOLOGY", styles['ReportTitle']),
                    Paragraph("Isabela State University - Echague Campus", styles['ReportSubtitle']),
                ]
            ])
    else:
        header_data.append([
            '',
            [
                Paragraph("COLLEGE OF INFORMATION AND<br/>COMMUNICATIONS TECHNOLOGY", styles['ReportTitle']),
                Paragraph("Isabela State University - Echague Campus", styles['ReportSubtitle']),
            ]
        ])

    header_table = Table(header_data, colWidths=[1*inch, 5.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    elements.append(header_table)

    # Title
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(title, styles['ReportTitle']))

    if subtitle:
        elements.append(Paragraph(subtitle, styles['ReportSubtitle']))

    # Divider line
    elements.append(Spacer(1, 6))
    divider = Table([['']], colWidths=[6.5*inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, MAROON),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 12))

    return elements


def _create_grade_table(headers, data, col_widths=None):
    """Create a styled grade table."""
    table_data = [headers] + data

    if col_widths is None:
        col_widths = [1.2*inch] * len(headers)

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), MAROON),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Data rows style
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),

        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BOX', (0, 0), (-1, -1), 1, MAROON),
    ]))

    return table


def _get_remarks(grade):
    """Get remarks text for a grade."""
    if grade.remarks == 'INC':
        return 'INCOMPLETE'
    elif grade.remarks == 'DRP':
        return 'DROPPED'
    elif grade.grade_value is not None:
        if grade.grade_value <= 3.0:
            return 'PASSED'
        else:
            return 'FAILED'
    return '-'


def export_semester_grades(semester: str, academic_year: str) -> io.BytesIO:
    """
    Generate master grade list for all students in a semester.
    Returns: BytesIO PDF buffer
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    styles = _create_styles()
    elements = []

    # Header
    elements.extend(_create_header(
        "SEMESTER GRADE REPORT",
        f"{semester} Semester, Academic Year {academic_year}"
    ))

    # Get all enrollments for this semester with grades
    enrollments = Enrollment.query.filter_by(
        semester=semester,
        academic_year=academic_year
    ).join(Student).order_by(Student.full_name).all()

    if not enrollments:
        elements.append(Paragraph(
            "No enrollments found for this semester.",
            styles['InfoText']
        ))
    else:
        # Group by student and calculate GWA
        student_data = {}
        for enrollment in enrollments:
            student = enrollment.student
            if student.id not in student_data:
                student_data[student.id] = {
                    'student': student,
                    'enrollments': [],
                    'grades': [],
                }
            student_data[student.id]['enrollments'].append(enrollment)
            if enrollment.grade:
                student_data[student.id]['grades'].append(enrollment.grade)

        # Create table data
        headers = ['Student ID', 'Full Name', 'Section', 'Subjects', 'GWA', 'Status']
        data = []

        for sid, sdata in student_data.items():
            student = sdata['student']
            grades = sdata['grades']
            gwa = gwa_service.compute_gwa(grades)
            status = gwa_service.get_gwa_status(gwa)

            gwa_str = f"{gwa:.2f}" if gwa is not None else "N/A"
            section = student.section or "-"

            data.append([
                student.student_id,
                student.full_name,
                section,
                str(len(sdata['enrollments'])),
                gwa_str,
                status['label'],
            ])

        # Create table
        col_widths = [1.1*inch, 2*inch, 0.9*inch, 0.7*inch, 0.7*inch, 1.1*inch]
        table = _create_grade_table(headers, data, col_widths)
        elements.append(table)

        # Summary
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"<b>Total Students:</b> {len(student_data)}",
            styles['InfoText']
        ))

    # Footer with generation timestamp
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['FooterText']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def export_subject_grades(subject_id: int, semester: str, academic_year: str) -> io.BytesIO:
    """
    Generate class list with grades for a specific subject.
    Returns: BytesIO PDF buffer
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    styles = _create_styles()
    elements = []

    # Get subject
    subject = db.session.get(Subject, subject_id)
    if not subject:
        elements.extend(_create_header("SUBJECT GRADE REPORT", "Subject Not Found"))
        elements.append(Paragraph("The specified subject was not found.", styles['InfoText']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    # Header
    subject_title = f"{subject.code} - {subject.title}" if hasattr(subject, 'code') else f"{subject.subject_code} - {subject.title}"
    elements.extend(_create_header(
        "SUBJECT GRADE REPORT",
        f"{subject_title}<br/>{semester} Semester, Academic Year {academic_year}"
    ))

    # Subject info
    elements.append(Paragraph(
        f"<b>Units:</b> {subject.units}",
        styles['InfoText']
    ))
    elements.append(Spacer(1, 12))

    # Get enrollments for this subject
    enrollments = Enrollment.query.filter_by(
        subject_id=subject_id,
        semester=semester,
        academic_year=academic_year
    ).join(Student).order_by(Student.full_name).all()

    if not enrollments:
        elements.append(Paragraph(
            "No students enrolled in this subject for the selected period.",
            styles['InfoText']
        ))
    else:
        # Create table data
        headers = ['#', 'Student ID', 'Full Name', 'Section', 'Grade', 'Remarks']
        data = []
        passed = failed = incomplete = dropped = no_grade = 0

        for i, enrollment in enumerate(enrollments, start=1):
            student = enrollment.student
            grade = enrollment.grade

            if grade and grade.grade_value is not None:
                grade_str = f"{grade.grade_value:.2f}"
                remarks = _get_remarks(grade)
                if grade.grade_value <= 3.0:
                    passed += 1
                else:
                    failed += 1
            elif grade and grade.remarks == 'INC':
                grade_str = "-"
                remarks = "INCOMPLETE"
                incomplete += 1
            elif grade and grade.remarks == 'DRP':
                grade_str = "-"
                remarks = "DROPPED"
                dropped += 1
            else:
                grade_str = "-"
                remarks = "NOT ENCODED"
                no_grade += 1

            data.append([
                str(i),
                student.student_id,
                student.full_name,
                student.section or "-",
                grade_str,
                remarks,
            ])

        # Create table
        col_widths = [0.4*inch, 1.1*inch, 2.2*inch, 0.9*inch, 0.7*inch, 1.2*inch]
        table = _create_grade_table(headers, data, col_widths)
        elements.append(table)

        # Summary
        elements.append(Spacer(1, 12))
        summary_text = f"""
        <b>Summary:</b> {len(enrollments)} student(s) |
        Passed: {passed} |
        Failed: {failed} |
        Incomplete: {incomplete} |
        Dropped: {dropped} |
        Not Encoded: {no_grade}
        """
        elements.append(Paragraph(summary_text, styles['InfoText']))

    # Footer
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['FooterText']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def export_student_transcript(
    student_id: int,
    semester: str = None,
    academic_year: str = None
) -> io.BytesIO:
    """
    Generate individual student transcript.
    If semester/year provided, filter to that period only.
    Returns: BytesIO PDF buffer
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    styles = _create_styles()
    elements = []

    # Get student
    student = db.session.get(Student, student_id)
    if not student:
        elements.extend(_create_header("TRANSCRIPT OF RECORDS", "Student Not Found"))
        elements.append(Paragraph("The specified student was not found.", styles['InfoText']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    # Header
    elements.extend(_create_header(
        "TRANSCRIPT OF RECORDS",
        None
    ))

    # Student info
    info_data = [
        ['Student ID:', student.student_id, 'Section:', student.section or '-'],
        ['Name:', student.full_name.upper(), 'Year Level:', str(student.year_level or '-')],
        ['Program:', 'Bachelor of Science in Information Technology', '', ''],
    ]
    info_table = Table(info_data, colWidths=[1*inch, 2.5*inch, 1*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), MAROON),
        ('TEXTCOLOR', (2, 0), (2, -1), MAROON),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    # Get enrollments
    query = Enrollment.query.filter_by(student_id=student.id)
    if semester and academic_year:
        query = query.filter_by(semester=semester, academic_year=academic_year)

    enrollments = query.join(Subject).order_by(
        Enrollment.academic_year,
        Enrollment.semester,
        Subject.code if hasattr(Subject, 'code') else Subject.subject_code
    ).all()

    if not enrollments:
        elements.append(Paragraph(
            "No enrollment records found for this student.",
            styles['InfoText']
        ))
    else:
        # Group by academic period
        periods = {}
        all_grades = []

        for enrollment in enrollments:
            period_key = f"{enrollment.semester} Semester {enrollment.academic_year}"
            if period_key not in periods:
                periods[period_key] = []
            periods[period_key].append(enrollment)
            if enrollment.grade:
                all_grades.append(enrollment.grade)

        # Create tables for each period
        for period, period_enrollments in periods.items():
            elements.append(Paragraph(period.upper(), styles['SectionHeader']))

            headers = ['Code', 'Subject Title', 'Units', 'Grade', 'Remarks']
            data = []
            period_grades = []
            total_units = 0

            for enrollment in period_enrollments:
                subject = enrollment.subject
                grade = enrollment.grade
                code = subject.code if hasattr(subject, 'code') else subject.subject_code

                total_units += subject.units

                if grade and grade.grade_value is not None:
                    grade_str = f"{grade.grade_value:.2f}"
                    remarks = _get_remarks(grade)
                    period_grades.append(grade)
                elif grade and grade.remarks:
                    grade_str = "-"
                    remarks = grade.remarks
                else:
                    grade_str = "-"
                    remarks = "-"

                data.append([
                    code,
                    subject.title,
                    str(subject.units),
                    grade_str,
                    remarks,
                ])

            col_widths = [0.9*inch, 2.8*inch, 0.6*inch, 0.7*inch, 1.5*inch]
            table = _create_grade_table(headers, data, col_widths)
            elements.append(table)

            # Period GWA
            period_gwa = gwa_service.compute_gwa(period_grades)
            gwa_str = f"{period_gwa:.4f}" if period_gwa is not None else "N/A"
            elements.append(Paragraph(
                f"<b>Units:</b> {total_units} | <b>GWA:</b> {gwa_str}",
                styles['InfoText']
            ))
            elements.append(Spacer(1, 12))

        # Cumulative GWA
        cumulative_gwa = gwa_service.compute_gwa(all_grades)
        gwa_status = gwa_service.get_gwa_status(cumulative_gwa)
        cumulative_str = f"{cumulative_gwa:.4f}" if cumulative_gwa is not None else "N/A"

        elements.append(Spacer(1, 6))
        summary_table = Table([
            ['CUMULATIVE GWA:', cumulative_str, gwa_status['label']]
        ], colWidths=[1.5*inch, 1*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, 0), MAROON),
            ('TEXTCOLOR', (1, 0), (1, 0), MAROON),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, MAROON),
        ]))
        elements.append(summary_table)

    # Footer
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        "*** NOTHING FOLLOWS ***",
        styles['FooterText']
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['FooterText']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
