# Urban Traffic Status Inquiry System

This project is a demo of an urban traffic status inquiry system based on the provided design document. It exposes a small Flask API plus a modern dashboard + Event Studio built with Bootstrap, custom CSS, and Chart.js.

## Features

- Live dashboard with hero banner, alert center, summary cards, congestion leaderboard, interactive map, road snapshot, system monitor, and event timeline.
- Historical explorer overlays traffic time series with recorded events, powered by Chart.js annotations.
- Event Studio page to create new events, review history, and manage status/severity (demo access portal included for future RBAC integration).
- REST API covering roads, traffic feeds, dashboard summaries, road snapshots, alerts, system status, weekly reports, map feeds, and event CRUD.
- Mock data generator for quickly seeding SQLite with realistic demo data (users, roads, traffic, and events).

## Project Structure

```
.database/
|-- app/                  # Main application folder
|   |-- __init__.py       # Application factory
|   |-- models.py         # Database models
|   |-- routes.py         # API + view routes
|   |-- services.py       # Business logic helpers
|   |-- static/
|   |   |-- css/
|   |   |   `-- styles.css
|   |   `-- js/
|   |       |-- main.js   # Dashboard interactions
|   |       `-- events.js # Event Studio logic
|   `-- templates/
|       |-- base.html
|       |-- index.html    # Dashboard
|       |-- events.html   # Event Studio
|       `-- auth.html     # Access portal (demo)
|-- data/
|   `-- generate_data.py  # Script to generate mock data
|-- config.py             # Configuration file
|-- main.py               # Application entry point
|-- requirements.txt      # Python dependencies
|-- traffic.db            # SQLite database file
`-- 1.txt                 # Original design document
```

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate mock data and create the database:**
    ```bash
    python data/generate_data.py
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

4.  Open your browser and navigate to `http://127.0.0.1:5000`.

## API Endpoints

| Endpoint | Method(s) | Description |
| --- | --- | --- |
| `/api/roads` | GET | List all roads with metadata needed by the UI. |
| `/api/roads/<road_id>` | GET | Snapshot for a given road (latest reading + 24h averages + event counts). |
| `/api/traffic/latest?limit=10` | GET | Fetch the latest traffic samples (limit defaults to 10, max 100). |
| `/api/events` | GET, POST | Read events (filter by `status`, limit results) or create a new event. |
| `/api/events/map` | GET | Return events that include coordinates for the Leaflet map. |
| `/api/traffic/history/<road_id>` | GET | Retrieve traffic series plus events for a specific road and time window. |
| `/api/dashboard/summary` | GET | Aggregate stats for the summary widgets (totals, averages, congestion leaders). |
| `/api/system/status` | GET | Lightweight system monitor (record counts + latest ingested data). |
| `/api/reports/weekly` | GET | 7-day aggregated report for analytics/export workflows. |
| `/api/alerts` | GET | Derived alert center data (threshold-based warnings). |

All timestamps use ISO 8601 strings. When requesting history data you can pass `start` and `end` query parameters in ISO 8601 (the frontend uses `toISOString()`, so `Z`/UTC is accepted).

## Mock Data Generation

Use `data/generate_data.py` inside an application context to reset the SQLite database and seed users, roads, traffic points, and events:

```bash
python data/generate_data.py
```

You can tweak the amount of generated data by passing parameters to `generate_mock_data`. Each run clears existing tables, so only execute it in local/dev environments.
