import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def main():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found")
        return
        
    if db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
    # Supabase Transaction Pooler often works better on 6543
    if ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                email = 'assimangca@isufst.edu.ph'
                print(f"Checking ID for {email} in 'users' table...")
                cur.execute("SELECT id, email, role, is_active FROM users WHERE email = %s", (email,))
                rows = cur.fetchall()
                for row in rows:
                    print(f"ID: {row[0]}, Email: {row[1]}, Role: {row[2]}, Active: {row[3]}")
                
                print(f"\nChecking 'students' table for ANY record with 'Assi' or 'Simangca'...")
                cur.execute("SELECT id, user_id, full_name, gmail, student_id FROM students WHERE full_name ILIKE '%Simangca%' OR gmail ILIKE '%assimangca%'")
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        print(f"ID: {row[0]}, User ID: {row[1]}, Name: {row[2]}, Email: {row[3]}, Student ID: {row[4]}")
                else:
                    print("No matching student records found.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
