from flask import Blueprint, render_template

print("--> SUCCESS: Main Routes File is Loading...") # <--- أضف هذا السطر

# تأكد أن الاسم هنا هو 'main'
main = Blueprint('main', __name__)

# هذا السطر هو الذي يضيف الرابط للصفحة الرئيسية
@main.route('/') 
def index():
    print("--> Accessing Home Page") # (1) جملة طباعة للتأكد أن الكود يعمل
    return render_template('landing.html')