from flask import (Blueprint, render_template, redirect, url_for, request, flash, 
                   send_file, session, request)
from flask_login import login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
import io
from collections import defaultdict
from datetime import datetime, timedelta, date, time
from models.models import db, User, Attendance, Schedule, GlobalSettings, Logs
from sqlalchemy.exc import IntegrityError
from flask_apscheduler import APScheduler

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Funtion of udate user schedule
def parse_time(time_str):
    """Convert string to time object, return None if empty or invalid."""
    if not time_str or time_str.strip() == "":  # Ensure empty strings return None
        return None
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None  # Handle incorrect formats safely

def systemLogEntry(userId, action, details=None):
    entry = Logs(
        userId = userId,
        action = action,
        details = details,
        timestamp = datetime.now()
    )

    db.session.add(entry)
    db.session.commit()

""" 
FUNTION FOR LOG LOGGING (example)
systemLogEntry(
    admin_id=current_user.user_id,
    action=f"Force Clocked Out {user_id}",
    details=f"Clock-out set to {attendance.clock_out.strftime('%Y-%m-%d %H:%M:%S')}"
)
 """
class Config:
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

# Auto Logout
@admin_bp.route('/logout')
def logout():
    logout_user()  # Logs out the user
    session.clear()  # Clears session data
    return render_template('auth/login.html')  # Redirect to login page

# Dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('auth_bp.login')) 
    
    total_employees = User.query.filter(User.role != "superadmin").count()

    today = datetime.now().date()
    
    completed_records = Attendance.query.filter(
        Attendance.date == today,
        Attendance.clock_out.isnot(None)
    ).all()

    total_seconds_worked = 0
    total_overtime_seconds = 0
    compliant_shifts_count = 0

    compliance_limit = timedelta(hours=4)
    overtime_threshold = timedelta(hours=4)
    
    for record in completed_records:
        dt_in = datetime.combine(record.date, record.clock_in)
        dt_out = datetime.combine(today, record.clock_out)
        
        duration = dt_out - dt_in
        total_seconds_worked += duration.total_seconds()

        if duration > overtime_threshold:
            overtime_duration = duration - overtime_threshold
            total_overtime_seconds += overtime_duration.total_seconds()

        if duration <= compliance_limit:
            compliant_shifts_count += 1

    total_hours_worked = total_seconds_worked / 3600
    overtime_hours = total_overtime_seconds / 3600

    num_completed_shifts = len(completed_records)
    if num_completed_shifts > 0:
        average_hours_worked = total_hours_worked / num_completed_shifts
    else:
        average_hours_worked = 0
        
    average_hours_worked = round(average_hours_worked, 2)
    overtime_hours = round(overtime_hours, 2)

    compliance_hours = compliant_shifts_count 

    return render_template(
        'admin/dashboard.html',
        user=current_user,
        total_employees=total_employees,
        average_hours_worked=average_hours_worked, 
        overtime_hours=overtime_hours,             
        compliance_hours=compliance_hours,
        current_time = datetime.now().strftime("%A, %B %d, %Y"),
    )

# VIEW USERS PAGE
@admin_bp.route('/users')
@login_required
def users():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/login.html')

    users = User.query.filter(User.role != "superadmin").all()

    return render_template('admin/users.html', current_user=current_user)

# GIA SCHEDULE PAGE
@admin_bp.route('/gia-schedule')
@login_required
def gia_schedule():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/login.html')
    
    users = User.query.filter(User.role == "gia").all()
    schedules = Schedule.query.all()

    return render_template('admin/schedule.html')

# DAILY LOGS PAGE
@admin_bp.route('/daily-logs', methods=['GET'])
@login_required
def daily_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/login.html')
    
    users = User.query.filter_by(role = 'gia').order_by(User.first_name).all()
    today = datetime.now().date()

    return render_template('admin/daily_logs.html', today=today, users=users)

# MANUAL LOGS PAGE
@admin_bp.route('/manual-logs')
@login_required
def manual_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/login.html')
    
    month = datetime.now().strftime("%Y-%m")

    return render_template('admin/manual_logs.html', month=month)

# EXPORT DTR PAGE
@admin_bp.route('/export-dtr')
@login_required
def export_dtr():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized access!", "danger")
        return render_template('auth/login.html')
    
    month = datetime.today().strftime('%Y-%m')

    return render_template('admin/export_dtr.html', month=month)

