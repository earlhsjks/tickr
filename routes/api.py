from flask import (Blueprint, render_template, redirect, url_for, request, flash, 
                   send_file, session, request, jsonify)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
import pandas as pd
import io
from collections import defaultdict
from datetime import datetime, timedelta
from models.models import db, User, Attendance, Schedule, GlobalSettings, Logs
# from flask_apscheduler import APScheduler

# Create a Blueprint for admin routes
api_bp = Blueprint('api', __name__)

# System Log
def systemLogEntry(userId, action, details=None):
    entry = Logs(
        userId = userId,
        action = action,
        details = details,
        timestamp = datetime.now()
    )

    db.session.add(entry)
    db.session.commit()

# GET ALL USER
@api_bp.route('/users-data', methods=['GET'])
@login_required
def get_data():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    users = User.query.filter(User.role != "superadmin").all()
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
        middle_name=middle_initial,
        role=role,
        password=generate_password_hash('admin123')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'success': True,
    }), 200

# GET USER DETAILS
@api_bp.route('/get-user/<string:user_id>')
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
    user.first_name = data.get('firstName', user.first_name)
    user.last_name = data.get('lastName', user.last_name)
    user.middle_name = data.get('middleInitial', user.middle_name)
    user.role = data.get('role', user.role)
    user.status = data.get('status', user.status)
    user.role = data.get('role', user.role)

    try:
        db.session.commit()
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

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        systemLogEntry()

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
        'start_time': s.start_time.strftime("%H:%M") if s.start_time else '',
        'end_time': s.end_time.strftime("%H:%M") if s.end_time else '',
        'split_start_time': s.split_start_time.strftime("%H:%M") if s.split_start_time else '',
        'split_end_time': s.split_end_time.strftime("%H:%M") if s.split_end_time else ''
    }

# GET ALL SCHEDULE
@api_bp.route('/get-schedules')
def get_schedules():
    if current_user.role not in ["superadmin", "admin"]:
        flash("Access Denied!", "danger")
        return jsonify({'success': False, 'error': 'Access Denied'}), 400
    
    users = User.query.filter(User.role != "superadmin", User.role != "admin")
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

@api_bp.route('/get-schedule/<string:user_id>')
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
        return jsonify({'success': True, 'message': 'Schedule updated successfully!'})

    except Exception as e:
        db.session.rollback()
        print("Error updating schedule:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
