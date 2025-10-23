from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.models import db, Schedule, GlobalSettings

gia_bp = Blueprint('gia', __name__)

def check_attendance_flags(attendance_entry):
    """
    Checks and updates attendance flags based on clock-in and clock-out times.
    Handles late arrivals, early departures, and overtime detection.
    Excludes weekends (Saturday and Sunday).
    """

    settings = GlobalSettings.query.first()  # Assuming only one settings row exists
    strict_mode = settings.enable_strict_schedule if settings else False

    if not strict_mode:
        return

    if not attendance_entry or not attendance_entry.clock_in:
        return

    today = attendance_entry.clock_in.date()

    if today.weekday() in [5, 6]:
        return

    allowed_late_minutes = 0

    user_schedule = Schedule.query.filter_by(user_id=attendance_entry.user_id, day=today.strftime('%A')).first()

    if not user_schedule:
        return

    schedule_start = datetime.combine(today, user_schedule.start_time)
    schedule_end = datetime.combine(today, user_schedule.end_time)

    # LATE: Clock-in is after scheduled start + grace period
    if attendance_entry.clock_in > schedule_start + timedelta(minutes=allowed_late_minutes):
        db.session.add(AttendanceInconsistency(
            user_id=attendance_entry.user_id,
            date=today,
            issue_type="Late",
            details=f"Clock-in at {attendance_entry.clock_in.strftime('%I:%M %p')}, scheduled start {schedule_start.strftime('%I:%M %p')}"
        ))

    # EARLY OUT: Clock-out before scheduled end
    if attendance_entry.clock_out and attendance_entry.clock_out < schedule_end:
        db.session.add(AttendanceInconsistency(
            user_id=attendance_entry.user_id,
            date=today,
            issue_type="Early Out",
            details=f"Clock-out at {attendance_entry.clock_out.strftime('%I:%M %p')}, scheduled end {schedule_end.strftime('%I:%M %p')}"
        ))

    # OVERTIME: Work exceeds scheduled shift + buffer (default 4 hours)
    if attendance_entry.clock_out:
        work_duration = attendance_entry.clock_out - attendance_entry.clock_in
        scheduled_duration = schedule_end - schedule_start
        overtime_threshold = timedelta(hours=4)

        if work_duration > scheduled_duration + overtime_threshold:
            db.session.add(AttendanceInconsistency(
                user_id=attendance_entry.user_id,
                date=today,
                issue_type="Overtime",
                details=f"Worked {work_duration}, scheduled {scheduled_duration}"
            ))

    db.session.commit()

WHITELIST = {
    "0.0.0.0", # Local Host
    "172.16.254.250", # GIA Station
    "172.16.255.235", # Office Router
    "172.16.255.236", # Printing 1
    "172.16.255.237", # Printin 2
    "172.16.255.83", # 3013 STN 23
}

# Decorator to apply to specific routes
def ip_whitelist():
    def wrapper(fn):
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            if client_ip not in WHITELIST:
                abort(403)  # Forbidden
            return fn(*args, **kwargs)
        decorated.__name__ = fn.__name__  # Avoid Flask route errors
        return decorated
    return wrapper

# Employee Dashboard
@gia_bp.route('/dashboard')
@ip_whitelist()
@login_required
def dashboard():
    if current_user.role != 'gia':
        return redirect(url_for('admin.dashboard'))
    
    month = datetime.today().strftime("%Y-%m")
    
    return render_template('/gia/dashboard.html', user=current_user, month=month)