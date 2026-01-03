"""
Business logic helpers for the Urban Traffic Status Inquiry System.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func

from . import db, cache
from .models import Event, Road, TrafficData, User


def _to_iso(dt: datetime) -> str:
    """Serialize datetime to ISO 8601 string."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _to_float(value) -> Optional[float]:
    return float(value) if value is not None else None


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO formatted string (accepting trailing Z) into an aware datetime."""
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_point_wkt(wkt: Optional[str]) -> Optional[Dict[str, float]]:
    if not wkt:
        return None
    try:
        cleaned = wkt.strip().lstrip("POINT").lstrip("(").rstrip(")")
        lon_str, lat_str = cleaned.split()
        return {"lat": float(lat_str), "lon": float(lon_str)}
    except Exception:
        return None


@cache.cached(timeout=300, key_prefix='all_roads')
def get_all_roads() -> List[Dict]:
    """Get all roads (cached for 5 minutes)."""
    roads = Road.query.order_by(Road.name.asc()).all()
    return [
        {
            "id": road.id,
            "name": road.name,
            "code": road.code,
            "lanes": road.lanes,
            "level": road.level,
            "speed_limit": road.speed_limit,
            "length": _to_float(road.length),
        }
        for road in roads
    ]


def get_road_by_id(road_id: int) -> Optional[Road]:
    return db.session.get(Road, road_id)


def get_latest_traffic(limit: int = 10, offset: int = 0) -> Dict:
    """Get latest traffic data with pagination support."""
    total = TrafficData.query.count()

    rows = (
        TrafficData.query.order_by(TrafficData.timestamp.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        'data': [_serialize_traffic_row(row) for row in rows],
        'total': total,
        'limit': limit,
        'offset': offset
    }


def get_events(
    limit: Optional[int] = None, status: Optional[str] = "active", offset: int = 0
) -> Dict:
    """Get events with pagination support."""
    query = Event.query.order_by(Event.timestamp.desc())
    if status and status != "all":
        query = query.filter_by(status=status)

    total = query.count()

    if limit:
        query = query.limit(limit).offset(offset)

    rows = query.all()

    return {
        'data': [_serialize_event_row(row) for row in rows],
        'total': total,
        'limit': limit or total,
        'offset': offset
    }


def _serialize_traffic_row(row: TrafficData) -> Dict:
    return {
        "id": row.id,
        "road_id": row.road_id,
        "road_name": row.road.name if row.road else None,
        "timestamp": _to_iso(row.timestamp),
        "speed": _to_float(row.speed),
        "volume": row.volume,
        "status": row.status,
        "congestion_level": _to_float(row.congestion_level),
    }


def _serialize_event_row(row: Event) -> Dict:
    return {
        "id": row.id,
        "road_id": row.road_id,
        "road_name": row.road.name if row.road else None,
        "type": row.type,
        "description": row.description,
        "position": row.position,
        "timestamp": _to_iso(row.timestamp),
        "status": row.status,
        "severity": row.severity,
    }


def get_traffic_history(
    road_id: int, start: Optional[str], end: Optional[str]
) -> Tuple[List[Dict], List[Dict], Tuple[datetime, datetime]]:
    default_end = datetime.now(timezone.utc)
    default_start = default_end - timedelta(days=7)
    start_dt = _parse_iso_datetime(start) or default_start
    end_dt = _parse_iso_datetime(end) or default_end

    if start_dt > end_dt:
        raise ValueError("Start time must be earlier than end time.")

    traffic_rows = (
        TrafficData.query.filter(
            TrafficData.road_id == road_id,
            TrafficData.timestamp.between(start_dt, end_dt),
        )
        .order_by(TrafficData.timestamp.asc())
        .all()
    )

    event_rows = (
        Event.query.filter(
            Event.road_id == road_id,
            Event.timestamp.between(start_dt, end_dt),
        )
        .order_by(Event.timestamp.asc())
        .all()
    )

    return (
        [_serialize_traffic_row(row) for row in traffic_rows],
        [_serialize_event_row(row) for row in event_rows],
        (start_dt, end_dt),
    )


@cache.cached(timeout=60, key_prefix='dashboard_summary')
def build_dashboard_summary(window_hours: int = 1) -> Dict:
    """Build dashboard summary (cached for 1 minute)."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)

    total_roads = db.session.query(func.count(Road.id)).scalar() or 0
    active_events = (
        db.session.query(func.count(Event.id))
        .filter(Event.status == "active")
        .scalar()
        or 0
    )

    avg_speed = (
        db.session.query(func.avg(TrafficData.speed))
        .filter(TrafficData.timestamp >= window_start)
        .scalar()
    )
    max_volume = (
        db.session.query(func.max(TrafficData.volume))
        .filter(TrafficData.timestamp >= window_start)
        .scalar()
    )

    congested = (
        db.session.query(
            Road.name.label("road_name"),
            func.avg(TrafficData.congestion_level).label("avg_congestion"),
        )
        .join(TrafficData, TrafficData.road_id == Road.id)
        .filter(TrafficData.timestamp >= window_start)
        .group_by(Road.id)
        .order_by(func.avg(TrafficData.congestion_level).desc())
        .limit(5)
        .all()
    )

    return {
        "generated_at": _to_iso(now),
        "window_hours": window_hours,
        "total_roads": total_roads,
        "active_events": active_events,
        "avg_speed_last_window": _to_float(avg_speed),
        "max_volume_last_window": int(max_volume) if max_volume is not None else None,
        "top_congested_roads": [
            {"road_name": row.road_name, "avg_congestion": _to_float(row.avg_congestion)}
            for row in congested
        ],
    }


