from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    User model for storing account details.
    Handles both 'operator' (Pilots) and 'controller' (Admins) roles.
    """
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'operator' or 'controller'
    
    # Operator specific fields
    national_id = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    organization_type = db.Column(db.String(50)) # Individual, Company, Government
    
    # Controller specific fields
    job_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    
    # Account Status
    is_approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email}')"

class Zone(db.Model):
    """Model for Geofencing Zones (No-Fly Zones, Restricted Areas)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_type = db.Column(db.String(20), nullable=False) 
    geometry_data = db.Column(db.Text, nullable=False)  # Stored as JSON string
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Drone(db.Model):
    """Model for registered UAVs."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    usage_type = db.Column(db.String(50), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('drones', lazy=True))

class FlightRequest(db.Model):
    """Model for flight authorization requests."""
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_altitude = db.Column(db.Float, nullable=False)
    path_data = db.Column(db.Text, nullable=False)  # Waypoints as JSON
    
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pilot = db.relationship('User', backref='flight_requests')
    drone = db.relationship('Drone', backref='flight_requests')