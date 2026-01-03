"""
Pytest configuration and fixtures.
"""
import pytest
from app import create_app, db
from app.models import User, Road, TrafficData, Event
from datetime import datetime, timezone


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def sample_user(app):
    """Create a sample user."""
    user = User(
        username='testuser',
        email='test@example.com',
        role='user',
        password_hash='',
        salt=''
    )
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def sample_road(app):
    """Create a sample road."""
    road = Road(
        name='Test Road',
        code='R0001',
        start_point='POINT(116.4074 39.9042)',
        end_point='POINT(116.4174 39.9142)',
        geometry='LINESTRING(116.4074 39.9042, 116.4174 39.9142)',
        length=5.5,
        lanes=4,
        level=2,
        speed_limit=60
    )
    db.session.add(road)
    db.session.commit()
    return road


@pytest.fixture(scope='function')
def sample_traffic_data(app, sample_road):
    """Create sample traffic data."""
    traffic = TrafficData(
        road_id=sample_road.id,
        timestamp=datetime.now(timezone.utc),
        speed=45.5,
        volume=320,
        status='MODERATE',
        congestion_level=0.35
    )
    db.session.add(traffic)
    db.session.commit()
    return traffic


@pytest.fixture(scope='function')
def sample_event(app, sample_user, sample_road):
    """Create a sample event."""
    event = Event(
        user_id=sample_user.id,
        road_id=sample_road.id,
        type='Accident',
        description='Test accident event',
        position='POINT(116.4100 39.9100)',
        timestamp=datetime.now(timezone.utc),
        status='active',
        severity=3
    )
    db.session.add(event)
    db.session.commit()
    return event
