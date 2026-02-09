from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Zone, User, FlightRequest
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

# 1. صفحة الداشبورد
@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'controller':
        flash('Restricted Area!', 'danger')
        return redirect(url_for('pilot.dashboard'))
    return render_template('admin/dashboard.html')

# 2. (API) حفظ منطقة جديدة
@admin.route('/add_zone', methods=['POST'])
@login_required
def add_zone():
    data = request.get_json()
    
    name = data.get('name')
    zone_type = data.get('type') 
    # تحويل الإحداثيات لنص JSON لحفظها في قاعدة البيانات
    coords = json.dumps(data.get('coords')) 
    
    new_zone = Zone(name=name, zone_type=zone_type, geometry_data=coords)
    db.session.add(new_zone)
    db.session.commit()
    
    return jsonify({'message': 'Zone added successfully!', 'id': new_zone.id})

# 3. (API) جلب المناطق
@admin.route('/get_zones')
@login_required
def get_zones():
    zones = Zone.query.all()
    zones_list = []
    for z in zones:
        # محاولة فك تشفير البيانات بأمان
        try:
            coords_data = json.loads(z.geometry_data)
        except:
            coords_data = []

        zones_list.append({
            'id': z.id,
            'name': z.name,
            'type': z.zone_type,
            'coords': coords_data
        })
    return jsonify(zones_list)

# ==========================================
#  نظام إدارة المستخدمين
# ==========================================

# 4. صفحة عرض قائمة المستخدمين
@admin.route('/users')
@login_required
def manage_users():
    if current_user.role != 'controller':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('pilot.dashboard'))
        
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin/users.html', users=users)

# 5. تنفيذ الموافقة أو الرفض
@admin.route('/approve_user/<int:user_id>/<action>')
@login_required
def approve_user(user_id, action):
    if current_user.role != 'controller':
        return redirect(url_for('pilot.dashboard'))

    user = User.query.get_or_404(user_id)
    
    if action == 'approve':
        user.is_approved = True
        flash(f'User {user.full_name} has been APPROVED.', 'success')
    elif action == 'reject':
        user.is_approved = False 
        flash(f'User {user.full_name} access REVOKED.', 'warning')
    
    # (تم إصلاح هذا الجزء الناقص)
    db.session.commit()
    return redirect(url_for('admin.manage_users'))

# ==========================================
#  نظام إدارة الرحلات (Flight Control)
# ==========================================

# 6. صفحة إدارة الرحلات الجوية (برج المراقبة)
@admin.route('/flights')
@login_required
def manage_flights():
    if current_user.role != 'controller':
        return redirect(url_for('pilot.dashboard'))
        
    # جلب الرحلات مرتبة الأحدث أولاً
    flights = FlightRequest.query.order_by(FlightRequest.created_at.desc()).all()
    return render_template('admin/flights.html', flights=flights)

# 7. (API) الموافقة أو الرفض على الرحلة
@admin.route('/process_flight/<int:flight_id>/<action>')
@login_required
def process_flight(flight_id, action):
    if current_user.role != 'controller':
        return redirect(url_for('pilot.dashboard'))
        
    flight = FlightRequest.query.get_or_404(flight_id)
    
    if action == 'approve':
        flight.status = 'approved'
        flash(f'Flight #{flight.id} Cleared for Takeoff.', 'success')
    elif action == 'reject':
        flight.status = 'rejected'
        flash(f'Flight #{flight.id} Request Denied.', 'danger')
        
    db.session.commit()
    return redirect(url_for('admin.manage_flights'))

# 8. (جديد) صفحة مراقبة الرحلة (Admin Simulation View)
@admin.route('/monitor_flight/<int:flight_id>')
@login_required
def monitor_flight(flight_id):
    if current_user.role != 'controller':
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    flight = FlightRequest.query.get_or_404(flight_id)
    
    # الأدمن يراقب فقط الرحلات الموافق عليها
    if flight.status != 'approved':
        flash('Cannot monitor flight. Status is not Approved.', 'warning')
        return redirect(url_for('admin.manage_flights'))
        
    return render_template('admin/simulate.html', flight=flight)