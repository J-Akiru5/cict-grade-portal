import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    if not url or not service_key:
        print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return

    admin_client = create_client(url, service_key)
    email = 'assimangca@isufst.edu.ph'

    print(f"Checking Supabase Auth for {email}...")
    try:
        response = admin_client.auth.admin.list_users()
        sb_user = None
        for u in response:
            if u.email == email:
                sb_user = u
                break
        
        if sb_user:
            print(f"Supabase User Found:")
            print(f"  ID: {sb_user.id}")
            print(f"  Email: {sb_user.email}")
            print(f"  Metadata: {sb_user.user_metadata}")
            print(f"  Confirmed At: {sb_user.email_confirmed_at}")
            print(f"  Last Sign In: {sb_user.last_sign_in_at}")
        else:
            print("Supabase User NOT FOUND in Auth.")
    except Exception as e:
        print(f"Error checking Supabase: {e}")

    # Check local DB using psycopg directly to avoid app import issues
    import psycopg
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if db_url and db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    if db_url and ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    print(f"\nChecking Local Database for {email}...")
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cursor:
                # Check users table
                cursor.execute("SELECT id, email, role, is_active FROM users WHERE email = %s", (email,))
                user_rows = cursor.fetchall()
                if user_rows:
                    for row in user_rows:
                        print(f"Local User Record:")
                        print(f"  ID: {row[0]}")
                        print(f"  Email: {row[1]}")
                        print(f"  Role: {row[2]}")
                        print(f"  Active: {row[3]}")
                else:
                    print("Local User Record NOT FOUND.")

                # Check students table
                cursor.execute("SELECT id, user_id, full_name, student_id FROM students WHERE gmail ILIKE %s", (f"%{email}%",))
                student_row = cursor.fetchone()
                if student_row:
                    print(f"\nStudent Table Entry Found:")
                    print(f"  ID: {student_row[0]}")
                    print(f"  User ID: {student_row[1]}")
                    print(f"  Full Name: {student_row[2]}")
                    print(f"  Student ID: {student_row[3]}")
                else:
                    print("\nStudent Table Entry NOT FOUND by email.")
    except Exception as e:
        print(f"Error checking local DB: {e}")


if __name__ == '__main__':
    main()
