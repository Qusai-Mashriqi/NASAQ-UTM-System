from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User
from flask_login import login_user, logout_user, current_user

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register/select')
def register_selection():
    """Route to select user role before registration."""
    return render_template('auth/register_selection.html')

@auth.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    """
    Handles user registration for both Pilots (Operators) and Controllers.
    Dynamically adjusts validation based on the selected role.
    """
    if current_user.is_authenticated:
        return redirect(url_for('pilot.dashboard'))
    
    if role not in ['operator', 'controller']:
        return redirect(url_for('auth.register_selection'))

    if request.method == 'POST':
        # Common fields
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Operator specific
        organization_type = request.form.get('organization_type')
        national_id = request.form.get('national_id')
        license_number = request.form.get('license_number')
        
        # Controller specific
        job_id = request.form.get('job_id')
        department = request.form.get('department')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Default approval logic
        is_approved = True
        
        if role == 'controller':
            # Check if this is the first controller (Super Admin logic)
            if User.query.filter_by(role='controller').count() > 0:
                is_approved = False
                flash('Clearance Request Submitted. Pending Super Controller Approval.', 'warning')
            else:
                flash('System initialized. You are the Super Controller.', 'success')
        else:
            flash('Application Successful. Provisional Access Granted.', 'success')
        
        user = User(
            full_name=full_name,
            phone=phone,
            email=email, 
            password=hashed_password, 
            role=role, 
            is_approved=is_approved,
            organization_type=organization_type,
            national_id=national_id,
            license_number=license_number,
            job_id=job_id,
            department=department
        )
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', role=role)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication and redirection based on role."""
    if current_user.is_authenticated:
        if current_user.role == 'admin': # Assuming 'controller' might be stored as 'admin' logically or kept as controller
             return redirect(url_for('admin.dashboard'))
        return redirect(url_for('pilot.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Check for approval status for controllers
            if user.role == 'controller' and not user.is_approved:
                flash('Account pending approval.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            next_page = url_for('admin.dashboard') if user.role == 'controller' else url_for('pilot.dashboard')
            return redirect(next_page)
        else:
            flash('Login failed. Please check your credentials.', 'danger')
            
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))