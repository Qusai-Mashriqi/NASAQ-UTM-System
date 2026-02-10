from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Run the application with SocketIO support
    socketio.run(app, debug=True)