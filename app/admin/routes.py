from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Zone, User, FlightRequest
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    """Admin/Controller main dashboard view."""
    if current_user.role != 'controller':
        flash('Restricted Area! Authorized Personnel Only.', 'danger')
        return redirect(url_for('pilot.dashboard'))
    return render_template('admin/dashboard.html')

# --- Zone Management APIs ---

@admin.route('/add_zone', methods=['POST'])
@login_required
def add_zone():
    """API to create a new Geofencing zone."""
    data = request.get_json()
    
    name = data.get('name')
    zone_type = data.get('type') 
    coords = json.dumps(data.get('coords')) 
    
    new_zone = Zone(name=name, zone_type=zone_type, geometry_data=coords)
    db.session.add(new_zone)
    db.session.commit()
    
    return jsonify({'message': 'Zone added successfully!', 'id': new_zone.id})

@admin.route('/get_zones')
@login_required
def get_zones():
    """API to fetch all active zones."""
    zones = Zone.query.all()
    zones_list = []
    for z in zones:
        try:
            coords_data = json.loads(z.geometry_data)
        except json.JSONDecodeError:
            coords_data = []

        zones_list.append({
            'id': z.id,
            'name': z.name,
            'type': z.zone_type,
            'coords': coords_data
        })
    return jsonify(zones_list)

# --- User Management ---

@admin.route('/users')
@login_required
def manage_users():
    """View to manage registered users."""
    if current_user.role != 'controller':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('pilot.dashboard'))
        
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin/users.html', users=users)

@admin.route('/approve_user/<int:user_id>/<action>')
@login_required
def approve_user(user_id, action):
    """Action to Approve or Reject a user account."""
    if current_user.role != 'controller':
        return redirect(url_for('pilot.dashboard'))

    user = User.query.get_or_404(user_id)
    
    if action == 'approve':
        user.is_approved = True
        flash(f'User {user.full_name} has been APPROVED.', 'success')
    elif action == 'reject':
        user.is_approved = False 
        flash(f'User {user.full_name} access REVOKED.', 'warning')
    
    db.session.commit()
    return redirect(url_for('admin.manage_users'))

# --- Flight Management ---

@admin.route('/flights')
@login_required
def manage_flights():
    """View to oversee flight requests."""
    if current_user.role != 'controller':
        return redirect(url_for('pilot.dashboard'))
        
    flights = FlightRequest.query.order_by(FlightRequest.created_at.desc()).all()
    return render_template('admin/flights.html', flights=flights)

@admin.route('/process_flight/<int:flight_id>/<action>')
@login_required
def process_flight(flight_id, action):
    """Action to Approve or Reject a flight plan."""
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

@admin.route('/monitor_flight/<int:flight_id>')
@login_required
def monitor_flight(flight_id):
    """Real-time flight simulation monitoring view."""
    if current_user.role != 'controller':
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    flight = FlightRequest.query.get_or_404(flight_id)
    
    if flight.status != 'approved':
        flash('Cannot monitor flight. Status is not Approved.', 'warning')
        return redirect(url_for('admin.manage_flights'))
        
    return render_template('admin/simulate.html', flight=flight)