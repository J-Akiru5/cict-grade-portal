import sys, os, traceback
sys.path.insert(0, '.')
os.environ['FLASK_DEBUG'] = '1'

from app import create_app
from flask_login import FlaskLoginClient

app = create_app()
app.config['TESTING'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.test_client_class = FlaskLoginClient

with app.app_context():
    from app.models.user import User
    # Find assimangca to test with
    student_user = User.query.filter_by(email='assimangca@isufst.edu.ph').first()
    if not student_user:
        student_user = User.query.filter_by(role='student').first()
    print(f'Testing as: {student_user.email} (role={student_user.role})')
    
    with app.test_client(user=student_user) as client:
        print('\n--- Testing /student/grades ---')
        try:
            resp = client.get('/student/grades')
            print(f'STATUS: {resp.status_code}')
            if resp.status_code >= 400:
                data = resp.data.decode('utf-8', errors='replace')
                print(data[:3000])
        except Exception as e:
            print(f'Exception: {e}')
            traceback.print_exc()
