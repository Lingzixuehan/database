from datetime import datetime, timezone
import bcrypt

from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)  # Kept for backward compatibility
    role = db.Column(db.String(20), nullable=False, default='user')
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    register_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=1)
    events = db.relationship('Event', backref='reporter', lazy='dynamic')

    def set_password(self, password: str) -> None:
        """Hash and set user password using bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode('utf-8')
        self.salt = salt.decode('utf-8')  # Store salt separately for reference

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        if not self.password_hash:
            return False
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

class Road(db.Model):
    __tablename__ = 'roads'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    # Using simple text for geo data for this demo
    start_point = db.Column(db.String(100))
    end_point = db.Column(db.String(100))
    geometry = db.Column(db.Text)
    length = db.Column(db.Numeric(10, 2), nullable=False)
    lanes = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer)
    speed_limit = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    traffic_data = db.relationship('TrafficData', backref='road', lazy='dynamic')
    events = db.relationship('Event', backref='road', lazy='dynamic')

class TrafficData(db.Model):
    __tablename__ = 'traffic_data'
    __table_args__ = (
        # Composite index for common queries (road + time range)
        db.Index('idx_road_timestamp', 'road_id', 'timestamp'),
        # Index for status-based queries
        db.Index('idx_status_timestamp', 'status', 'timestamp'),
        # Index for congestion analysis
        db.Index('idx_congestion_timestamp', 'congestion_level', 'timestamp'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True, default=lambda: datetime.now(timezone.utc))
    speed = db.Column(db.Numeric(6, 2))
    volume = db.Column(db.Integer)
    status = db.Column(db.String(20))
    congestion_level = db.Column(db.Numeric(3, 2))

class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = (
        # Composite index for event queries by road and time
        db.Index('idx_event_road_timestamp', 'road_id', 'timestamp'),
        # Index for active events filtering
        db.Index('idx_event_status_timestamp', 'status', 'timestamp'),
        # Index for severity-based queries
        db.Index('idx_event_severity', 'severity', 'timestamp'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'))
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    # Using simple text for geo data for this demo
    position = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='active')
    severity = db.Column(db.Integer)
