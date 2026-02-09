from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print(app.url_map)   # <--- أضفنا هذا السطر لنرى الخريطة
    socketio.run(app, debug=True)