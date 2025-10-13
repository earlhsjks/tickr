from flask import (Blueprint, render_template, redirect, url_for, request, flash, 
                   send_file, session, request, jsonify)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
import io
from collections import defaultdict
from datetime import datetime, timedelta
from models.models import db, User, Attendance, Schedule, GlobalSettings, Logs
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, or_
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

# Admin Login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        user = User.query.filter(
            User.user_id == user_id,
            User.role.in_(["superadmin", "admin"])
        ).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid Credentials. Please try again.", "danger")

    return render_template('auth/admin.html')

# Auto Logout
@admin_bp.route('/logout')
def logout():
    logout_user()  # Logs out the user
    session.clear()  # Clears session data
    return render_template('auth/admin.html')  # Redirect to login page

# Dashboard
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')
    
    # Exclude superadmin from statistics
    total_employees = User.query.filter(User.role != "superadmin").count()

    # Today's Date
    today = datetime.now().date()

    # Dashboard Summary
    average_hours_worked = (
        db.session.query(db.func.avg(
            db.func.extract('epoch', Attendance.clock_out - Attendance.clock_in) / 3600
        )).filter(
            Attendance.clock_out.isnot(None)
        ).scalar() or 0
    )

    overtime_hours = (
        db.session.query(db.func.sum(
            db.func.extract('epoch', Attendance.clock_out - Attendance.clock_in) / 3600
        )).filter(
            Attendance.clock_out.isnot(None),
            Attendance.clock_out > Attendance.clock_in + timedelta(hours=4)  # 4 hours overtime threshold
        ).scalar() or 0
    )

    compliance_hours = (
        db.session.query(db.func.sum(
            db.func.extract('epoch', Attendance.clock_out - Attendance.clock_in) / 3600
        )).filter(
            Attendance.clock_out.isnot(None),
            Attendance.clock_out <= Attendance.clock_in + timedelta(hours=4) # 4 hours compliance threshold
        ).scalar() or 0
    )

    return render_template(
        'admin/dashboard.html',
        user=current_user,
        total_employees=total_employees,
        average_hours_worked=average_hours_worked,
        overtime_hours=overtime_hours,
        compliance_hours=compliance_hours,
        current_time = datetime.now().strftime("%A, %B %d, %Y"),
    )

# Attendance 
@admin_bp.route('/attendance-records', methods=['GET', 'POST'])
@login_required
def admin_attendance():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized Access!", "danger")
        return render_template('auth/admin.html')

    # Ensure `month` is properly formatted
    month = request.args.get('month', '').strip()

    if not month or '-' not in month:  # Handle missing or incorrect format
        month = datetime.today().strftime('%Y-%m')  # Default to current month

    try:
        year, month = map(int, month.split('-'))  # Convert to integers
    except ValueError:
        flash("Invalid month format. Please select a valid month.", "danger")
        return redirect(url_for('admin.admin_attendance'))

    # Query attendance records for the selected month
    attendance_records = db.session.query(
        User.first_name,
        User.last_name,
        Attendance.user_id,
        Attendance.clock_in,
        Attendance.clock_out
    ).join(User).filter(
        db.extract('year', Attendance.clock_in) == year,
        db.extract('month', Attendance.clock_in) == month
    ).order_by(Attendance.clock_in.desc()).all()

    # Fetch attendance inconsistencies for the selected month
    inconsistency_records = AttendanceInconsistency.query.filter(
        db.extract('year', AttendanceInconsistency.date) == year,
        db.extract('month', AttendanceInconsistency.date) == month
    ).all()

    # Process inconsistencies into a dictionary (indexed by user_id & date)
    inconsistencies = {}
    for record in inconsistency_records:
        date_str = record.date.strftime('%Y-%m-%d')  # Format properly
        if record.user_id not in inconsistencies:
            inconsistencies[record.user_id] = {}
        if date_str not in inconsistencies[record.user_id]:
            inconsistencies[record.user_id][date_str] = []
        inconsistencies[record.user_id][date_str].append(record.issue_type)

    # Pass the data to the template
    return render_template(
        'admin/attendance_records.html',
        user=current_user,  # Ensure `user` is available in the template
        attendance=attendance_records,
        inconsistencies=inconsistencies,
        current_month=f"{year}-{month:02d}",
        datetime=datetime
    )

