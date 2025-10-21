from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required ,current_user
from werkzeug.security import check_password_hash
from models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role not in ['superadmin', 'admin']:
            return render_template('/gia/dashboard.html')
        else:
            return render_template('/admin/dashboard.html')

    return render_template('/auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()

    gia_id = data.get('giaId')
    admin_id = data.get('adminId')
    password = data.get('password')

    gia = User.query.filter_by(user_id=gia_id).first()
    isGia = User.query.filter_by(user_id=gia_id, role='gia').first() is not None
    
    if gia_id and isGia:
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
    
    return jsonify({'success': False, 'error': 'Incorrect username or password'}), 401

@auth_bp.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()

    return render_template('/auth/login.html')
