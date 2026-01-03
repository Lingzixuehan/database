from app import create_app, db
from app.models import User, Road, TrafficData, Event

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Road': Road, 'TrafficData': TrafficData, 'Event': Event}

if __name__ == '__main__':
    app.run(debug=True)