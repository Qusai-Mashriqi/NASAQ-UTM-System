from app import create_app, db, bcrypt
from app.models import User

app = create_app()

def create_admin():
    """
    Initializes the database with a default Super Admin account.
    Usage: Run this script once after creating the database.
    """
    with app.app_context():
        # Check if admin already exists
        if User.query.filter_by(email="admin@nasaq.jo").first():
            print("[-] Super Admin account already exists.")
        else:
            # Create standard admin account
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            
            super_admin = User(
                full_name="System Administrator",
                email="admin@nasaq.jo",
                password=hashed_password,
                role="controller",
                phone="+962790000000",
                
                # Controller specific fields
                job_id="SYS-ADMIN-001",
                department="IT Operations",
                
                # Auto-approve the first admin
                is_approved=True 
            )
            
            db.session.add(super_admin)
            db.session.commit()
            print("[+] SUCCESS: Super Admin account created successfully.")
            print("    Email: admin@nasaq.jo")
            print("    Pass:  admin123")

if __name__ == "__main__":
    create_admin()