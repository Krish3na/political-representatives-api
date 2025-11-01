# Political Representatives API

REST API that provides information about US Congress members. Includes both Flask and Django REST Framework implementations running side by side with separate databases.

## What it does

- Lists all current US Congress members (538+ legislators)
- Filter by state or party
- Get age statistics (average, youngest, oldest)
- Update notes about representatives
- Get live weather for state capitals
- Health check endpoint

## Flask vs Django

Both implementations provide identical endpoints but use separate databases for complete independence.

**Flask API** (`flask-api/`)
- Micro-framework approach
- Simple, explicit code
- Runs on port 5001 (default)
- Uses Flask-SQLAlchemy for ORM
- Database: `flask_legislators_db` (created via SQL init script)
- Table managed by SQL script

**Django API** (`django-api/`)
- Full framework with batteries included
- Django REST Framework for serialization
- Runs on port 8001 (default)
- Uses Django ORM
- Database: `django_legislators_db` (created via SQL init script)
- Table managed by Django migrations

Both run simultaneously and independently - no dependencies between them.

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
├── docker-compose.yml          # Orchestrates all services
├── environment-variables.txt     # Environment variables template
├── shared/
│   ├── flask_init.sql          # Flask database initialization
│   └── django_init.sql         # Django database initialization
└── README.md
```

## Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repo)

### Environment Variables

Create `.env` file by copying `environment-variables.txt`:
```bash
cp environment-variables.txt .env
```

Update `WEATHER_API_KEY` with your OpenWeatherMap API key. All other default values are ready to use.

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Task-DE

# Copy environment variables
cp environment-variables.txt .env
# Edit .env and update WEATHER_API_KEY with your OpenWeatherMap API key

# Start database (required for both implementations)
docker-compose up -d db
```

## Flask Implementation

### Setup Flask API

```bash
# Start Flask API
docker-compose up -d flask-api

# Check Flask is running
docker-compose ps flask-api

# View Flask logs
docker-compose logs -f flask-api
```

### Load Data into Flask Database

```bash
# Ingest data into Flask database
docker-compose --profile data-load run --rm data_ingestion

# Verify data loaded
docker-compose exec db psql -U postgres -d flask_legislators_db -c "SELECT COUNT(*) FROM legislators;"
```

### Test Flask API

```bash
# Run test script
python flask-api/test_flask_api.py

# Or test manually
curl http://localhost:5001/health
curl http://localhost:5001/api/legislators
```

### Flask API Commands

```bash
# Start Flask API
docker-compose up -d flask-api

# Stop Flask API
docker-compose stop flask-api

# Restart Flask API
docker-compose restart flask-api

# View logs
docker-compose logs -f flask-api

# Rebuild Flask container (after code changes)
docker-compose build flask-api
docker-compose up -d flask-api

# Access Flask database
docker-compose exec db psql -U postgres -d flask_legislators_db
```

## Django Implementation

### Setup Django API

```bash
# Start Django API
docker-compose up -d django-api

# Run migrations (creates legislators table)
docker-compose exec django-api python manage.py migrate

# Check Django is running
docker-compose ps django-api

# View Django logs
docker-compose logs -f django-api
```

### Load Data into Django Database

```bash
# Ingest data into Django database
docker-compose exec django-api python manage.py ingest_legislators --truncate

# Verify data loaded
docker-compose exec db psql -U postgres -d django_legislators_db -c "SELECT COUNT(*) FROM legislators;"
```

### Test Django API

```bash
# Run test script
python django-api/test_django_api.py

# Or test manually
curl http://localhost:8001/api/health/
curl http://localhost:8001/api/legislators/
```

### Django API Commands

```bash
# Start Django API
docker-compose up -d django-api

# Stop Django API
docker-compose stop django-api

# Restart Django API
docker-compose restart django-api

# View logs
docker-compose logs -f django-api

# Run migrations
docker-compose exec django-api python manage.py migrate

# Check migration status
docker-compose exec django-api python manage.py showmigrations

# Rebuild Django container (after code changes)
docker-compose build django-api
docker-compose up -d django-api

# Access Django database
docker-compose exec db psql -U postgres -d django_legislators_db

# Access Django shell
docker-compose exec django-api python manage.py shell
```

## Running Both Implementations

```bash
# Start everything (database, Flask, Django)
docker-compose up -d

# Setup Django (migrations only needed once)
docker-compose exec django-api python manage.py migrate

# Load data for both
docker-compose --profile data-load run --rm data_ingestion
docker-compose exec django-api python manage.py ingest_legislators --truncate

# Test both
python flask-api/test_flask_api.py
python django-api/test_django_api.py
```

## API Endpoints

Both APIs expose identical endpoints:

- `GET /health` (Flask) or `GET /api/health/` (Django) - Health check
- `GET /api/legislators` - List all (filter: `?state=CA&party=Democrat`)
- `GET /api/legislators/{id}` - Get specific legislator
- `PATCH /api/legislators/{id}/notes` - Update notes
- `GET /api/stats/age` - Age statistics
- `GET /api/legislators/{id}/weather` - Weather for state capital

**Flask API**: http://localhost:5001  
**Django API**: http://localhost:8001

## Database Architecture

- **Single PostgreSQL container** shared by both APIs
- **Two separate databases**:
  - `flask_legislators_db` - Flask's database
  - `django_legislators_db` - Django's database
- **Same credentials**: Both use `POSTGRES_USER` and `POSTGRES_PASSWORD` from `.env`
- **Independent operation**: Each API manages its own database completely

### Database Initialization

- `shared/flask_init.sql` - Creates Flask database and table on container startup
- `shared/django_init.sql` - Creates Django database on container startup (table created by migrations)

### Django Migrations

Django manages its table via migrations (not SQL scripts):
```bash
# Create tables
docker-compose exec django-api python manage.py migrate

# Check migration status
docker-compose exec django-api python manage.py showmigrations
```

## Common Commands

```bash
# Check all running containers
docker-compose ps

# View all logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove database data (fresh start)
docker-compose down -v

# Rebuild all services after code changes
docker-compose build --no-cache
docker-compose up -d

# View database container logs
docker-compose logs -f db

# Access PostgreSQL shell
docker-compose exec db psql -U postgres
```

## Troubleshooting

**Django migrations not running:**
```bash
docker-compose exec django-api python manage.py migrate
```

**Tables don't exist:**
- Flask: Check that `flask_init.sql` ran (should create table automatically)
- Django: Run migrations manually

**Connection errors:**
- Ensure database container is healthy: `docker-compose ps db`
- Check environment variables in `.env` file
- Verify database names match: `flask_legislators_db` and `django_legislators_db`
