from flask import (Blueprint, request, flash, 
                   send_file, request, jsonify)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import io, traceback
import pandas as pd
from datetime import datetime, date, timedelta, time
from models.models import db, User, Attendance, Schedule, GlobalSettings, Logs
from routes.gia import WHITELIST
# from flask_apscheduler import APScheduler

# Create a Blueprint for admin routes
api_bp = Blueprint('api', __name__)

# System Log
def systemLogEntry(action, details):
    try:
        entry = Logs(
            action=action,
            details=details,
            user_id=getattr(current_user, 'user_id', None),
            timestamp=datetime.now(),
            client_ip=request.remote_addr

        )
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

# GET ALL USER
@api_bp.route('/users-data', methods=['GET'])
@login_required
def get_data():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    users = User.query.filter(User.role != "superadmin").order_by(User.role, User.first_name).all()
    users_list = []
    for user in users:
        data = user.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data.pop('password', None)
        data.pop('id', None)
        users_list.append(data)
        
    return jsonify(users_list)

# ADD NEW USER
@api_bp.route('/add-user', methods=['POST'])
@login_required
def add_user():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid or missing JSON data'}), 400

    user_id = data.get('userId')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    middle_initial = data.get('middleInitial')
    role = data.get('role')

    # Check if user already exists
    if User.query.get(user_id):
        return jsonify({'success': False, 'error': 'User ID already exists'}), 400

    # Create and save new user
    new_user = User(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_initial.upper(),
        role=role,
        password=generate_password_hash('admin123')
    )
    db.session.add(new_user)
    db.session.commit()

    systemLogEntry(
        action="Created",
        details=f"User '{new_user.first_name} {new_user.last_name}' (ID: {new_user.user_id}) was created by {current_user.first_name} {current_user.last_name}."
    )
    
    return jsonify({
        'success': True,
    }), 200

# GET USER DETAILS
@api_bp.route('/get-user/<string:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'user_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name, 
        'middle_name': user.middle_name[0] if user.middle_name else '',
        'role_id': user.role,
        'status': user.status,
    }

    return jsonify(user_data)

