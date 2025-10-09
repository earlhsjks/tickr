from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.sql import func
from datetime import time

db = SQLAlchemy()

### USERS ###
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    course = db.Column(db.String(50), nullable=True)
    year = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # String role for legacy/backend logic
    office_id = db.Column(db.Integer, db.ForeignKey('office.office_id'), nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='active')

    office = db.relationship('Office', backref='users', foreign_keys=[office_id])

    def has_permission(self, perm_name):
        return db.session.query(RolePermission).join(Permission).filter(
            RolePermission.role_id == self.role_id,
            Permission.name == perm_name
        ).first() is not None

    def set_password(self, password):
        self.password = generate_password_hash(password) if password else self.password

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.user_id}, Role={self.role}>"

### PERMISSIONS ###
class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)

    role = db.relationship('Role', backref='permissions')
    permission = db.relationship('Permission', backref='role_permissions')

### OFFICE ###
class Office(db.Model):
    __tablename__ = 'office'

    office_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    campus = db.Column(db.String(50), nullable=False)
    unit_head_id = db.Column(
        db.String(50),
        db.ForeignKey('user.user_id', use_alter=True),
        nullable=False
    )

    unit_head = db.relationship('User', foreign_keys=[unit_head_id], post_update=True)

    def __repr__(self):
        return f"<Office {self.name}, Campus={self.campus}>"

### ATTENDANCE ###
class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    clock_in = db.Column(db.Time, nullable=False)
    clock_out = db.Column(db.Time)
    remarks = db.Column(db.Text, nullable=True)  # fixed typo here

    user = db.relationship('User', backref='attendance_records')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_attendance_per_user'),
    )

    def __repr__(self):
        return f"<Attendance {self.user_id} on {self.date}>"

### SCHEDULE ###
class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_broken = db.Column(db.Boolean, default=False)
    second_start_time = db.Column(db.Time)
    second_end_time = db.Column(db.Time)

    user = db.relationship('User', backref='schedules')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'day', name='unique_schedule_per_user_day'),
    )

### GLOBAL SETTINGS ###
class GlobalSettings(db.Model):
    __tablename__ = 'global_settings'

    id = db.Column(db.Integer, primary_key=True, default=1)
    enable_strict_schedule = db.Column(db.Boolean, default=False)
    auto_clock_out_hours = db.Column(db.Integer, default=10)
    early_out_allowed = db.Column(db.Boolean, default=True)
    overtime_allowed = db.Column(db.Boolean, default=False)
    default_schedule_start = db.Column(db.Time, default=time(7, 30))
    default_schedule_end = db.Column(db.Time, default=time(20, 30))
    allowed_early_in = db.Column(db.Integer, default=0)

    @property
    def default_schedule(self):
        return type('DefaultSchedule', (object,), {
            'start_time': self.default_schedule_start,
            'end_time': self.default_schedule_end
        })()

    @staticmethod
    def get():
        return db.session.get(GlobalSettings, 1)

### ATTENDANCE INCONSISTENCIES ###
class AttendanceInconsistency(db.Model):
    __tablename__ = 'attendance_inconsistencies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)

    user = db.relationship("User", backref="inconsistencies")

    def __repr__(self):
        return f"<Inconsistency {self.issue_type} for {self.user_id} on {self.date}>"

### LOGS ###
class Logs(db.Model):
    __tablename__ = 'dtr_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False, index=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    details = db.Column(db.Text)

    user = db.relationship('User', backref='logs', lazy=True)

    def __repr__(self):
        return f"<Log action='{self.action}' by user_id='{self.user_id}' at {self.timestamp}>"
