from flask import Blueprint, render_template, jsonify, request
from marshmallow import ValidationError
from datetime import datetime

from .schemas import EventCreateSchema, EventFilterSchema, PaginationSchema
from .services import (
    build_dashboard_summary,
    create_event,
    get_alerts,
    get_all_roads,
    get_events,
    get_latest_traffic,
    get_map_events,
    get_road_by_id,
    get_road_snapshot,
    get_system_status,
    get_traffic_history,
    get_weekly_report,
)
from .export import (
    export_traffic_data_csv,
    export_traffic_data_excel,
    export_events_csv
)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/events')
def events_page():
    return render_template('events.html')

@main.route('/auth')
def auth_page():
    return render_template('auth.html')

@main.route('/api/roads')
def roads_endpoint():
    return jsonify(get_all_roads())

@main.route('/api/roads/<int:road_id>')
def road_snapshot(road_id):
    snapshot = get_road_snapshot(road_id)
    if not snapshot:
        return jsonify({'error': 'Road not found.'}), 404
    return jsonify(snapshot)

@main.route('/api/traffic/latest')
def latest_traffic_endpoint():
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(limit or 10, 100))
    offset = max(0, offset)
    return jsonify(get_latest_traffic(limit, offset))

@main.route('/api/events', methods=['GET', 'POST'])
def events_endpoint():
    if request.method == 'GET':
        # Validate query parameters
        filter_schema = EventFilterSchema()
        try:
            filters = filter_schema.load(request.args)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400

        offset = request.args.get('offset', default=0, type=int)
        offset = max(0, offset)

        return jsonify(get_events(
            limit=filters.get('limit'),
            status=filters.get('status'),
            offset=offset
        ))

    # POST - Create event
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'error': 'Request body cannot be empty.'}), 400

    # Validate input using schema
    schema = EventCreateSchema()
    try:
        validated_data = schema.load(payload)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400

    # Check if road exists
    if not get_road_by_id(validated_data['road_id']):
        return jsonify({'error': 'Road not found.'}), 404

    created = create_event(validated_data)
    return jsonify(created), 201

@main.route('/api/traffic/history/<int:road_id>')
def traffic_history(road_id):
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    road = get_road_by_id(road_id)
    if not road:
        return jsonify({'error': 'Road not found.'}), 404

    try:
        traffic, events, window = get_traffic_history(road_id, start_str, end_str)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify({
        'road': {
            'id': road.id,
            'name': road.name,
            'code': road.code,
        },
        'window': {
            'start': window[0].isoformat(),
            'end': window[1].isoformat(),
        },
        'traffic': traffic,
        'events': events,
    })

@main.route('/api/dashboard/summary')
def dashboard_summary():
    return jsonify(build_dashboard_summary())

@main.route('/api/system/status')
def system_status():
    return jsonify(get_system_status())

@main.route('/api/reports/weekly')
def weekly_report():
    return jsonify(get_weekly_report())

@main.route('/api/alerts')
def alerts_endpoint():
    return jsonify(get_alerts())

@main.route('/api/events/map')
def events_map():
    limit = request.args.get('limit', type=int, default=100)
    limit = max(1, min(limit, 200))
    return jsonify(get_map_events(limit))

@main.route('/api/export/traffic/csv')
def export_traffic_csv():
    """Export traffic data to CSV."""
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start_date = datetime.fromisoformat(start_str) if start_str else None
    end_date = datetime.fromisoformat(end_str) if end_str else None

    return export_traffic_data_csv(start_date, end_date)

@main.route('/api/export/traffic/excel')
def export_traffic_excel():
    """Export traffic data to Excel."""
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start_date = datetime.fromisoformat(start_str) if start_str else None
    end_date = datetime.fromisoformat(end_str) if end_str else None

    return export_traffic_data_excel(start_date, end_date)

@main.route('/api/export/events/csv')
def export_events_csv_endpoint():
    """Export events to CSV."""
    status = request.args.get('status', default='all')
    return export_events_csv(status)
