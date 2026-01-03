"""
Tests for API endpoints.
"""
import json
from datetime import datetime, timezone


def test_index_route(client):
    """Test index route."""
    response = client.get('/')
    assert response.status_code == 200


def test_get_all_roads(client, sample_road):
    """Test GET /api/roads endpoint."""
    response = client.get('/api/roads')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['name'] == 'Test Road'
    assert data[0]['code'] == 'R0001'


def test_get_road_snapshot(client, sample_road, sample_traffic_data):
    """Test GET /api/roads/<id> endpoint."""
    response = client.get(f'/api/roads/{sample_road.id}')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'road' in data
    assert 'latest' in data
    assert data['road']['name'] == 'Test Road'


def test_get_road_snapshot_not_found(client):
    """Test GET /api/roads/<id> with non-existent road."""
    response = client.get('/api/roads/99999')
    assert response.status_code == 404


def test_get_latest_traffic(client, sample_traffic_data):
    """Test GET /api/traffic/latest endpoint."""
    response = client.get('/api/traffic/latest?limit=10')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert 'speed' in data[0]
    assert 'volume' in data[0]


def test_create_event(client, sample_road):
    """Test POST /api/events endpoint."""
    payload = {
        'road_id': sample_road.id,
        'type': 'Accident',
        'description': 'Test accident',
        'severity': 3,
        'status': 'active'
    }

    response = client.post(
        '/api/events',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['type'] == 'Accident'
    assert data['status'] == 'active'


def test_create_event_validation_error(client):
    """Test POST /api/events with invalid data."""
    payload = {
        'road_id': 'invalid',  # Should be integer
        'type': 'Accident'
    }

    response = client.post(
        '/api/events',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_get_events(client, sample_event):
    """Test GET /api/events endpoint."""
    response = client.get('/api/events?status=active')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['status'] == 'active'


def test_dashboard_summary(client, sample_road, sample_traffic_data):
    """Test GET /api/dashboard/summary endpoint."""
    response = client.get('/api/dashboard/summary')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'total_roads' in data
    assert 'active_events' in data
    assert data['total_roads'] >= 1


def test_system_status(client):
    """Test GET /api/system/status endpoint."""
    response = client.get('/api/system/status')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'totals' in data
    assert 'generated_at' in data
