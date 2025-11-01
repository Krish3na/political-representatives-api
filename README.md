# Political Representatives API

REST API for US Congress members data. Two implementations - Flask and Django - running independently with separate databases.

## Features

- List all Congress members (538+ legislators)
- Filter by state or party
- Age statistics (average, youngest, oldest)
- Update notes for representatives
- Weather data for state capitals
- Health check endpoint

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd Task-DE
cp environment-variables.txt .env

# Edit .env and add your OpenWeatherMap API key
# WEATHER_API_KEY=your_key_here
# WEATHER_API_URL=http://api.openweathermap.org/data/2.5/weather

# Start database
docker-compose up -d db
```

## Flask API

**Port:** 5001  
**Database:** `flask_legislators_db` (table created by SQL script)

```bash
# Start
docker-compose up -d flask-api

# Load data
docker-compose --profile data-load run --rm data_ingestion

# Test
python flask-api/test_flask_api.py

# Useful commands
docker-compose logs -f flask-api
docker-compose restart flask-api
docker-compose exec db psql -U postgres -d flask_legislators_db
```

## Django API

**Port:** 8001  
**Database:** `django_legislators_db` (table created by migrations)

```bash
# Start
docker-compose up -d django-api

# Run migrations (first time only)
docker-compose exec django-api python manage.py migrate

# Load data
docker-compose exec django-api python manage.py ingest_legislators --truncate

# Test
python django-api/test_django_api.py

# Useful commands
docker-compose logs -f django-api
docker-compose restart django-api
docker-compose exec django-api python manage.py shell
docker-compose exec db psql -U postgres -d django_legislators_db
```

## Running Both

```bash
docker-compose up -d
docker-compose exec django-api python manage.py migrate
docker-compose --profile data-load run --rm data_ingestion
docker-compose exec django-api python manage.py ingest_legislators --truncate
```

## API Endpoints

- `GET /health` (Flask) or `/api/health/` (Django)
- `GET /api/legislators` - List all (`?state=CA&party=Democrat`)
- `GET /api/legislators/{id}`
- `PATCH /api/legislators/{id}/notes`
- `GET /api/stats/age`
- `GET /api/legislators/{id}/weather`

**Base URLs:**
- Flask: http://localhost:5001
- Django: http://localhost:8001

## Database Setup

Both APIs use the same PostgreSQL container but different databases:
- Flask: `flask_legislators_db` (created by `shared/flask_init.sql`)
- Django: `django_legislators_db` (created by `shared/django_init.sql`, table via migrations)

Same credentials from `.env` file.

## Common Commands

```bash
docker-compose ps
docker-compose logs -f
docker-compose down
docker-compose down -v  # Remove volumes
docker-compose build --no-cache
docker-compose exec db psql -U postgres
```

## Troubleshooting

**Django needs migrations:**
```bash
docker-compose exec django-api python manage.py migrate
```

**Flask/Django won't start:**
- Check database is running: `docker-compose ps db`
- Check `.env` has correct variables
- Check logs: `docker-compose logs flask-api` or `docker-compose logs django-api`
