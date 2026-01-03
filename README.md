# Urban Traffic Status Inquiry System

An enterprise-grade urban traffic management system with real-time monitoring, event tracking, and comprehensive analytics. Built with Flask, featuring modern security practices, caching, WebSocket support, and data export capabilities.

## Features

### Core Features
- **Live Dashboard**: Real-time traffic monitoring with hero banner, alert center, summary cards, congestion leaderboard, interactive map, road snapshots, system monitor, and event timeline
- **Historical Analysis**: Time series traffic data visualization with event annotations using Chart.js
- **Event Management**: Create, track, and manage traffic events with severity levels and status tracking
- **Data Export**: Export traffic data and events to CSV or Excel formats with customizable date ranges
- **Real-time Updates**: WebSocket support for live traffic and event updates

### Technical Features
- **Security**: bcrypt password hashing, API input validation with Marshmallow schemas
- **Performance**: Redis caching, database indexing optimization, pagination support
- **Error Handling**: Comprehensive logging system and structured error responses
- **Testing**: pytest-based test suite with fixtures and coverage reporting
- **Configuration**: Environment-based configuration with python-dotenv

## Project Structure

```
database/
|-- app/                    # Main application folder
|   |-- __init__.py         # Application factory with logging and error handling
|   |-- models.py           # Database models with optimized indexes
|   |-- routes.py           # API routes and view endpoints
|   |-- services.py         # Business logic with caching
|   |-- schemas.py          # Marshmallow validation schemas
|   |-- websocket.py        # WebSocket event handlers
|   |-- export.py           # Data export utilities
|   |-- static/
|   |   |-- css/
|   |   |   `-- styles.css
|   |   `-- js/
|   |       |-- main.js     # Dashboard interactions
|   |       |-- events.js   # Event Studio logic
|   |       `-- utils.js    # Frontend utilities (debounce, pagination)
|   `-- templates/
|       |-- base.html
|       |-- index.html      # Dashboard
|       |-- events.html     # Event Studio
|       `-- auth.html       # Access portal
|-- data/
|   `-- generate_data.py    # Mock data generator
|-- tests/                  # Test suite
|   |-- __init__.py
|   |-- conftest.py         # pytest fixtures
|   |-- test_models.py      # Model tests
|   `-- test_api.py         # API endpoint tests
|-- config.py               # Configuration classes
|-- main.py                 # Application entry point
|-- requirements.txt        # Python dependencies
|-- pytest.ini              # pytest configuration
|-- .env.example            # Environment variables template
`-- traffic.db              # SQLite database file
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd database

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# For development, default values are sufficient
```

### 3. Database Setup

```bash
# Generate mock data and create the database
python data/generate_data.py
```

This creates:
- 10 demo users (password: `demo123`)
- 50 roads
- 5000 traffic data points
- 100 events

### 4. Run the Application

```bash
# Development mode (with WebSocket support)
python main.py

# Production mode (set environment variable first)
export FLASK_ENV=production
python main.py
```

### 5. Access the Application

Open your browser and navigate to:
- Dashboard: `http://127.0.0.1:5000/`
- Event Studio: `http://127.0.0.1:5000/events`
- API Documentation: See API Endpoints section below

## API Endpoints

### Core Endpoints

| Endpoint | Method(s) | Description | Parameters |
|----------|-----------|-------------|------------|
| `/api/roads` | GET | List all roads (cached) | - |
| `/api/roads/<road_id>` | GET | Road snapshot with 24h stats | - |
| `/api/traffic/latest` | GET | Latest traffic data with pagination | `limit`, `offset` |
| `/api/traffic/history/<road_id>` | GET | Historical traffic + events | `start`, `end` (ISO 8601) |
| `/api/events` | GET, POST | List/create events | `status`, `limit`, `offset` |
| `/api/events/map` | GET | Events with geo coordinates | `limit` |
| `/api/dashboard/summary` | GET | Dashboard stats (cached 1min) | - |
| `/api/system/status` | GET | System health and counts | - |
| `/api/reports/weekly` | GET | 7-day aggregated report | - |
| `/api/alerts` | GET | Auto-generated alerts | - |

### Export Endpoints (New)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/export/traffic/csv` | GET | Export traffic data as CSV | `start`, `end` |
| `/api/export/traffic/excel` | GET | Export traffic data as Excel | `start`, `end` |
| `/api/export/events/csv` | GET | Export events as CSV | `status` |

### Notes
- All timestamps use ISO 8601 format (e.g., `2024-01-15T10:30:00Z`)
- Pagination: Use `limit` and `offset` parameters for paginated endpoints
- Caching: Roads endpoint cached for 5 minutes, dashboard for 1 minute
- Validation: All POST requests validated with Marshmallow schemas

## Testing

Run the complete test suite:

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

Test coverage includes:
- Model tests (password hashing, relationships)
- API endpoint tests (CRUD operations, validation)
- Error handling tests

## WebSocket Real-time Updates

Connect to WebSocket for live updates:

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Subscribe to traffic updates
socket.emit('subscribe_traffic');

// Listen for updates
socket.on('traffic_update', (data) => {
    console.log('New traffic data:', data);
});

// Subscribe to specific road
socket.emit('subscribe_road', { road_id: 1 });

// Subscribe to events
socket.emit('subscribe_events');
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///traffic.db

# Cache (Redis)
CACHE_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Configuration Classes

- `DevelopmentConfig`: Debug mode, simple cache
- `ProductionConfig`: Optimized for production, requires SECRET_KEY
- `TestingConfig`: In-memory database, testing mode

## Performance Optimizations

### Implemented Optimizations

1. **Database Indexing**
   - Composite indexes on `road_id + timestamp`
   - Indexes on `status + timestamp` for filtering
   - Optimizes common query patterns

2. **Caching Layer**
   - Redis support for distributed caching
   - Roads list cached for 5 minutes
   - Dashboard summary cached for 1 minute

3. **API Pagination**
   - All list endpoints support `limit` and `offset`
   - Maximum page size: 100 items
   - Efficient data transfer

4. **Frontend Utilities**
   - Debounce and throttle functions
   - Client-side pagination controls
   - Lazy loading support

## Security Features

### Password Security
- bcrypt hashing with automatic salt generation
- Secure password verification
- No plain-text storage

### API Validation
- Marshmallow schemas for all inputs
- Type checking and range validation
- Sanitized error messages

### Error Handling
- Structured JSON error responses
- Comprehensive logging
- Automatic database rollback on errors

## Development

### Code Quality Tools

```bash
# Format code with black
black app/ tests/

# Lint with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/
```

### Adding New Features

1. Create models in `app/models.py`
2. Add business logic in `app/services.py`
3. Define validation schemas in `app/schemas.py`
4. Create routes in `app/routes.py`
5. Write tests in `tests/`

## Production Deployment

### Prerequisites
- Python 3.8+
- Redis server (for caching)
- Reverse proxy (nginx recommended)

### Deployment Steps

```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=<strong-random-key>

# Install production dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'

# With WebSocket support (using eventlet)
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 'app:create_app()'
```

## Mock Data Generation

Generate realistic demo data:

```bash
python data/generate_data.py
```

This creates:
- 10 users with role assignments
- 50 roads with geo coordinates
- 5000 traffic data points (7 days)
- 100 events across different severity levels

**Warning**: Clears all existing data. Only use in development!

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## Support

For issues and questions:
- Check the documentation
- Review existing issues
- Open a new issue with details
