import os
from dotenv import load_dotenv
from supabase import create_client
import psycopg

load_dotenv()

def main():
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    db_url = os.environ.get('DATABASE_URL')
    
    if not all([url, service_key, db_url]):
        print("Missing environment variables.")
        return

    admin_client = create_client(url, service_key)
    
    accounts = [
        {
            'email': 'assimangca@isufst.edu.ph',
            'password': 'cictstudent2026',
            'role': 'student',
        },
    ]

    if db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    if ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            for acct in accounts:
                email = acct['email']
                password = acct['password']
                role = acct['role']

                print(f"\n--- Processing: {email} ---")

                # Step 1: Find or Create Supabase User
                sb_user = None
                try:
                    response = admin_client.auth.admin.list_users()
                    for u in response:
                        if u.email == email:
                            sb_user = u
                            break
                except Exception as e:
                    print(f"  [!] Error listing Supabase users: {e}")
                    continue

                if sb_user:
                    print(f"  [+] Found Supabase user: {sb_user.id}")
                    try:
                        admin_client.auth.admin.update_user_by_id(
                            str(sb_user.id),
                            {'password': password, 'email_confirm': True}
                        )
                        print("  [+] Password reset and email confirmed in Supabase")
                    except Exception as e:
                        print(f"  [!] Error updating Supabase user: {e}")
                else:
                    print("  [*] Creating Supabase user...")
                    try:
                        response = admin_client.auth.admin.create_user({
                            'email': email,
                            'password': password,
                            'email_confirm': True,
                            'user_metadata': {'role': role}
                        })
                        sb_user = response.user
                        print(f"  [+] Created Supabase user: {sb_user.id}")
                    except Exception as e:
                        print(f"  [!] Error creating Supabase user: {e}")
                        continue

                sb_id = str(sb_user.id)

                # Step 2: Sync Local User
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                local_row = cur.fetchone()
                if local_row:
                    if local_row[0] != sb_id:
                        print(f"  [!] ID Mismatch. Updating local ID {local_row[0]} -> {sb_id}")
                        # We must update references too. 
                        # In this app, references are mainly in 'students', 'audit_logs', etc.
                        # For simplicity, if it's a seed account, we can just delete and recreate if update fails.
                        try:
                            # Update references first
                            cur.execute("UPDATE students SET user_id = %s WHERE user_id = %s", (sb_id, local_row[0]))
                            cur.execute("UPDATE users SET id = %s, is_active = true WHERE id = %s", (sb_id, local_row[0]))
                            print("  [+] Local ID updated.")
                        except Exception as e:
                            print(f"  [!] Update failed: {e}. Re-creating user.")
                            conn.rollback()
                            cur.execute("DELETE FROM users WHERE email = %s", (email,))
                            cur.execute("INSERT INTO users (id, email, role, is_active) VALUES (%s, %s, %s, true)", (sb_id, email, role))
                    else:
                        cur.execute("UPDATE users SET is_active = true WHERE id = %s", (sb_id,))
                        print("  [+] Local User OK and Active.")
                else:
                    cur.execute("INSERT INTO users (id, email, role, is_active) VALUES (%s, %s, %s, true)", (sb_id, email, role))
                    print("  [+] Created Local User.")

                # Step 3: Ensure Student Link
                cur.execute("SELECT id FROM students WHERE gmail ILIKE %s OR full_name ILIKE '%%Simangca%%'", (f"%{email}%",))
                student_row = cur.fetchone()
                if student_row:
                    cur.execute("UPDATE students SET user_id = %s, gmail = %s WHERE id = %s", (sb_id, email, student_row[0]))
                    print(f"  [+] Linked Student profile {student_row[0]} to {sb_id}")
                else:
                    print("  [!] No student profile found to link.")

            conn.commit()

if __name__ == '__main__':
    main()
