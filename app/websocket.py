"""
WebSocket event handlers for real-time data broadcasting.
"""
from flask_socketio import emit, join_room, leave_room
from . import socketio
from .services import get_latest_traffic, get_events


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connected', {'data': 'Connected to traffic system'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('subscribe_traffic')
def handle_subscribe_traffic(data):
    """Subscribe to real-time traffic updates."""
    room = 'traffic_updates'
    join_room(room)
    emit('subscribed', {'room': room, 'message': 'Subscribed to traffic updates'})


@socketio.on('unsubscribe_traffic')
def handle_unsubscribe_traffic():
    """Unsubscribe from traffic updates."""
    room = 'traffic_updates'
    leave_room(room)
    emit('unsubscribed', {'room': room})


@socketio.on('subscribe_road')
def handle_subscribe_road(data):
    """Subscribe to updates for a specific road."""
    road_id = data.get('road_id')
    if road_id:
        room = f'road_{road_id}'
        join_room(room)
        emit('subscribed', {'room': room, 'road_id': road_id})


@socketio.on('unsubscribe_road')
def handle_unsubscribe_road(data):
    """Unsubscribe from a specific road."""
    road_id = data.get('road_id')
    if road_id:
        room = f'road_{road_id}'
        leave_room(room)
        emit('unsubscribed', {'room': room, 'road_id': road_id})


@socketio.on('subscribe_events')
def handle_subscribe_events():
    """Subscribe to real-time event notifications."""
    room = 'event_updates'
    join_room(room)
    emit('subscribed', {'room': room, 'message': 'Subscribed to event updates'})


@socketio.on('request_traffic_update')
def handle_traffic_update_request():
    """Send latest traffic data on request."""
    traffic_data = get_latest_traffic(limit=10)
    emit('traffic_update', {'data': traffic_data})


@socketio.on('request_events_update')
def handle_events_update_request():
    """Send latest events on request."""
    events = get_events(limit=10, status='active')
    emit('events_update', {'data': events})


def broadcast_traffic_update(traffic_data):
    """Broadcast traffic update to all subscribed clients."""
    socketio.emit('traffic_update', {'data': traffic_data}, room='traffic_updates')


def broadcast_road_update(road_id, traffic_data):
    """Broadcast traffic update for a specific road."""
    socketio.emit('road_update', {'road_id': road_id, 'data': traffic_data}, room=f'road_{road_id}')


def broadcast_event(event_data):
    """Broadcast new event to all subscribed clients."""
    socketio.emit('new_event', {'data': event_data}, room='event_updates')
