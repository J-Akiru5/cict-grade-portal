import os
import psycopg
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    db_url = os.environ.get('DATABASE_URL')
    
    if not all([url, key, db_url]):
        print("Missing environment variables.")
        return

    admin_client = create_client(url, key)
    email = 'assimangca@isufst.edu.ph'
    password = 'cictstudent2026' # Standard seed password

    print(f"--- Synchronizing: {email} ---")
    
    # 1. Get Supabase User
    sb_user = None
    try:
        response = admin_client.auth.admin.list_users()
        for u in response:
            if u.email == email:
                sb_user = u
                break
    except Exception as e:
        print(f"Error listing Supabase users: {e}")
        return

    if not sb_user:
        print("Supabase user not found. Creating...")
        try:
            response = admin_client.auth.admin.create_user({
                'email': email,
                'password': password,
                'email_confirm': True,
                'user_metadata': {'role': 'student'}
            })
            sb_user = response.user
            print(f"Created Supabase user: {sb_user.id}")
        except Exception as e:
            print(f"Error creating Supabase user: {e}")
            return
    else:
        print(f"Found Supabase user: {sb_user.id}")
        # Reset password to be sure
        try:
            admin_client.auth.admin.update_user_by_id(str(sb_user.id), {'password': password})
            print("Password reset to cictstudent2026")
        except Exception as e:
            print(f"Error resetting password: {e}")

    sb_id = str(sb_user.id)

    # 2. Update Local DB
    if db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    if ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                # Check for existing user with different ID
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                local_user = cur.fetchone()
                
                if local_user:
                    old_id = local_user[0]
                    if old_id != sb_id:
                        print(f"ID Mismatch! Local: {old_id}, Supabase: {sb_id}")
                        print("Updating local user ID...")
                        # We need to update ID in users and its FKs if any
                        # But since it's a UUID PK, it's easier to just swap it if no FKs yet?
                        # Or update users table first.
                        try:
                            # Update the ID. Note: This might fail if there are FKs with ON UPDATE NO ACTION.
                            cur.execute("UPDATE users SET id = %s WHERE id = %s", (sb_id, old_id))
                            print("Updated user ID.")
                        except Exception as e:
                            print(f"Error updating user ID: {e}. Trying deletion and re-insertion.")
                            conn.rollback()
                            cur.execute("DELETE FROM users WHERE email = %s", (email,))
                            cur.execute("INSERT INTO users (id, email, role, is_active) VALUES (%s, %s, 'student', true)", (sb_id, email))
                            print("Re-inserted user with correct ID.")
                    else:
                        print("Local ID matches Supabase.")
                else:
                    print("No local user found. Inserting...")
                    cur.execute("INSERT INTO users (id, email, role, is_active) VALUES (%s, %s, 'student', true)", (sb_id, email))
                    print("Inserted user.")

                # Link Student Profile
                cur.execute("SELECT id FROM students WHERE full_name ILIKE '%Simangca%' OR gmail ILIKE %s", (f"%{email}%",))
                student_row = cur.fetchone()
                if student_row:
                    student_id = student_row[0]
                    cur.execute("UPDATE students SET user_id = %s, gmail = %s WHERE id = %s", (sb_id, email, student_id))
                    print(f"Linked student profile {student_id} to user {sb_id}")
                else:
                    print("No student profile found to link.")
                
                conn.commit()
                print("--- Synchronization Complete ---")
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == '__main__':
    main()
