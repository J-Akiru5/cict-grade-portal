"""
Seed script to set up user accounts, update passwords, and link to student/faculty records.
Run with: python seed_accounts.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    from app import create_app
    from app.extensions import db
    from app.models.user import User
    from app.models.student import Student
    from app.models.faculty import Faculty
    from supabase import create_client

    app = create_app()

    with app.app_context():
        url = os.environ['SUPABASE_URL']
        service_key = os.environ['SUPABASE_SERVICE_KEY']
        admin_client = create_client(url, service_key)

        # ── Account definitions ──
        accounts = [
            {
                'email': 'danitarasreb@isufst.edu.ph',
                'password': 'cictfaculty2026',
                'role': 'faculty',
            },
            {
                'email': 'jeffmartinez@isufst.edu.ph',
                'password': 'cictstudent2026',
                'role': 'student',
            },
            {
                'email': 'assimangca@isufst.edu.ph',
                'password': 'cictstudent2026',
                'role': 'student',
            },
        ]

        for acct in accounts:
            email = acct['email']
            password = acct['password']
            role = acct['role']

            print(f"\n--- Processing: {email} (role: {role}) ---")

            # Step 1: Find or create Supabase Auth user
            sb_user = None
            try:
                # List users and find by email
                response = admin_client.auth.admin.list_users()
                for u in response:
                    if u.email == email:
                        sb_user = u
                        break
            except Exception as e:
                print(f"  [!] Error listing Supabase users: {e}")

            if sb_user:
                print(f"  [+] Found existing Supabase user: {sb_user.id}")
                # Update password
                try:
                    admin_client.auth.admin.update_user_by_id(
                        str(sb_user.id),
                        {'password': password}
                    )
                    print(f"  [+] Password updated successfully")
                except Exception as e:
                    print(f"  [!] Error updating password: {e}")
            else:
                print(f"  [*] Supabase user not found, creating...")
                try:
                    response = admin_client.auth.admin.create_user({
                        'email': email,
                        'password': password,
                        'email_confirm': True,
                        'user_metadata': {'role': role},
                    })
                    sb_user = response.user
                    print(f"  [+] Created Supabase user: {sb_user.id}")
                except Exception as e:
                    print(f"  [!] Error creating Supabase user: {e}")
                    continue

            sb_user_id = str(sb_user.id)

            # Step 2: Ensure local User record exists
            user = db.session.get(User, sb_user_id)
            if not user:
                user = User.query.filter_by(email=email).first()
                if user:
                    print(f"  [*] Found local user by email, updating ID to match Supabase")
                    user.id = sb_user_id
                else:
                    user = User(id=sb_user_id, email=email, role=role, is_active=True)
                    db.session.add(user)
                    print(f"  [+] Created local User record")

            user.role = role
            user.is_active = True
            db.session.flush()
            print(f"  [+] Local User: id={user.id}, role={user.role}, active={user.is_active}")

            # Step 3: Link to profile records
            if role == 'faculty':
                faculty = Faculty.query.filter_by(user_id=sb_user_id).first()
                if not faculty:
                    # Try to find by name pattern from email
                    name_from_email = email.split('@')[0]
                    faculty = Faculty.query.filter(
                        Faculty.full_name.ilike(f'%{name_from_email}%')
                    ).first()
                    if faculty and not faculty.user_id:
                        faculty.user_id = sb_user_id
                        print(f"  [+] Linked to existing faculty: {faculty.full_name}")
                    elif not faculty:
                        # Create new faculty record
                        faculty = Faculty(
                            user_id=sb_user_id,
                            full_name=name_from_email.replace('.', ' ').title(),
                            department='CICT',
                        )
                        db.session.add(faculty)
                        print(f"  [+] Created faculty profile: {faculty.full_name}")
                    else:
                        print(f"  [*] Faculty already linked to another user: {faculty.full_name}")
                else:
                    print(f"  [+] Faculty profile already linked: {faculty.full_name}")

            elif role == 'student':
                student = Student.query.filter_by(user_id=sb_user_id).first()
                if not student:
                    # Try to find student by gmail matching email
                    student = Student.query.filter(
                        db.or_(
                            Student.gmail.ilike(f'%{email}%'),
                            Student.gmail.ilike(f'%{email.split("@")[0]}%'),
                        )
                    ).first()
                    if student and not student.user_id:
                        student.user_id = sb_user_id
                        print(f"  [+] Linked to existing student by gmail: {student.full_name} ({student.student_id})")
                    else:
                        # Find any student with grades that doesn't have a user_id
                        from app.models.enrollment import Enrollment
                        from app.models.grade import Grade
                        unlinked_with_grades = (
                            Student.query
                            .filter(Student.user_id.is_(None))
                            .join(Enrollment)
                            .join(Grade)
                            .filter(Grade.grade_value.isnot(None))
                            .first()
                        )
                        if unlinked_with_grades:
                            unlinked_with_grades.user_id = sb_user_id
                            student = unlinked_with_grades
                            print(f"  [+] Linked to student with grades: {student.full_name} ({student.student_id})")
                        else:
                            # Check for any unlinked student
                            unlinked = Student.query.filter(Student.user_id.is_(None)).first()
                            if unlinked:
                                unlinked.user_id = sb_user_id
                                student = unlinked
                                print(f"  [+] Linked to unlinked student: {student.full_name} ({student.student_id})")
                            else:
                                print(f"  [!] No unlinked student records found to link")
                else:
                    print(f"  [+] Student profile already linked: {student.full_name} ({student.student_id})")

            db.session.commit()
            print(f"  [+] Done!")

        # Summary
        print("\n" + "=" * 60)
        print("ACCOUNT SETUP SUMMARY")
        print("=" * 60)
        for acct in accounts:
            user = User.query.filter_by(email=acct['email']).first()
            if user:
                profile = "N/A"
                if user.role == 'faculty' and user.faculty_profile:
                    profile = f"Faculty: {user.faculty_profile.full_name}"
                elif user.role == 'student' and user.student_profile:
                    profile = f"Student: {user.student_profile.full_name} ({user.student_profile.student_id})"
                print(f"  {acct['email']}")
                print(f"    Role: {user.role} | Active: {user.is_active} | Profile: {profile}")
            else:
                print(f"  {acct['email']} - NOT FOUND in local DB")
        print("=" * 60)


if __name__ == '__main__':
    main()