# DTR PRINT
@admin_bp.route('/export')
@login_required
def export_pdf():
    if current_user.role not in ["superadmin", "admin"]:
        return render_template('auth/login.html')

    unit_head = GlobalSettings.query.first()
    selected_month = request.args.get('month', '').strip() or datetime.today().strftime('%Y-%m')

    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        flash("Invalid month format. Defaulting to current month.", "warning")
        return redirect(url_for('admin.export_pdf', month=datetime.today().strftime('%Y-%m')))

    first_day = datetime(year, month, 1).date()
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    total_days = (last_day - first_day).days + 1

    users = User.query.filter(User.role.notin_(["superadmin", "admin"])) \
                      .order_by(User.last_name).all()

    attendance_records = Attendance.query.filter(
        Attendance.date >= first_day,
        Attendance.date <= last_day
    ).order_by(Attendance.date, Attendance.id).all()

    # use plain dict with string keys so Jinja lookup is predictable
    attendance_dict = {}
    total_hours_dict = {str(user.user_id): "0:00" for user in users}

    def to_datetime(val, record_date):
        """Normalize time/datetime/iso strings to a datetime on record_date."""
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, time):
            return datetime.combine(record_date, val)
        # attempt ISO parse/fallback
        try:
            return datetime.fromisoformat(str(val))
        except Exception:
            return None

    # Populate attendance records (use string date keys)
    for record in attendance_records:
        user_key = str(record.user_id)
        date_key = record.date.strftime('%Y-%m-%d')   # Attendance.date is a date

        attendance_dict.setdefault(user_key, {}).setdefault(date_key, {
            "shift1": {"in": None, "out": None},
            "shift2": {"in": None, "out": None}
        })

        slot = attendance_dict[user_key][date_key]

        cin = to_datetime(record.clock_in, record.date)
        cout = to_datetime(record.clock_out, record.date)

        # assign into first/second shift slots preserving order
        if cin and cout:
            if not slot["shift1"]["in"]:
                slot["shift1"]["in"] = cin
                slot["shift1"]["out"] = cout
            elif slot["shift1"]["out"] is None:
                slot["shift1"]["out"] = cout
            else:
                slot["shift2"]["in"] = cin
                slot["shift2"]["out"] = cout
        else:
            # Skip adding the shift since clock-out is missing
            pass

    # Calculate total hours per user
    for user in users:
        user_key = str(user.user_id)
        total_seconds = 0
        for date_key, shifts in attendance_dict.get(user_key, {}).items():
            for shift in ("shift1", "shift2"):
                t_in = shifts[shift]["in"]
                t_out = shifts[shift]["out"]
                if not t_in or not t_out:
                    continue
                start_dt = t_in
                end_dt = t_out
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                total_seconds += (end_dt - start_dt).total_seconds()

        decimal_hours = round(total_seconds / 3600, 2)  # convert to decimal hours
        total_hours_dict[user_key] = decimal_hours

    user_pairs = [users[i:i + 2] for i in range(0, len(users), 2)]

    return render_template(
        'admin/dtr_report.html',
        now=datetime.now(),
        user_pairs=user_pairs,
        month=month,
        year=year,
        total_days=total_days,
        datetime=datetime,
        unit_head=unit_head.unit_head if unit_head else "N/A",
        attendance_dict=attendance_dict,
        total_hours_dict=total_hours_dict
    )

# Account Settings (Change Password)
@admin_bp.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate current password
        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for('admin.account_settings'))

        # Check if new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for('admin.account_settings'))

        # Enforce password strength
        if len(new_password) < 8 or not any(char.isdigit() for char in new_password):
            flash("Password must be at least 8 characters long and contain a number!", "danger")
            return redirect(url_for('admin.account_settings'))

        try:
            # Hash and update password
            current_user.password = generate_password_hash(new_password)
            db.session.commit()

            # Log the password change
            log_entry = Logs(
                admin_id=current_user.user_id,
                action="Updated Account Password",
                details="Password changed successfully."
            )
            db.session.add(log_entry)
            db.session.commit()

            flash("Password updated successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating password: {e}", "danger")

    return render_template('admin/account_settings.html')

# Global Settings
@admin_bp.route('/settings')
@login_required
def settings():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/login.html')

    settings = GlobalSettings.query.first()

    if not settings:
        settings = GlobalSettings()
        db.session.add(settings)
        db.session.commit()  # Save new settings immediately

    if request.method == "POST":
        try:
            # Update boolean settings
            settings.enable_strict_schedule = request.form.get("enable_strict_schedule") == "on"
            settings.early_out_allowed = request.form.get("early_out_allowed") == "on"
            settings.overtime_allowed = request.form.get("overtime_allowed") == "on"

            # Update time-based settings
            default_start_time = request.form.get("default_schedule_start")
            default_end_time = request.form.get("default_schedule_end")
            settings.default_schedule_start = datetime.strptime(default_start_time, "%H:%M").time() if default_start_time else None
            settings.default_schedule_end = datetime.strptime(default_end_time, "%H:%M").time() if default_end_time else None

            # Update early-in allowance (ensure it's an integer)
            allowed_early_in = request.form.get("allowed_early_in")
            settings.allowed_early_in = int(allowed_early_in) if allowed_early_in else 0

            db.session.commit()

            # Log the update
            log_entry = Logs(
                admin_id=current_user.user_id,
                action="Updated Global Settings",
                details=f"Strict Schedule: {settings.enable_strict_schedule}, Early Out: {settings.early_out_allowed}, Overtime: {settings.overtime_allowed}"
            )
            db.session.add(log_entry)
            db.session.commit()

            flash("Settings updated successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error saving settings: {e}", "danger")

        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html")

# AUDIT LOG PAGE
@admin_bp.route('/audit-logs')
@login_required
def audit_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized access!", "danger")
        return render_template('auth/login.html')
    
    today = datetime.now().date()

    return render_template('admin/audit_logs.html', today=today)