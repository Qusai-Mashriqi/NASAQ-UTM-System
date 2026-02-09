from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    # 1. تحقق هل السوبر أدمن موجود أصلاً؟
    if User.query.filter_by(email="admin@nasaq.jo").first():
        print("Super Admin already exists!")
    else:
        # 2. إنشاء الحساب
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        
        super_admin = User(
            full_name="Chief Commander",
            email="admin@nasaq.jo",        # إيميل الدخول
            password=hashed_password,      # الباسورد: admin123
            role="controller",             # هو مراقب، لكن مميز
            phone="+962790000000",
            
            # حقول المراقب
            job_id="ADMIN-MODE-001",
            department="Headquarters",
            
            # أهم نقطة: مفعل تلقائياً
            is_approved=True 
        )
        
        db.session.add(super_admin)
        db.session.commit()
        print("--> SUCCESS: Super Admin Account Created!")
        print("--> Email: admin@nasaq.jo")
        print("--> Pass:  admin123")