# VIEW USERS
@admin_bp.route('/users')
@login_required
def users():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    users = User.query.filter(User.role != "superadmin").all()

    return render_template('admin/users.html',
                           current_user=current_user,
    )

# DAILY LOGS PAGE
@admin_bp.route('/daily-logs', methods=['GET'])
@login_required
def daily_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    # Get the current date
    today = datetime.today().date()

    # Fetch daily logs for today
    daily_logs = db.session.query(
        User.first_name,
        User.last_name,
        Attendance.clock_in,
        Attendance.clock_out
    ).join(User).filter(
        db.func.date(Attendance.clock_in) == today
    ).order_by(Attendance.clock_in.desc()).all()

    return render_template(
        'admin/daily_log.html',
        daily_logs=daily_logs,
        current_date=today.strftime("%Y-%m-%d")
        
    )

# MANUAL LOGS PAGE
@admin_bp.route('/manual-logs', methods=['GET'])
@login_required
def manual_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    # Fetch manual logs
    manual_logs = db.session.query(
        # Logs.admin_id,
        Logs.action,
        Logs.details,
        Logs.timestamp
    ).filter(Logs.action.like('%Manual%')).order_by(Logs.timestamp.desc()).all()

    return render_template('admin/manual_logs.html', manual_logs=manual_logs)

# VIEW SHIFT TEMPLATE
@admin_bp.route('/shift-template')
@login_required
def shift_template():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    # Fetch all shift templates
    shift_templates = db.session.query(
        User.first_name,
        User.last_name,
        Schedule.day,
        Schedule.start_time,
        Schedule.end_time,
        Schedule.is_broken
    ).join(User).filter(Schedule.is_broken == False).all()

    return render_template('admin/shift_template.html', shift_templates=shift_templates)

# VIEW OVERTIME REQUESTS
@admin_bp.route('/overtime-requests')
@login_required
def overtime_requests():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    # Fetch all overtime requests
    overtime_requests = db.session.query(
        User.first_name,
        User.last_name,
        Attendance.clock_in,
        Attendance.clock_out,
        AttendanceInconsistency.issue_type,
        AttendanceInconsistency.date
    ).join(User).filter(AttendanceInconsistency.issue_type == "Overtime").all()

    return render_template('admin/overtime_requests.html', overtime_requests=overtime_requests)

# GIA SCHEDULE MANAGEMENT
@admin_bp.route('/gia-schedule')
@login_required
def gia_schedule():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')
    
    users = User.query.filter(User.role == "gia").all()
    schedules = Schedule.query.all()

    # Create a mapping of user_id to their schedules
    schedule_map = defaultdict(list)
    for schedule in schedules:
        schedule_map[schedule.user_id].append(schedule)

    return render_template('admin/schedule.html', users=users, schedule_map=schedule_map)

# OFFICE MANAGEMENT
@admin_bp.route('/work-assignment')
@login_required
def admin_department():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/work-assignment.html')

    heads = User.query.filter_by(role='head').all()
    offices = Office.query.all()
    return render_template('admin/work-assignment.html', offices=offices, heads=heads)

# ADD NEW OFFICE
@admin_bp.route('/add-office', methods=['POST'])
@login_required
def add_office():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    office_name = request.form.get('name', '').strip()
    campus = request.form.get('campus')
    unit_head_id = request.form.get('head')

    if not office_name or not campus or not unit_head_id:
        flash("All fields are required!", "danger")
        return redirect(url_for('admin.admin_offices'))

    new_office = Office(name=office_name, campus=campus, unit_head_id=unit_head_id)

    try:
        db.session.add(new_office)
        db.session.commit()
        flash("Office added successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Office already exists!", "danger")

    return redirect(url_for('admin.admin_offices'))

