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
    admin = User.query.filter_by(role='admin').first()
    print(f'Testing as: {admin.email} (role={admin.role})')
    
    with app.test_client(user=admin) as client:
        # Test admin_students
        print('\n--- Testing /panel/admin/students ---')
        try:
            resp = client.get('/panel/admin/students')
            print(f'STATUS: {resp.status_code}')
            if resp.status_code >= 400:
                data = resp.data.decode('utf-8', errors='replace')
                print(data[:3000])
        except Exception as e:
            print(f'Exception: {e}')
            traceback.print_exc()
        
        # Test admin_grades
        print('\n--- Testing /panel/admin/grades ---')
        try:
            resp = client.get('/panel/admin/grades')
            print(f'STATUS: {resp.status_code}')
            if resp.status_code >= 400:
                data = resp.data.decode('utf-8', errors='replace')
                print(data[:3000])
        except Exception as e:
            print(f'Exception: {e}')
            traceback.print_exc()
