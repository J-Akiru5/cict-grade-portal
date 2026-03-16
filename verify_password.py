from app.services import auth_service
import os
from dotenv import load_dotenv

load_dotenv()

email = "admin@isufst.edu.ph"
password = "cictadmin2026"

print(f"Attempting to sign in as {email} with new password...")
try:
    response = auth_service.sign_in(email, password)
    if response.user and response.user.email == email:
        print("SUCCESS: Sign-in verified.")
    else:
        print("FAILURE: Unexpected response from sign-in.")
except Exception as e:
    print(f"FAILURE: Sign-in failed with error: {e}")
