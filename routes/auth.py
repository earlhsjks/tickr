from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required ,current_user
from werkzeug.security import check_password_hash
from models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/whoami')
def whoami():
    if current_user.is_authenticated:
        return jsonify({
            'loggedIn': True,
            'userId': current_user.user_id,
            'role': current_user.role,
            'name': f"{current_user.first_name}"
        })
    else:
        return jsonify({'loggedIn': False})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()

    gia_id = data.get('giaId')
    admin_id = data.get('adminId')
    password = data.get('password')
    
    if gia_id:
        gia = User.query.filter_by(user_id=gia_id).first()

        if not gia:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        login_user(gia)
        return jsonify({'success': True, 'message': f'Welcome {gia.first_name}!'}), 200

    if admin_id:
        admin = User.query.filter_by(user_id=admin_id).first()

        if not admin:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        if not check_password_hash(admin.password, password):
            return jsonify({'success': False, 'error': 'Incorrect password'}), 401

        login_user(admin)
        return jsonify({'success': True, 'message': f'Welcome {admin.first_name}!'}), 200

@auth_bp.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()

    return render_template('/auth/login.html')
