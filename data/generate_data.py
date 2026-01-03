import os
import random
import sys
from datetime import datetime, timedelta, timezone

from faker import Faker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Event, Road, TrafficData, User

STATUS_LABELS = ("SMOOTH", "MODERATE", "CONGESTED")
EVENT_TYPES = ("Accident", "Construction", "Congestion", "Control")


def _random_point(fake: Faker) -> str:
    lat = fake.latitude()
    lon = fake.longitude()
    return f"POINT({lon:.6f} {lat:.6f})"


def generate_mock_data(
    user_count: int = 10,
    road_count: int = 50,
    traffic_points: int = 5000,
    event_count: int = 100,
) -> None:
    """Generate mock data for the database."""
    fake = Faker()

    # Clean up existing data
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    # Generate Users
    users = []
    for _ in range(user_count):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role=random.choice(["admin", "operator", "user"]),
            phone=fake.phone_number(),
            password_hash="",  # Will be set by set_password
            salt="",
        )
        # Use bcrypt to hash password
        user.set_password("demo123")  # Default demo password
        users.append(user)
    db.session.add_all(users)
    db.session.commit()  # Commit users to get their IDs

    # Generate Roads
    roads = []
    for i in range(road_count):
        road = Road(
            name=f"{fake.street_name()} Road",
            code=f"R{i+1:04d}",
            start_point=_random_point(fake),
            end_point=_random_point(fake),
            geometry=(
                f"LINESTRING({fake.longitude():.4f} {fake.latitude():.4f}, "
                f"{fake.longitude():.4f} {fake.latitude():.4f})"
            ),
            length=round(random.uniform(0.5, 15.0), 2),
            lanes=random.randint(1, 6),
            level=random.randint(1, 4),
            speed_limit=random.choice([30, 40, 50, 60, 80, 100]),
        )
        roads.append(road)
    db.session.add_all(roads)
    db.session.commit()  # Commit roads to get their IDs

    # Generate Traffic Data
    traffic_rows = []
    now = datetime.now(timezone.utc)
    for _ in range(traffic_points):
        road = random.choice(roads)
        timestamp = now - timedelta(minutes=random.randint(1, 60 * 24 * 7))
        speed = round(random.uniform(5, road.speed_limit), 2)
        congestion_ratio = max(0.0, min(1.0, speed / road.speed_limit))
        congestion_level = round(1 - congestion_ratio, 2)
        status = STATUS_LABELS[0]
        if congestion_level >= 0.4:
            status = STATUS_LABELS[1]
        if congestion_level >= 0.7:
            status = STATUS_LABELS[2]

        traffic_rows.append(
            TrafficData(
                road_id=road.id,
                timestamp=timestamp,
                speed=speed,
                volume=random.randint(50, 800),
                status=status,
                congestion_level=congestion_level,
            )
        )

    if traffic_rows:
        db.session.bulk_save_objects(traffic_rows)
        db.session.commit()

    # Generate Events
    events = []
    for _ in range(event_count):
        event = Event(
            user_id=random.choice(users).id,
            road_id=random.choice(roads).id,
            type=random.choice(EVENT_TYPES),
            description=fake.sentence(),
            position=_random_point(fake),
            timestamp=now - timedelta(hours=random.randint(1, 72)),
            status="active",
            severity=random.randint(1, 3),
        )
        events.append(event)
    db.session.add_all(events)

    db.session.commit()
    print(
        f"Generated {user_count} users, {road_count} roads, "
        f"{traffic_points} traffic data points, and {event_count} events."
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created.")
        generate_mock_data()
