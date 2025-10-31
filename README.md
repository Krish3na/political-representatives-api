# Political Representatives API

REST API that provides information about US Congress members. Includes both Flask and Django REST Framework implementations running side by side.

## What it does

- Lists all current US Congress members (538+ legislators)
- Filter by state or party
- Get age statistics (average, youngest, oldest)
- Update notes about representatives
- Get live weather for state capitals
- Health check endpoint

## Flask vs Django

Both implementations provide identical endpoints and share the same PostgreSQL database.

**Flask API** (`flask-api/`)
- Micro-framework approach
- Simple, explicit code
- Runs on port 5000
- Uses Flask-SQLAlchemy for ORM

**Django API** (`django-api/`)
- Full framework with batteries included
- Django REST Framework for serialization
- Runs on port 8000
- Uses Django ORM
- Includes Django admin panel

Both use the same database schema and can run simultaneously.

## File Structure

```
Task-DE/
├── flask-api/
│   ├── app.py              # Flask application
│   ├── ingest_data.py      # Flask data ingestion script
│   ├── test_flask_api.py   # Test script
│   ├── requirements.txt    # Flask dependencies
│   └── Dockerfile
├── django-api/
│   ├── legislators_api/    # Django project
│   ├── legislators/        # Django app (models, views, serializers)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── management/commands/ingest_legislators.py
│   ├── test_django_api.py  # Test script
│   ├── requirements.txt    # Django dependencies
│   └── Dockerfile
├── docker-compose.yml      # Orchestrates all services
├── init.sql                # Database schema
└── README.md
```

## Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repo)

### Environment Variables

Create a `.env` file in the project root:

```
WEATHER_API_KEY=your_openweathermap_api_key
POSTGRES_DB=legislators_db
POSTGRES_USER=legislators_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://legislators_user:your_secure_password@db:5432/legislators_db

# Optional: CSV URL override
LEGISLATORS_CSV_URL=https://unitedstates.github.io/congress-legislators/legislators-current.csv
```

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Task-DE

# Start database
docker-compose up db -d

# Load data (choose one method)
# Flask ingestion:
docker-compose --profile data-load run --rm data_ingestion

# OR Django ingestion:
docker-compose up django-api -d
docker-compose exec django-api python manage.py migrate legislators --fake-initial
docker-compose exec django-api python manage.py ingest_legislators --truncate

# Start APIs
docker-compose up flask-api -d
docker-compose up django-api -d

# Test endpoints
python flask-api/test_flask_api.py    # Test Flask API (port 5000)
python django-api/test_django_api.py  # Test Django API (port 8000)
```

## Data Ingestion

Both implementations include their own ingestion scripts:

**Flask**: `ingest_data.py`
- Downloads CSV from GitHub
- Uses Flask app context
- Run via Docker: `docker-compose --profile data-load run --rm data_ingestion`

**Django**: Management command `ingest_legislators`
- Same CSV source
- Django ORM approach
- Run: `docker-compose exec django-api python manage.py ingest_legislators --truncate`

Both scripts truncate existing data and reload fresh records from the official source.

## API Endpoints

Both APIs expose identical endpoints:

- `GET /health` or `/api/health/` - Health check
- `GET /api/legislators` - List all (filter: `?state=CA&party=Democrat`)
- `GET /api/legislators/{id}` - Get specific legislator
- `PATCH /api/legislators/{id}/notes` - Update notes
- `GET /api/stats/age` - Age statistics
- `GET /api/legislators/{id}/weather` - Weather for state capital

**Flask API**: http://localhost:5000  
**Django API**: http://localhost:8000

## Common Commands

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f flask-api
docker-compose logs -f django-api
docker-compose logs -f db

# Stop everything
docker-compose down

# Stop and remove database data
docker-compose down -v

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

## Database

PostgreSQL runs in a container and persists data in a Docker volume. The schema is defined in `init.sql` and includes indexes on state, party, type, and birthday for better query performance.

Both APIs connect to the same database, so data loaded by either ingestion script is available to both.
