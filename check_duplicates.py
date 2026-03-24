import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def main():
    db_url = os.getenv('DATABASE_URL')
    if not db_url: return
    if db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    if ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                email = 'assimangca@isufst.edu.ph'
                
                print("--- ALL Students matching 'Simangca' or email ---")
                cur.execute("SELECT id, user_id, full_name, gmail, student_id FROM students WHERE full_name ILIKE '%%Simangca%%' OR gmail ILIKE %s", (f"%{email}%",))
                for row in cur.fetchall():
                    print(f"ID: {row[0]}, User ID: {row[1]}, Name: {row[2]}, Email: {row[3]}, Student ID: {row[4]}")
                
                print("\n--- ANY Student linked to the target User ID (f5f24d41...) ---")
                # I'll use the ID from the previous check_db_v2 output if I can remember it. 
                # Better yet, search by the email's user ID.
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                user_row = cur.fetchone()
                if user_row:
                    uid = user_row[0]
                    print(f"User ID for {email}: {uid}")
                    cur.execute("SELECT id, full_name, student_id FROM students WHERE user_id = %s", (uid,))
                    for row in cur.fetchall():
                        print(f"Linked Student ID: {row[0]}, Name: {row[1]}, Student ID: {row[2]}")
                else:
                    print("No user found for email.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
