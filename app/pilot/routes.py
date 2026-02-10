from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Zone, Drone, FlightRequest
from datetime import datetime
import json

pilot = Blueprint('pilot', __name__, url_prefix='/pilot')

@pilot.route('/dashboard')
@login_required
def dashboard():
    """Pilot/Operator dashboard view."""
    if current_user.role != 'operator':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    my_drones = Drone.query.filter_by(owner=current_user).all()
    my_flights = FlightRequest.query.filter_by(pilot=current_user).order_by(FlightRequest.created_at.desc()).all()
    
    return render_template('pilot/dashboard.html', drones=my_drones, flights=my_flights)

@pilot.route('/add_drone', methods=['GET', 'POST'])
@login_required
def add_drone():
    """Form to register a new drone."""
    if request.method == 'POST':
        name = request.form.get('name')
        serial = request.form.get('serial_number')
        weight = request.form.get('weight')
        usage = request.form.get('usage_type')
        
        if Drone.query.filter_by(serial_number=serial).first():
            flash('Serial Number already exists!', 'danger')
            return redirect(url_for('pilot.add_drone'))
            
        new_drone = Drone(name=name, serial_number=serial, weight=float(weight), usage_type=usage, owner=current_user)
        db.session.add(new_drone)
        db.session.commit()
        flash('Drone Registered Successfully!', 'success')
        return redirect(url_for('pilot.dashboard'))
        
    return render_template('pilot/add_drone.html')

@pilot.route('/request_flight', methods=['GET', 'POST'])
@login_required
def request_flight():
    """Form to submit a new flight plan."""
    drones = Drone.query.filter_by(owner=current_user).all()
    
    if request.method == 'POST':
        drone_id = request.form.get('drone_id')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        max_altitude = request.form.get('max_altitude')
        path_json = request.form.get('path_coords')
        
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            
            new_flight = FlightRequest(
                pilot=current_user,
                drone_id=drone_id,
                start_time=start_time,
                end_time=end_time,
                max_altitude=float(max_altitude),
                path_data=path_json,
                status='pending'
            )
            
            db.session.add(new_flight)
            db.session.commit()
            flash('Flight Plan Submitted! Awaiting Approval.', 'success')
            return redirect(url_for('pilot.dashboard'))
        except Exception as e:
            flash(f'Error submitting flight: {str(e)}', 'danger')

    return render_template('pilot/request_flight.html', drones=drones)

@pilot.route('/get_operational_zones')
@login_required
def get_operational_zones():
    """API to fetch zones for the pilot map."""
    try:
        zones = Zone.query.all()
        zones_list = []
        for z in zones:
            try:
                coords_data = json.loads(z.geometry_data)
            except json.JSONDecodeError:
                coords_data = [] 

            zones_list.append({
                'name': z.name, 
                'type': z.zone_type, 
                'coords': coords_data
            })
        
        return jsonify(zones_list)
        
    except Exception as e:
        return jsonify({'error': 'Server Error fetching zones', 'details': str(e)}), 500

@pilot.route('/simulate/<int:flight_id>')
@login_required
def simulate_flight(flight_id):
    """View to simulate a user's approved flight."""
    flight = FlightRequest.query.get_or_404(flight_id)
    
    if flight.pilot != current_user:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('pilot.dashboard'))
        
    if flight.status != 'approved':
        flash('Flight not approved yet!', 'warning')
        return redirect(url_for('pilot.dashboard'))
        
    return render_template('pilot/simulate.html', flight=flight)