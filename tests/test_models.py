"""
Tests for database models.
"""
from app.models import User, Road, TrafficData, Event


def test_user_password_hashing(app):
    """Test user password hashing and verification."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash='',
        salt=''
    )
    user.set_password('mypassword')

    assert user.password_hash != 'mypassword'
    assert user.check_password('mypassword')
    assert not user.check_password('wrongpassword')


def test_road_model(sample_road):
    """Test road model creation."""
    assert sample_road.id is not None
    assert sample_road.name == 'Test Road'
    assert sample_road.code == 'R0001'
    assert sample_road.lanes == 4


def test_traffic_data_model(sample_traffic_data):
    """Test traffic data model."""
    assert sample_traffic_data.id is not None
    assert float(sample_traffic_data.speed) == 45.5
    assert sample_traffic_data.volume == 320
    assert sample_traffic_data.status == 'MODERATE'


def test_event_model(sample_event):
    """Test event model."""
    assert sample_event.id is not None
    assert sample_event.type == 'Accident'
    assert sample_event.status == 'active'
    assert sample_event.severity == 3


def test_road_traffic_relationship(sample_road, sample_traffic_data):
    """Test relationship between road and traffic data."""
    assert sample_traffic_data.road_id == sample_road.id
    assert sample_traffic_data.road.name == 'Test Road'