# DELETE OFFICE
@admin_bp.route('delete-office/<int:id>', methods=['GET'])
@login_required
def delete_office(id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/offices.html')

    users = db.session.scalars(db.select(User)).all()
    offices = Office.query.all()
    users = User.query.filter(User.role != "superadmin").all()

    return render_template('admin/offices.html', users=users, offices=offices)

# Edit Office (Loads the Edit Page)
@admin_bp.route('/edit-office/<int:id>', methods=['GET'])
@login_required
def edit_office(id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

    office = Office.query.all()
    return render_template('admin/edit_offices.html', office=office)

# Specific User Attendance
@admin_bp.route('/user-logs/<string:user_id>', methods=['GET'])
@login_required
def view_user_logs(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized Access!", "danger")
        return render_template('auth/admin.html')

    month = request.args.get('month')  # Use GET instead of POST to match filter form

    user = User.query.get_or_404(user_id)

    if month:
        try:
            year, month = map(int, month.split('-'))
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('admin.view_user_logs', user_id=user_id))
    else:
        today = datetime.today()
        year, month = today.year, today.month

    # Fetch attendance records for the selected employee and month
    attendance_records = Attendance.query.filter(
        Attendance.user_id == user_id,
        db.extract('year', Attendance.clock_in) == year,
        db.extract('month', Attendance.clock_in) == month
    ).all()

    # Fetch inconsistencies for the selected employee and month
    inconsistency_records = AttendanceInconsistency.query.filter(
        AttendanceInconsistency.user_id == user_id,
        db.extract('year', AttendanceInconsistency.date) == year,
        db.extract('month', AttendanceInconsistency.date) == month
    ).all()

    # Properly map inconsistencies by user_id and date
    inconsistencies = {}
    for record in inconsistency_records:
        date_str = record.date.strftime('%Y-%m-%d')
        if user_id not in inconsistencies:
            inconsistencies[user_id] = {}
        if date_str not in inconsistencies[user_id]:
            inconsistencies[user_id][date_str] = []
        inconsistencies[user_id][date_str].append(record.issue_type)

    return render_template(
        'admin/user_attendance.html',
        user=user,
        attendance=attendance_records or [],
        inconsistencies=inconsistencies,
        user_id=user_id,
        current_month=f"{year}-{month:02d}"  # Ensure correct formatting
    )

# Edit Attendance Logs
@admin_bp.route('/edit-attendance', methods=['POST'])
@login_required
def edit_attendance():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized Access!", "danger")
        return render_template('auth/admin.html')

    record_id = request.form.get('save')  # Get the record ID from the button
    if not record_id:
        flash("Invalid request!", "danger")
        return redirect(request.referrer)

    attendance = Attendance.query.get_or_404(record_id)

    try:
        clock_in = request.form.get(f'clock_in_{record_id}')
        clock_out = request.form.get(f'clock_out_{record_id}')

        # Preserve the existing date
        existing_date = attendance.clock_in.date() if attendance.clock_in else datetime.today().date()

        changes = []  # To store log details

        # Update clock-in with the same date
        if clock_in:
            clock_in_time = datetime.strptime(clock_in, "%H:%M").time()
            new_clock_in = datetime.combine(existing_date, clock_in_time)
            if attendance.clock_in != new_clock_in:
                changes.append(f"Clock-In changed from {attendance.clock_in.strftime('%H:%M')} to {clock_in}")
                attendance.clock_in = new_clock_in

        # Update clock-out with the same date
        if clock_out:
            clock_out_time = datetime.strptime(clock_out, "%H:%M").time()
            new_clock_out = datetime.combine(existing_date, clock_out_time)
            if attendance.clock_out != new_clock_out:
                changes.append(f"Clock-Out changed from {attendance.clock_out.strftime('%H:%M') if attendance.clock_out else 'N/A'} to {clock_out}")
                attendance.clock_out = new_clock_out

        db.session.commit()

        # Log the attendance update
        if changes:
            log_entry = Logs(
                admin_id=current_user.user_id,
                action=f"Edited Attendance Record {record_id}",
                details=" | ".join(changes)
            )
            db.session.add(log_entry)
            db.session.commit()

        flash("Attendance record updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating record: {e}", "danger")

    return redirect(request.referrer)

@admin_bp.route('/add-attendance-entry', methods=['POST'])
@login_required
def add_attendance_entry():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized Access!", "danger")
        return render_template('auth/admin.html')

    user_id = request.form.get('user_id')
    date_str = request.form.get('date')
    clock_in_str = request.form.get('clock_in')
    clock_out_str = request.form.get('clock_out')

    try:
        clock_in = datetime.strptime(f"{date_str} {clock_in_str}", "%Y-%m-%d %H:%M")
        clock_out = datetime.strptime(f"{date_str} {clock_out_str}", "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        flash("Invalid date or time format.", "danger")
        return redirect(url_for('admin.view_user_logs', user_id=user_id))

    # Save the new attendance entry
    new_attendance = Attendance(
        user_id=user_id,
        clock_in=clock_in,
        clock_out=clock_out
    )
    db.session.add(new_attendance)
    db.session.commit()

    flash("New attendance entry added successfully.", "success")
    return redirect(url_for('admin.view_user_logs', user_id=user_id))

@admin_bp.route('/delete-attendance-entry', methods=['POST'])
@login_required
def delete_attendance_entry():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized Access!", "danger")
        return render_template('auth/admin.html')

    record_id = request.form.get('record_id')
    attendance = Attendance.query.get(record_id)
    if not attendance:
        flash("Attendance entry not found.", "danger")
        return redirect(request.referrer or url_for('admin.admin_employees'))

    try:
        db.session.delete(attendance)
        db.session.commit()

        # Log the deletion
        log_entry = Logs(
            admin_id=current_user.user_id,
            action=f"Deleted Attendance Record {record_id}",
            details=f"Deleted attendance entry for employee {attendance.user_id} on {attendance.clock_in.strftime('%Y-%m-%d') if attendance.clock_in else 'N/A'}"
        )
        db.session.add(log_entry)
        db.session.commit()

        flash("Attendance entry deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting attendance entry: {e}", "danger")

    return redirect(request.referrer or url_for('admin.admin_employees'))
  
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
@admin_bp.route('/settings', methods=["GET", "POST"])
@login_required
def settings():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return render_template('auth/admin.html')

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

    return render_template("admin/settings.html", settings=settings)

# Route to View Logs
@admin_bp.route('/logs', methods=['GET', 'POST'])
@login_required
def view_logs():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Unauthorized access!", "danger")
        return render_template('auth/admin.html')

    # Get page and rows_per_page from args or form
    page = int(request.args.get('page', 1))
    if request.method == 'POST':
        rows_per_page = int(request.form.get('rows_per_page', 25))
        log_date = request.form.get('log_date', '')
    else:
        rows_per_page = int(request.args.get('rows_per_page', 25))
        log_date = request.args.get('log_date', '')

    # Join with User model and exclude logs from superadmins
    query = Logs.query.join(User, User.user_id == Logs.admin_id).filter(User.role != 'superadmin').order_by(Logs.timestamp.desc())

    if log_date:
        try:
            selected_date = datetime.strptime(log_date, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Logs.timestamp) == selected_date)
        except ValueError:
            pass

    total_logs = query.count()
    logs = query.offset((page - 1) * rows_per_page).limit(rows_per_page).all()

    return render_template(
        'admin/system_logs.html',
        logs=logs,
        rows_per_page=rows_per_page,
        page=page,
        total_logs=total_logs,
        log_date=log_date
    )

# DTR Print
@admin_bp.route('/export-pdf')
@login_required
def export_pdf():
    if current_user.role not in ["superadmin", "admin"]:
        return render_template('auth/admin.html')

    # Ensure selected_month is valid, otherwise default to current month
    selected_month = request.args.get('month', '').strip() or datetime.today().strftime('%Y-%m')

    if not selected_month or '-' not in selected_month:
        selected_month = datetime.today().strftime('%Y-%m')  # Default to current month

    try:
        year, month = map(int, selected_month.split('-'))  # Convert to integers
    except ValueError:
        flash("Invalid month format. Defaulting to current month.", "warning")
        return redirect(url_for('admin.export_pdf', month=datetime.today().strftime('%Y-%m')))

    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    total_days = last_day.day

    # Exclude "superadmin" and "admin" roles
    users = User.query.filter(User.role.notin_(["superadmin", "admin"])).order_by(User.user_id).all()

    # Fetch attendance records for the selected month
    attendance_records = Attendance.query.filter(
        Attendance.clock_in >= first_day,
        Attendance.clock_in < (last_day + timedelta(days=1))
    ).order_by(Attendance.clock_in).all()

    # Dictionary to store attendance data
    attendance_dict = defaultdict(lambda: defaultdict(lambda: {
        "shift1": {"in": None, "out": None}, 
        "shift2": {"in": None, "out": None}
    }))
        
    # Dictionary to store total hours per user (initialized to 0 seconds)
    total_hours_dict = {user.user_id: 0 for user in users}  

    # Populate attendance records
    for record in attendance_records:
        date_key = record.clock_in.date().strftime('%Y-%m-%d')
        user_id = record.user_id

        clock_in_time = record.clock_in
        clock_out_time = record.clock_out if record.clock_out else None
            
        if not attendance_dict[user_id][date_key]["shift1"]["in"]:
            attendance_dict[user_id][date_key]["shift1"]["in"] = clock_in_time
            attendance_dict[user_id][date_key]["shift1"]["out"] = clock_out_time
        elif attendance_dict[user_id][date_key]["shift1"]["out"] is None:
            # If the first shift has an 'in' but no 'out', update 'out'
            attendance_dict[user_id][date_key]["shift1"]["out"] = clock_out_time
        else:
            attendance_dict[user_id][date_key]["shift2"]["in"] = clock_in_time
            attendance_dict[user_id][date_key]["shift2"]["out"] = clock_out_time
        
    # Calculate total hours per user
    for user in users:
        total_seconds = 0
        if user.user_id in attendance_dict:
            for date, shifts in attendance_dict[user.user_id].items():
                for shift in ["shift1", "shift2"]:
                    if shifts[shift]["in"] and shifts[shift]["out"]:
                        total_seconds += (shifts[shift]["out"] - shifts[shift]["in"]).total_seconds()

        # Convert total seconds to HH:MM format
        total_hours = int(total_seconds // 3600)
        total_minutes = int((total_seconds % 3600) // 60)
        total_hours_dict[user.user_id] = f"{total_hours}:{total_minutes:02d}"

    # Pair users (two per page)
    user_pairs = [users[i:i+2] for i in range(0, len(users), 2)]
    
    return render_template(
        'admin/dtr_report.html',
        now=datetime.now(),
        user_pairs=user_pairs, 
        month=month, 
        year=year, 
        total_days=total_days, 
        datetime=datetime,
        attendance_dict=attendance_dict,
        total_hours_dict=total_hours_dict  # Pass total hours data to template
    )

@admin_bp.route('/export-excel')
@login_required
def export_excel():
    if current_user.role not in ["superadmin", "admin"]:
        return render_template('auth/admin.html')

    records = Attendance.Session.scalars().all()
    data = [{"Employee ID": record.user_id, "Clock In": record.clock_in, "Clock Out": record.clock_out or "N/A"} for record in records]

    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")

    excel_file.seek(0)
    return send_file(excel_file, as_attachment=True, download_name="attendance_report.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
