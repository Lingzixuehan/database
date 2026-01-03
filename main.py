from app import create_app, db, socketio
from app.models import User, Road, TrafficData, Event
import app.websocket  # Import to register WebSocket handlers

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Road': Road, 'TrafficData': TrafficData, 'Event': Event}

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)