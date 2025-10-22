from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, current_user
from datetime import datetime, timedelta, time
from models.models import db, User, Attendance, Schedule, GlobalSettings

gia_bp = Blueprint('main', __name__)

@gia_bp.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

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

# Employee Dashboard
@gia_bp.route('/dashboard')
@login_required
def dashboard_gia():
    if current_user.role != 'gia':
        return redirect(url_for('admin.dashboard'))
    
    month = datetime.today().strftime("%Y-%m")
    
    return render_template('/gia/dashboard.html', user=current_user, month=month)

# Clock-In/Clock-Out Routes
@gia_bp.route('/clock-in')
@login_required
def clock_in():
    today = datetime.today().strftime('%A')
    now = datetime.now().time()

    # Get user's schedule for today (normal & broken)
    user_schedules = Schedule.query.filter_by(user_id=current_user.user_id, day=today).all()
    global_settings = GlobalSettings.query.first()

    # Apply global schedule if no personal schedule is found
    if not user_schedules and global_settings and global_settings.default_schedule_start and global_settings.default_schedule_end:
        user_schedules = [Schedule(
            user_id=current_user.user_id,
            day=today,
            start_time=global_settings.default_schedule_start,
            end_time=global_settings.default_schedule_end
        )]

    if not user_schedules:
        flash("No schedule set for today.", "danger")
        return redirect(url_for('main.dashboard_employee'))

    # Standard allowed early-in time
    allowed_early_in = global_settings.allowed_early_in if global_settings else 0

    # Apply special early-in rule (Weekdays @ 7:30 AM → Extra 30 mins)
    special_early_in = allowed_early_in  # Default: Normal early-in
    if today in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        for schedule in user_schedules:
            if schedule.start_time == time(7, 30):  # Check if schedule is 7:30 AM
                special_early_in += 30  # Add 30 minutes (Total: Early-in + 30 min)

    # Detect if user has a second shift
    has_second_shift = any(sched.is_broken and sched.second_start_time and sched.second_end_time for sched in user_schedules)

    # Validate clock-in time
    valid_schedule = None
    is_second_shift = False

    for schedule in user_schedules:
        earliest_clock_in_time = (datetime.combine(datetime.today(), schedule.start_time) - timedelta(minutes=special_early_in)).time()

        if earliest_clock_in_time <= now <= schedule.end_time:
            valid_schedule = schedule
            break

        if schedule.is_broken and schedule.second_start_time and schedule.second_end_time:
            earliest_second_clock_in_time = (datetime.combine(datetime.today(), schedule.second_start_time) - timedelta(minutes=allowed_early_in)).time()
            if earliest_second_clock_in_time <= now <= schedule.second_end_time:
                valid_schedule = schedule
                is_second_shift = True
                break

    # Get today's clock-ins
    total_clock_ins_today = Attendance.query.filter(
        Attendance.user_id == current_user.user_id,
        Attendance.clock_in >= datetime.combine(datetime.today(), datetime.min.time())
    ).count()

    active_shifts = Attendance.query.filter(
        Attendance.user_id == current_user.user_id,
        Attendance.clock_in >= datetime.combine(datetime.today(), datetime.min.time()),
        Attendance.clock_out == None
    ).all()

    # Max clock-in rule for strict schedule
    if len(active_shifts) >= 2:
        flash("Maximum of two clock-ins allowed per day!", "danger")
        return redirect(url_for('main.dashboard_employee'))
    
    # Prevent duplicate clock-in for the same shift
    for shift in active_shifts:
        if valid_schedule:
            if not is_second_shift and valid_schedule.start_time <= shift.clock_in.time() <= valid_schedule.end_time:
                flash("You are already on duty for this shift! Please clock out before clocking in again.", "warning")
                return redirect(url_for('main.dashboard_employee'))

            if is_second_shift and shift.clock_in.time() >= valid_schedule.second_start_time and shift.clock_out is None:
                flash("You already clocked in for your second shift! Please clock out before clocking in again.", "warning")
                return redirect(url_for('main.dashboard_employee'))

    # Enforce strict schedule
    if global_settings and global_settings.enable_strict_schedule and not valid_schedule:
        flash("You can only clock in during your scheduled shift!", "warning")
        return redirect(url_for('main.dashboard_employee'))

    # Create a new attendance record
    new_entry = Attendance(user_id=current_user.user_id, clock_in=datetime.now())
    check_attendance_flags(new_entry)
    db.session.add(new_entry)
    db.session.commit()
    
    return redirect(url_for('main.dashboard_employee', clocked_in=1))
    
@gia_bp.route('/clock-out')
@login_required
def clock_out():
    today = datetime.today()
    now = datetime.now()

    # Get the latest clock-in record for today
    last_record = Attendance.query.filter(
        Attendance.user_id == current_user.user_id,
        Attendance.clock_in != None,
        Attendance.clock_in >= datetime.combine(today, datetime.min.time()),  # Only today's records
        Attendance.clock_out == None  # Ensure they haven’t clocked out yet
    ).order_by(Attendance.id.desc()).first()  # Get the latest clock-in

    if not last_record:
        flash("No active clock-in found for today!", "danger")
        return redirect(url_for('main.dashboard_employee'))

    # Fetch global settings
    global_settings = GlobalSettings.query.first()
    strict_schedule = global_settings.enable_strict_schedule if global_settings else False

    # Get ALL schedules for today (including second shift)
    today_day = today.strftime("%A")
    user_schedules = Schedule.query.filter_by(user_id=current_user.user_id, day=today_day).all()

    # Default clock-out time: Now
    actual_clock_out = now

    if strict_schedule and user_schedules:
        # Detect if this is a second shift
        is_second_shift = False
        schedule_end = None

        for schedule in user_schedules:
            # Allow clock-in up to 1 hour before scheduled start
            earliest_clock_in = (datetime.combine(today, schedule.start_time) - timedelta(hours=1)).time()
            latest_clock_in = schedule.end_time

            if earliest_clock_in <= last_record.clock_in.time() <= latest_clock_in:
                schedule_end = datetime.combine(today, schedule.end_time)
                break  # First shift matched

            # Check second shift (broken schedule)
            if schedule.is_broken and schedule.second_start_time and schedule.second_end_time:
                earliest_second_in = (datetime.combine(today, schedule.second_start_time) - timedelta(hours=1)).time()
                if earliest_second_in <= last_record.clock_in.time() <= schedule.second_end_time:
                    schedule_end = datetime.combine(today, schedule.second_end_time)
                    is_second_shift = True
                    break  # Second shift matched

        if schedule_end:
            time_limit = schedule_end + timedelta(minutes=30)  # 30-minute grace period

            # Block clock-out if more than 30 minutes past scheduled end time
            if actual_clock_out > time_limit:
                flash("Clock-out denied! More than 30 minutes past your scheduled end time.", "danger")
                return redirect(url_for('main.dashboard_employee'))

            # If between schedule end and 7:30 PM, force clock-out to schedule end
            nightTime = datetime.combine(today, time(18, 30))  # 7:30 PM cutoff
            if schedule_end < actual_clock_out < nightTime:
                last_record.clock_out = schedule_end
            else:
                last_record.clock_out = actual_clock_out  # Normal clock-out

        else:
            # No schedule found → Allow normal clock-out
            last_record.clock_out = actual_clock_out

    else:
        # No strict schedule → Allow clock-out anytime
        last_record.clock_out = actual_clock_out

    db.session.commit()

    # Check attendance flags (Overtime, etc.)
    check_attendance_flags(last_record)

    # Redirect with `clocked_out=1` parameter
    return redirect(url_for('main.dashboard_employee', clocked_out=1))