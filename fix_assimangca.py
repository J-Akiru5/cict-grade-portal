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
    password = 'cictstudent2026'

    print(f"--- Fixing Account: {email} ---")
    
    # 1. Ensure Supabase Auth user is correct
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
        try:
            admin_client.auth.admin.update_user_by_id(str(sb_user.id), {'password': password, 'email_confirm': True})
            print(f"Password reset for {email}")
        except Exception as e:
            print(f"Error updating Supabase user: {e}")

    sb_id = str(sb_user.id)

    # 2. Update Local DB
    if db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    if ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                # A. Handle users table
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                local_user = cur.fetchone()
                
                if local_user:
                    old_id = local_user[0]
                    if old_id != sb_id:
                        print(f"Updating local user ID {old_id} to {sb_id}")
                        # Update references in other tables first to avoid FK errors
                        # We'll check common tables: students, enrollments, audit_logs
                        cur.execute("UPDATE students SET user_id = %s WHERE user_id = %s", (sb_id, old_id))
                        cur.execute("UPDATE users SET id = %s, is_active = true WHERE id = %s", (sb_id, old_id))
                    else:
                        cur.execute("UPDATE users SET is_active = true WHERE id = %s", (sb_id,))
                        print("Local ID already matches.")
                else:
                    cur.execute("INSERT INTO users (id, email, role, is_active) VALUES (%s, %s, 'student', true)", (sb_id, email))
                    print("Inserted new local user.")

                # B. Fix student profile linkage
                # First, unlink anyone using this ID who is NOT Simangca
                cur.execute("UPDATE students SET user_id = NULL WHERE user_id = %s AND full_name NOT ILIKE '%%Simangca%%'", (sb_id,))
                
                # Now find Simangca and link them
                cur.execute("SELECT id, full_name FROM students WHERE full_name ILIKE '%%Simangca%%' OR gmail ILIKE %s", (f"%{email}%",))
                sim_row = cur.fetchone()
                if sim_row:
                    sim_id = sim_row[0]
                    cur.execute("UPDATE students SET user_id = %s, gmail = %s WHERE id = %s", (sb_id, email, sim_id))
                    print(f"Linked Student '{sim_row[1]}' (ID: {sim_id}) to User ID {sb_id}")
                else:
                    print("Could not find a student profile for Simangca to link.")
                
                conn.commit()
                print("--- Fix Applied Successfully ---")
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == '__main__':
    main()
