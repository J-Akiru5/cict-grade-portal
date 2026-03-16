from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(email='admin@isufst.edu.ph').first()
    if u:
        print(f"ID:{u.id}")
    else:
        print("NOT_FOUND")