# UPDATE USER DETAILS
@api_bp.route('/update-user/<string:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid or missing JSON data'}), 400

    # Update user fields
    user.user_id = data.get('userId', user.user_id)
    user.first_name = data.get('firstName', user.first_name)
    user.last_name = data.get('lastName', user.last_name)
    user.middle_name = data.get('middleInitial', user.middle_name).upper()
    user.role = data.get('role', user.role)
    user.status = data.get('status', user.status)
    user.role = data.get('role', user.role)

    try:
        db.session.commit()

        systemLogEntry(
            action="Updated",
            details=f"#{user.id} User '{user.first_name} {user.last_name}' (ID: {user.user_id}) was updated by {current_user.first_name} {current_user.last_name}."
        )

        return jsonify({'success': True, 'message': 'User updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Error updating user: {str(e)}"}), 500

# DELETE USER
@api_bp.route('/delete-user/<string:user_id>', methods=['POST'])
@login_required
def delete_user_page(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    try:
        # Delete related attendance records
        Attendance.query.filter_by(user_id=user.user_id).delete()

        systemLogEntry(
            action="Deleted",
            details=f"User '{user.first_name} {user.last_name}' (ID: {user.user_id}) was deleted by {current_user.first_name} {current_user.last_name}."
        )

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'User deleted successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Error deleting user: {str(e)}"}), 500

# EXPORT USERS
@api_bp.route('/export-users', methods=['GET'])
@login_required
def export_users():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400

    # Fetch and sort users
    users = sorted(
        User.query.filter(User.role == "gia").all(),
        key=lambda x: (x.last_name, x.first_name)
    )

    # Prepare user data
    data = {
        'User ID': [user.user_id for user in users],
        'Last Name': [user.last_name for user in users],
        'First Name': [user.first_name for user in users],
        'Middle Initial': [user.middle_name[0].upper() if user.middle_name else '' for user in users],
    }

    df = pd.DataFrame(data)

    # Convert to CSV
    csv_data = df.to_csv(index=False)
    output = io.BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)

    # Filename with timestamp
    filename = f'GIA List {datetime.now().strftime("%m-%d-%Y")}.csv'

    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)

# Time to String
def serialize_schedule(s):
    return {
        'user_id': s.user_id,
        'day': s.day,
        'start_time': s.start_time.strftime("%I:%M %p") if s.start_time else '',
        'end_time': s.end_time.strftime("%I:%M %p") if s.end_time else '',
        'split_start_time': s.split_start_time.strftime("%I:%M %p") if s.split_start_time else '',
        'split_end_time': s.split_end_time.strftime("%I:%M %p") if s.split_end_time else ''
    }

# GET ALL SCHEDULE
@api_bp.route('/get-schedules', methods=['GET'])
@login_required
def get_schedules():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    users = User.query.filter(User.role != "superadmin", User.role != "admin").order_by(User.first_name)
    schedules = Schedule.query.all()
    users_list = []
    sched_list = [serialize_schedule(s) for s in schedules]

    for user in users:
        data = user.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data.pop('password', None)
        data.pop('role', None)
        data.pop('status', None)
        data.pop('id', None)
        users_list.append(data)

    return jsonify({
        'schedules': sched_list,
        'users': users_list
    })

@api_bp.route('/get-schedule/<string:user_id>', methods=['GET'])
@login_required
def get_user_schedule(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    schedule = Schedule.query.filter_by(user_id=user_id).all()

    user_data = {
        'user_id': user.user_id,
        'full_name': f"{user.first_name} {user.last_name}",
    }

    user_schedules = [
        {
            'id': s.id,
            'day': s.day,
            'start_time': s.start_time.strftime('%H:%M') if s.start_time else None,
            'end_time': s.end_time.strftime('%H:%M') if s.end_time else None,
            'is_split_shift': s.is_split_shift,
            'split_start_time': s.split_start_time.strftime('%H:%M') if s.split_start_time else None,
            'split_end_time': s.split_end_time.strftime('%H:%M') if s.split_end_time else None,
        }
        for s in schedule
    ]

    return jsonify({
        'user': user_data,
        'schedules': user_schedules
    })


def parse_time(value):
    """Convert 'HH:MM' string to Python time object or None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None

# UPDATE SCHEDULE
@api_bp.route('/update-schedule/<string:user_id>', methods=['POST'])
@login_required
def update_schedule(user_id):
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid or missing JSON data'}), 400

    schedules = data.get('schedules', [])
    brokenScheds = data.get('brokenSched', [])

    try:
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            match = next((s for s in schedules if s.get('day') == day), None)
            brokenMatch = next((b for b in brokenScheds if b.get('day') == day), None)

            # Parse times safely (may be None)
            start_time = parse_time(match.get('start_time')) if match else None
            end_time = parse_time(match.get('end_time')) if match else None
            split_start_time = parse_time(brokenMatch.get('split_start_time')) if brokenMatch else None
            split_end_time = parse_time(brokenMatch.get('split_end_time')) if brokenMatch else None

            # Determine split flag
            isBroken = bool(split_start_time and split_end_time)

            sched = Schedule.query.filter_by(user_id=user_id, day=day).first()

            if sched:
                # Update existing record
                sched.start_time = start_time
                sched.end_time = end_time
                sched.split_start_time = split_start_time
                sched.split_end_time = split_end_time
                sched.is_split_shift = isBroken
            elif match or brokenMatch:
                # Only create new if there’s relevant data
                new_sched = Schedule(
                    user_id=user_id,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    split_start_time=split_start_time,
                    split_end_time=split_end_time,
                    is_split_shift=isBroken
                )
                db.session.add(new_sched)

        db.session.commit()

        systemLogEntry(
            action="Updated",
            details=f"Schedule for user '{user.first_name} {user.last_name}' (ID: {user.user_id}) was updated by {current_user.first_name} {current_user.last_name}."
        )

        return jsonify({'success': True, 'message': 'Schedule updated successfully!'})

    except Exception as e:
        db.session.rollback()
        print("Error updating schedule:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/purge-schedules', methods=['POST'])
@login_required
def purge_schedules():
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    try:
        db.session.query(Schedule).delete()
        db.session.commit()

        systemLogEntry(
            action="Deleted",
            details=f"All schedules were purged by {current_user.first_name} {current_user.last_name}."
        )

        return jsonify({'success': True, 'message': 'All schedules cleared successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Error clearing schedules: {str(e)}"}), 500

def serialize_logs(l):
    role = None
    if (l.user.role == "admin"):
        role = "Admin"
    else:
        role = 'GIA'

    return {
        'date': l.timestamp.strftime("%b %d, %Y"),
        'time': l.timestamp.strftime("%I:%M %p"),
        'full_name': f"{l.user.first_name} {l.user.last_name}",
        'role': role,
        'action': l.action, 
        'details': l.details,
        'ip': l.client_ip
    }

@api_bp.route('/get-logs')
@login_required
def get_logs():
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403

    from_date = request.args.get("from")
    to_date = request.args.get("to")
    page = request.args.get("page", 1, type=int)       # current page
    per_page = request.args.get("per_page", 20, type=int)  # items per page

    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

    pagination = Logs.query.filter(
        Logs.user_id != 'superadmin',
        Logs.timestamp >= from_date_obj,
        Logs.timestamp <= to_date_obj
    ).order_by(Logs.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    logs_list = [serialize_logs(l) for l in pagination.items]

    return jsonify({
        "logs": logs_list,
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page
    })

def serialize_drecords(s):
    if s.clock_in and s.clock_out:
        clock_in_dt = datetime.combine(date.today(), s.clock_in)
        clock_out_dt = datetime.combine(date.today(), s.clock_out)
        time_difference = clock_out_dt - clock_in_dt
        t_hours = round(time_difference.total_seconds() / 3600, 2)
    else:
        t_hours = 0

    return {
        'name_initial': f"{s.user.first_name[0]}{s.user.last_name[0]}",
        'full_name': f"{s.user.first_name} {s.user.last_name}",
        'user_id': s.user.user_id,
        'log_id': s.id,
        'date': s.date.strftime("%Y-%m-%d"),
        'clock_in': s.clock_in.strftime("%I:%M %p").lower() if s.clock_in else '',
        'clock_out': s.clock_out.strftime("%I:%M %p").lower() if s.clock_out else '',
        'total_hours': t_hours,
    }

@api_bp.route('/get-daily-logs')
@login_required
def get_daily_logs():
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    today = request.args.get('today')

    records = Attendance.query.filter(Attendance.date == today).order_by(Attendance.id.desc()).all()
    records_list = [serialize_drecords(s) for s in records]

    return jsonify(records_list)

@api_bp.route('/get-user-log/<string:log_id>')
@login_required
def get_user_log(log_id):
    
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    record = Attendance.query.get(log_id)
    user_record = {
        'log_id': record.id,
        'full_name': f"{record.user.first_name} {record.user.last_name}",
        'clock_in': record.clock_in.strftime("%H:%M") if record.clock_in else '',
        'clock_out': record.clock_out.strftime("%H:%M") if record.clock_out else '',
        # 'notes': record.notes if record.notes else '',
    }

    return jsonify(user_record)

@api_bp.route('/update-log/<string:log_id>', methods=['POST'])
@login_required
def update_log(log_id):
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    data = request.get_json()
    log = Attendance.query.get(log_id)
    
    log.clock_in = data.get('clockIn', log.clock_in)
    log.clock_out = data.get('clockOut', log.clock_out)

    try:
        db.session.commit()

        systemLogEntry(
            action="Updated",
            details=f"#{log.id} Attendance record updated for {log.user.first_name} {log.user.last_name}."
        )

        return jsonify({'success': True, 'message': 'Log updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Error updating log: {str(e)}"}), 500

@api_bp.route('/add-log', methods=['POST'])
def add_log():
    if current_user.role not in ["superadmin", "admin"]:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    data = request.get_json()

    user_id = data.get('userId')
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    new_log = Attendance(
        user_id = user_id,
        date = data.get('date'),
        clock_in = data.get('clockIn'),
        clock_out = data.get('clockOut'),
        is_manual = True 
    )

    try:
        db.session.add(new_log)

        systemLogEntry(
            action="Created",
            details=f"New attendance record added for {user.first_name} {user.last_name}."
        )

        return jsonify({'success': True, 'message': 'Log updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Error updating log: {str(e)}"}), 500

##### GIA API #####

@api_bp.route('/status', methods=['GET'])
@login_required
def status():
    user_id = request.args.get('user_id')

    if current_user.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    today = date.today()

    # Get latest attendance for today
    last_record = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.date == today
    ).order_by(Attendance.id.desc()).first()

    # Get today's schedule(s)
    user_schedules = Schedule.query.filter_by(
        user_id=user_id,
        day=datetime.today().strftime('%A').lower()
    ).all()

    # Check global settings for strict schedule enforcement
    global_settings = GlobalSettings.query.first()
    strict_schedule = bool(global_settings and global_settings.enable_strict_schedule)

    schedule_end = None
    is_30_mins = False

    # No record = not clocked in yet
    if not last_record or not last_record.clock_in:
        return jsonify({
            'clocked_in': False,
            'clocked_out': False,
            'is30min': False
        }), 200

    clock_in_time = last_record.clock_in

    # Determine applicable schedule
    for sched in user_schedules:
        # Check first shift
        if sched.start_time and sched.end_time:
            early_start = (datetime.combine(today, sched.start_time) - timedelta(hours=1)).time()
            if early_start <= clock_in_time <= sched.end_time:
                schedule_end = sched.end_time
                break

        # Check second shift (split schedule)
        if sched.is_split_shift and sched.split_start_time and sched.split_end_time:
            early_second_start = (datetime.combine(today, sched.split_start_time) - timedelta(hours=1)).time()
            if early_second_start <= clock_in_time <= sched.split_end_time:
                schedule_end = sched.split_end_time
                break

    # Check if user exceeded 30-min grace period
    if strict_schedule and schedule_end:
        now = datetime.now()
        grace_limit = datetime.combine(today, schedule_end) + timedelta(minutes=60)
        if now > grace_limit:
            is_grace = True

    # Response
    return jsonify({
        'clocked_in': bool(last_record.clock_in and not last_record.clock_out),
        'clocked_out': bool(last_record.clock_out),
        'is_grace': is_grace
    }), 200

def serialize_records(s):
    if s.clock_in and s.clock_out:
        clock_in_dt = datetime.combine(date.today(), s.clock_in)
        clock_out_dt = datetime.combine(date.today(), s.clock_out)
        time_difference = clock_out_dt - clock_in_dt
        t_hours = round(time_difference.total_seconds() / 3600, 2)
    else:
        t_hours = 0

    return {
        'date': s.date.strftime("%b %d, %Y"),
        'clock_in': s.clock_in.strftime("%I:%M %p").lower() if s.clock_in else '',
        'clock_out': s.clock_out.strftime("%I:%M %p").lower() if s.clock_out else '',
        'total_hours': t_hours,
    }

@api_bp.route('/gia-data', methods=['GET'])
@login_required
def gia_data():
    user_id = request.args.get('user_id')

    if current_user.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    month = request.args.get('month')
    year, month = map(int, month.split('-'))

    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        db.extract('year', Attendance.date) == year,
        db.extract('month', Attendance.date) == month,
    ).order_by(Attendance.date.desc(), Attendance.id.desc()).all()
    user_records = [serialize_records(r) for r in records]

    t_hours = 0.0
    sum_hours = 0.0
    for record in records:
        if record.clock_in and record.clock_out:
            clock_in_dt = datetime.combine(date.today(), record.clock_in)
            clock_out_dt = datetime.combine(date.today(), record.clock_out)
            time_difference = clock_out_dt - clock_in_dt
            t_hours = round(time_difference.total_seconds() / 3600, 2)
        else:
            t_hours = 0
    
        sum_hours += t_hours

    summary = {
        'total_hours': round(sum_hours, 2),
        'total_on_time': 0,
        'total_late': 0,
        'total_absences': 0
    }

    return jsonify({
        'records': user_records,
        'summary': summary
    })

# Whitelist verification
def ip_whitelist():
    if not current_user.is_authenticated or current_user.user_id != "2024998":
        client_ip = request.remote_addr
        if client_ip not in WHITELIST:
            return({'success': False, 'error': 'Access denied. Your device isn’t allowed to use this feature.'}), 400

@api_bp.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    user_id = request.get_json()

    if current_user.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    ip_whitelist()
    
    try:
        today_name = datetime.today().strftime('%A').lower()
        now = datetime.now().time()

        # Get Schedules and Global Settings 
        user_schedules = Schedule.query.filter_by(user_id=user_id, day=today_name).all()
        global_settings = GlobalSettings.query.first()

        # Apply default schedule if no personal one exists
        if not user_schedules and global_settings and global_settings.default_start and global_settings.default_end:
            user_schedules = [Schedule(
                user_id=user_id,
                day=today_name,
                start_time=global_settings.default_start,
                end_time=global_settings.default_end
            )]

        if not user_schedules:
            return jsonify({'success': False, 'error': 'You don’t have a schedule for today.'}), 400

        # Early-in Rules 
        allowed_early_in = global_settings.allowed_early_in_mins if global_settings else 0
        special_early_in = allowed_early_in

        # Add special 30min early-in for 7:30 AM weekday shifts
        if today_name in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if any(s.start_time == time(7, 30) for s in user_schedules):
                special_early_in += 30

        # Determine Valid Schedule 
        valid_schedule = None
        is_split_shift = False

        for sched in user_schedules:
            if sched.start_time and sched.end_time:
                earliest_in = (datetime.combine(datetime.today(), sched.start_time) - timedelta(minutes=special_early_in)).time()
                if earliest_in <= now <= sched.end_time:
                    valid_schedule = sched.start_time
                    break

            if getattr(sched, 'is_split_shift', False) and sched.split_start_time and sched.split_end_time:
                earliest_second_in = (datetime.combine(datetime.today(), sched.split_start_time) - timedelta(minutes=allowed_early_in)).time()
                if earliest_second_in <= now <= sched.split_end_time:
                    valid_schedule = sched.split_start_time
                    is_split_shift = True
                    break

        # Enforce strict schedule
        if global_settings and global_settings.enable_strict_schedule and not valid_schedule:
            return jsonify({'success': False, 'error': 'Clock-in blocked. You\'re outside your allowed schedule window.'}), 400

        # Check Attendance Rules 
        today = datetime.today().date()

        active_shifts = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.clock_in.is_not(None),
            Attendance.date == today,
        ).all()

        # Limit to 2 clock-ins per day
        if len(active_shifts) >= 2:
            return jsonify({'success': False, 'error': 'You’ve already reached the daily limit of two clock-ins.'}), 400

        # Prevent duplicate clock-in for same shift (not used, js covered)
        # for shift in active_shifts:
        #     if valid_schedule:
        #         if not is_split_shift and valid_schedule.start_time <= shift.clock_in <= valid_schedule.end_time:
        #             return jsonify({'success': False, 'error': 'Already clocked in for this shift. Clock out first.'}), 400
        #         if is_split_shift and shift.clock_in >= valid_schedule.split_start_time:
        #             return jsonify({'success': False, 'error': 'Already clocked in for your second shift.'}), 400

        #  Create and Save Attendance Entry 
        new_entry = Attendance(
            user_id=user_id,
            date=datetime.now(),
            clock_in=datetime.now().time()
        )
        db.session.add(new_entry)
        db.session.commit()

        systemLogEntry(
            action="Clock In",
            details=f"User {current_user.first_name} {current_user.last_name} clocked in."
        )

        return jsonify({
            'success': True,
            'message': 'Clock-in successful!',
            'data': {
                'user_id': user_id,
                'time_record': new_entry.clock_in.strftime("%I:%M %p"),
                'date': new_entry.date.strftime("%Y-%m-%d"),
                'shift': 'second' if is_split_shift else 'first'
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Clock-in failed: {str(e)}', 'trace': traceback.format_exc()}), 500
    
@api_bp.route('/clock-out', methods=['POST'])
@login_required
def clock_out():
    user_id = request.get_json()

    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user_id'}), 400
    if current_user.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    ip_whitelist()

    try:
        now = datetime.now()
        actual_clock_out = now.time()
        today = now.date()

        last_record = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.clock_in.isnot(None),
            Attendance.clock_out.is_(None),
            Attendance.date == today,
        ).order_by(Attendance.clock_in.desc()).first()
        print(last_record)

        if not last_record:
            return jsonify({'success': False, 'error': 'You can’t clock out without clocking in first today.'}), 400
        
        clock_in_time = last_record.clock_in 

        global_settings = GlobalSettings.query.first()
        strict_schedule = bool(global_settings and global_settings.enable_strict_schedule)
        user_schedules = Schedule.query.filter_by(
            user_id=user_id,
            day=datetime.today().strftime('%A').lower()
        ).all()

        schedule_end = None
        is_split_shift = False

        if strict_schedule and user_schedules:
            # Determine applicable schedule
            for sched in user_schedules:
                if sched.start_time and sched.end_time:
                    early_start = (datetime.combine(today, sched.start_time) - timedelta(hours=1)).time()
                    if early_start <= clock_in_time <= sched.end_time:
                        schedule_end = sched.end_time
                    break

                if getattr(sched, 'is_split_shift', False) and sched.split_start_time and sched.split_end_time:
                    early_second_start = (datetime.combine(today, sched.split_start_time) - timedelta(hours=1)).time()
                    if early_second_start <= clock_in_time <= sched.split_end_time:
                        schedule_end = sched.split_end_time
                        is_split_shift = True
                        break

            # Strict schedule enforcement
            if schedule_end:
                actual_clock_out_dt = datetime.combine(today, actual_clock_out)
                schedule_end_dt = datetime.combine(today, schedule_end)
                
                grace_limit = schedule_end_dt + timedelta(minutes=60)
                
                if actual_clock_out_dt > grace_limit:
                    return jsonify({
                        'success': False,
                        'error': 'Exceeded the 60-minute grace period after your shift.'
                    }), 400

                evening_cutoff = datetime.combine(today, time(18, 30))

                if schedule_end_dt < actual_clock_out_dt < evening_cutoff:
                    last_record.clock_out = schedule_end
                else:
                    last_record.clock_out = actual_clock_out
            else:
                last_record.clock_out = actual_clock_out

        else:
            last_record.clock_out = actual_clock_out

        db.session.commit()

        systemLogEntry(
            action="Clock Out",
            details=f"User {current_user.first_name} {current_user.last_name} clocked out."
        )

        return jsonify({
            'success': True,
            'message': 'Clock-out successful!',
            'data': {
                'user_id': user_id,
                'time_record': last_record.clock_out.strftime("%I:%M %p"),
                'date': last_record.date.strftime("%Y-%m-%d"),
                'shift': 'second' if is_split_shift else 'first'
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Clock-out failed: {str(e)}'
        }), 500