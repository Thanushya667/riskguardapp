from database import db
from models.user import User

def seed_database(app):
    """
    Initializes database tables.
    All predefined/demo student and alert data has been removed.
    Only the default admin account is initialized if not present.
    """
    with app.app_context():
        db.create_all()

        # Initialize default admin user only
        if not User.query.filter_by(username='admin').first():
            print("Initializing default admin account...")
            admin = User(
                username='admin',
                email='admin@university.edu',
                full_name='System Administrator',
                role='Admin',
                department='Institutional Administration'
            )
            admin.set_password('admin@123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin account initialized.")

if __name__ == '__main__':
    from flask import Flask
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    seed_database(app)