def get_road_snapshot(road_id: int) -> Optional[Dict]:
    road = get_road_by_id(road_id)
    if not road:
        return None

    now = datetime.now(timezone.utc)
    day_window = now - timedelta(hours=24)

    latest = (
        TrafficData.query.filter_by(road_id=road_id)
        .order_by(TrafficData.timestamp.desc())
        .first()
    )

    avg_speed, avg_volume, avg_congestion = (
        db.session.query(
            func.avg(TrafficData.speed),
            func.avg(TrafficData.volume),
            func.avg(TrafficData.congestion_level),
        )
        .filter(
            TrafficData.road_id == road_id,
            TrafficData.timestamp >= day_window,
        )
        .first()
    )

    event_count = (
        db.session.query(func.count(Event.id))
        .filter(Event.road_id == road_id, Event.timestamp >= day_window)
        .scalar()
        or 0
    )

    return {
        "road": {
            "id": road.id,
            "name": road.name,
            "code": road.code,
            "lanes": road.lanes,
            "length": _to_float(road.length),
            "speed_limit": road.speed_limit,
            "start_point": _parse_point_wkt(road.start_point),
            "end_point": _parse_point_wkt(road.end_point),
        },
        "latest": _serialize_traffic_row(latest) if latest else None,
        "averages": {
            "speed": _to_float(avg_speed),
            "volume": _to_float(avg_volume),
            "congestion": _to_float(avg_congestion),
        },
        "events_last_24h": int(event_count),
        "window_start": _to_iso(day_window),
        "window_end": _to_iso(now),
    }


def create_event(payload: Dict) -> Dict:
    timestamp = _parse_iso_datetime(payload.get("timestamp")) or datetime.now(
        timezone.utc
    )
    event = Event(
        user_id=payload.get("user_id"),
        road_id=payload["road_id"],
        type=payload["type"],
        description=payload.get("description"),
        position=payload.get("position"),
        timestamp=timestamp,
        status=payload.get("status", "active"),
        severity=payload.get("severity"),
    )
    db.session.add(event)
    db.session.commit()

    return _serialize_event_row(event)


def get_system_status() -> Dict:
    now = datetime.now(timezone.utc)
    tables = {
        "users": db.session.query(func.count(User.id)).scalar() or 0,
        "roads": db.session.query(func.count(Road.id)).scalar() or 0,
        "traffic": db.session.query(func.count(TrafficData.id)).scalar() or 0,
        "events": db.session.query(func.count(Event.id)).scalar() or 0,
    }

    latest_event = Event.query.order_by(Event.timestamp.desc()).first()
    latest_traffic = TrafficData.query.order_by(TrafficData.timestamp.desc()).first()

    return {
        "generated_at": _to_iso(now),
        "totals": tables,
        "latest_event": _serialize_event_row(latest_event) if latest_event else None,
        "latest_traffic": _serialize_traffic_row(latest_traffic) if latest_traffic else None,
    }


def get_weekly_report() -> Dict:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)

    traffic_count = (
        db.session.query(func.count(TrafficData.id))
        .filter(TrafficData.timestamp >= start)
        .scalar()
        or 0
    )
    avg_speed = (
        db.session.query(func.avg(TrafficData.speed))
        .filter(TrafficData.timestamp >= start)
        .scalar()
    )

    total_events = (
        db.session.query(func.count(Event.id))
        .filter(Event.timestamp >= start)
        .scalar()
        or 0
    )
    severe_events = (
        db.session.query(func.count(Event.id))
        .filter(Event.timestamp >= start, Event.severity >= 3)
        .scalar()
        or 0
    )

    busiest_roads = (
        db.session.query(
            Road.name.label("road_name"),
            func.avg(TrafficData.volume).label("avg_volume"),
        )
        .join(TrafficData, TrafficData.road_id == Road.id)
        .filter(TrafficData.timestamp >= start)
        .group_by(Road.id)
        .order_by(func.avg(TrafficData.volume).desc())
        .limit(3)
        .all()
    )

    return {
        "window": {"start": _to_iso(start), "end": _to_iso(now)},
        "traffic_records": traffic_count,
        "avg_speed": _to_float(avg_speed),
        "events": {
            "total": total_events,
            "severe": severe_events,
        },
        "busiest_roads": [
            {"road_name": row.road_name, "avg_volume": _to_float(row.avg_volume)}
            for row in busiest_roads
        ],
    }


def get_alerts() -> Dict:
    summary = build_dashboard_summary()
    alerts = []
    if summary["active_events"] and summary["active_events"] > 8:
        alerts.append(
            {
                "level": "critical",
                "message": f"{summary['active_events']} active events detected. Consider dispatching additional operators.",
            }
        )
    avg_speed = summary.get("avg_speed_last_window")
    if avg_speed is not None and avg_speed < 25:
        alerts.append(
            {
                "level": "warning",
                "message": f"Average city speed dropped to {avg_speed:.1f} km/h in the last hour.",
            }
        )

    congested = summary.get("top_congested_roads") or []
    if congested:
        top = congested[0]
        if top.get("avg_congestion") and top["avg_congestion"] > 0.75:
            alerts.append(
                {
                    "level": "warning",
                    "message": f"Severe congestion on {top['road_name']} (avg index {top['avg_congestion']:.2f}).",
                }
            )

    return {"alerts": alerts, "summary": summary}


def get_map_events(limit: int = 50) -> List[Dict]:
    events = (
        Event.query.filter(Event.position.isnot(None))
        .order_by(Event.timestamp.desc())
        .limit(limit)
        .all()
    )
    results = []
    for event in events:
        coords = _parse_point_wkt(event.position)
        if not coords:
            continue
        payload = _serialize_event_row(event)
        payload["coordinates"] = coords
        results.append(payload)
    return results
