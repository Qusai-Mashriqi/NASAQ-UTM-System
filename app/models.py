from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# جدول المستخدمين (شامل لكل الحقول المحتملة)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'operator' or 'controller'
    
    # === حقول المشغل (UAV Operator) ===
    national_id = db.Column(db.String(20))      # الرقم الوطني
    license_number = db.Column(db.String(50))   # رقم الرخصة (هذا اللي كان ناقص)
    organization_type = db.Column(db.String(50)) # فرد، شركة، جهة حكومية
    
    # === حقول المراقب (Controller) ===
    job_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    
    # حالة الموافقة
    is_approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email}')"

# جدول المناطق
class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_type = db.Column(db.String(20), nullable=False) 
    geometry_data = db.Column(db.Text, nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# جدول الدرونات
class Drone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    usage_type = db.Column(db.String(50), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('drones', lazy=True))

# جدول الرحلات
class FlightRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_altitude = db.Column(db.Float, nullable=False)
    path_data = db.Column(db.Text, nullable=False) 
    
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pilot = db.relationship('User', backref='flight_requests')
    drone = db.relationship('Drone', backref='flight_requests')