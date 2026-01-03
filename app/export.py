"""
Data export utilities for traffic system.
"""
import io
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
from flask import send_file

from .models import TrafficData, Event, Road
from . import db


def export_traffic_data_csv(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """Export traffic data to CSV format."""
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)

    # Query traffic data
    query = TrafficData.query.filter(
        TrafficData.timestamp.between(start_date, end_date)
    ).join(Road).add_columns(
        TrafficData.id,
        Road.name.label('road_name'),
        Road.code.label('road_code'),
        TrafficData.timestamp,
        TrafficData.speed,
        TrafficData.volume,
        TrafficData.status,
        TrafficData.congestion_level
    ).order_by(TrafficData.timestamp.desc())

    # Convert to DataFrame
    data = []
    for row in query.all():
        data.append({
            'ID': row.id,
            'Road Name': row.road_name,
            'Road Code': row.road_code,
            'Timestamp': row.timestamp.isoformat() if row.timestamp else '',
            'Speed (km/h)': float(row.speed) if row.speed else None,
            'Volume': row.volume,
            'Status': row.status,
            'Congestion Level': float(row.congestion_level) if row.congestion_level else None
        })

    df = pd.DataFrame(data)

    # Create CSV in memory
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'traffic_data_{start_date.date()}_{end_date.date()}.csv'
    )


def export_traffic_data_excel(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """Export traffic data to Excel format."""
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)

    # Create Excel file with multiple sheets
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Traffic Data
        traffic_query = TrafficData.query.filter(
            TrafficData.timestamp.between(start_date, end_date)
        ).join(Road).add_columns(
            TrafficData.id,
            Road.name.label('road_name'),
            Road.code.label('road_code'),
            TrafficData.timestamp,
            TrafficData.speed,
            TrafficData.volume,
            TrafficData.status,
            TrafficData.congestion_level
        ).order_by(TrafficData.timestamp.desc())

        traffic_data = []
        for row in traffic_query.all():
            traffic_data.append({
                'ID': row.id,
                'Road Name': row.road_name,
                'Road Code': row.road_code,
                'Timestamp': row.timestamp,
                'Speed (km/h)': float(row.speed) if row.speed else None,
                'Volume': row.volume,
                'Status': row.status,
                'Congestion Level': float(row.congestion_level) if row.congestion_level else None
            })

        df_traffic = pd.DataFrame(traffic_data)
        df_traffic.to_excel(writer, sheet_name='Traffic Data', index=False)

        # Sheet 2: Events
        events_query = Event.query.filter(
            Event.timestamp.between(start_date, end_date)
        ).join(Road).add_columns(
            Event.id,
            Road.name.label('road_name'),
            Event.type,
            Event.description,
            Event.timestamp,
            Event.status,
            Event.severity
        ).order_by(Event.timestamp.desc())

        events_data = []
        for row in events_query.all():
            events_data.append({
                'ID': row.id,
                'Road Name': row.road_name,
                'Event Type': row.type,
                'Description': row.description,
                'Timestamp': row.timestamp,
                'Status': row.status,
                'Severity': row.severity
            })

        df_events = pd.DataFrame(events_data)
        df_events.to_excel(writer, sheet_name='Events', index=False)

        # Sheet 3: Summary Statistics
        summary_data = {
            'Metric': [
                'Total Traffic Records',
                'Total Events',
                'Average Speed (km/h)',
                'Average Congestion Level',
                'Date Range Start',
                'Date Range End'
            ],
            'Value': [
                len(traffic_data),
                len(events_data),
                df_traffic['Speed (km/h)'].mean() if not df_traffic.empty else 0,
                df_traffic['Congestion Level'].mean() if not df_traffic.empty else 0,
                start_date.isoformat(),
                end_date.isoformat()
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'traffic_report_{start_date.date()}_{end_date.date()}.xlsx'
    )


def export_events_csv(status: Optional[str] = None):
    """Export events to CSV format."""
    query = Event.query.join(Road).add_columns(
        Event.id,
        Road.name.label('road_name'),
        Event.type,
        Event.description,
        Event.timestamp,
        Event.status,
        Event.severity,
        Event.position
    ).order_by(Event.timestamp.desc())

    if status and status != 'all':
        query = query.filter(Event.status == status)

    data = []
    for row in query.all():
        data.append({
            'ID': row.id,
            'Road Name': row.road_name,
            'Event Type': row.type,
            'Description': row.description,
            'Timestamp': row.timestamp.isoformat() if row.timestamp else '',
            'Status': row.status,
            'Severity': row.severity,
            'Position': row.position
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'events_{status or "all"}_{datetime.now().date()}.csv'
    )
