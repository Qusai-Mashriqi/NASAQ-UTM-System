from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO()

# توجيه المستخدم لصفحة الدخول إذا حاول فتح صفحة محمية
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # تهيئة الإضافات
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # --- استيراد الـ Blueprints ---
    from app.auth.routes import auth
    from app.admin.routes import admin
    from app.pilot.routes import pilot
    from app.main.routes import main  # <--- (1) هذا هو السطر الجديد للاستيراد
    
    print("--> CHECK: Registering Main Blueprint...") # <--- أضف هذا السطر

    # --- تسجيل الـ Blueprints ---
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(pilot)
    app.register_blueprint(main)      # <--- (2) هذا هو السطر الجديد للتسجيل

    # إنشاء قاعدة البيانات
    with app.app_context():
        db.create_all()

    return app