# Containerized Political Representatives API

## What is this project about?

This project is a web API that provides information about United States political representatives (Congress members). Think of it as a digital phone book for politicians, but much more powerful. You can search for representatives, get their details, and even check the weather in their state capitals.

## The Problem We're Solving

Imagine you're building a political app, a news website, or any application that needs information about US Congress members. Instead of manually maintaining a database of 538+ representatives, this API does the heavy lifting for you. It automatically downloads the latest data from official sources and provides it through easy-to-use web endpoints.

## What This API Does

Our API serves as a central hub for political representative data. It can:

- Show you all current US Congress members
- Find specific representatives by their ID
- Filter representatives by state or political party
- Calculate age statistics
- Update notes about representatives
- Get live weather data for state capitals
- Provide health status for monitoring

## Available API Endpoints

### 1. Health Check
**GET** `/health`
- **What it does**: Checks if the API is running properly
- **Expected output**: `{"status": "healthy", "timestamp": "2025-10-20T06:09:30.892890"}`

### 2. Get All Legislators
**GET** `/api/legislators`
- **What it does**: Returns a list of all current US Congress members
- **Optional filters**: `?state=CA` (filter by state), `?party=Democrat` (filter by party)
- **Expected output**: Array of legislator objects with details like name, party, state, age, etc.

### 3. Get Specific Legislator
**GET** `/api/legislators/{id}`
- **What it does**: Returns detailed information about one specific representative
- **Expected output**: Single legislator object with all their details

### 4. Update Legislator Notes
**PATCH** `/api/legislators/{id}/notes`
- **What it does**: Allows you to add or update notes about a specific representative
- **Body**: `{"notes": "Your note here"}`
- **Expected output**: Updated legislator object with confirmation message

### 5. Age Statistics
**GET** `/api/stats/age`
- **What it does**: Provides age statistics across all representatives
- **Expected output**: Average age, youngest and oldest representatives with their details

### 6. Weather Information
**GET** `/api/legislators/{id}/weather`
- **What it does**: Gets current weather for the state capital where the representative is from
- **Expected output**: Legislator details plus weather information (temperature, humidity, wind speed, description)

## Project File Structure

```
Task-DE/
├── app.py                    # Main Flask application with all API endpoints
├── ingest_data.py           # Script that downloads and loads data into database
├── test_api.py              # Test script to verify all endpoints work
├── requirements.txt         # Python dependencies
├── Dockerfile               # Instructions for building the API container
├── docker-compose.yml       # Orchestrates all services (database, API, data loading)
├── init.sql                 # Database setup script
├── environment-variables.txt # Template for environment variables
└── README.md               # This file
```

## What Each File Does

### app.py
This is the heart of our application. It contains:
- Flask web server setup
- Database connection configuration
- All API endpoint definitions
- Business logic for each endpoint
- Weather API integration

### ingest_data.py
This script handles data management:
- Downloads the latest legislator data from official sources
- Cleans and validates the data
- Loads it into our PostgreSQL database
- Handles errors and provides progress updates

### test_api.py
Our quality assurance tool:
- Tests all API endpoints automatically
- Verifies responses are correct
- Shows sample data from each endpoint
- Helps ensure everything works before deployment

### requirements.txt
Lists all Python packages needed:
- Flask for the web framework
- SQLAlchemy for database operations
- psycopg2 for PostgreSQL connection
- requests for external API calls
- gunicorn for production server

### Dockerfile
Instructions for building our API container:
- Starts with Python 3.11
- Installs system dependencies
- Copies our code
- Sets up a non-root user for security
- Configures the web server

### docker-compose.yml
Orchestrates our entire system:
- PostgreSQL database service
- Flask API service
- Data ingestion service
- Network configuration
- Volume management
- Environment variables

### init.sql
Database setup script:
- Creates the legislators table
- Defines all required columns
- Sets up indexes for better performance
- Ensures database is ready for data

## Understanding Docker

### What is Docker?
Docker is like a shipping container for software. Just like how shipping containers standardize how goods are transported, Docker standardizes how applications run. It packages your application with everything it needs to run, making it work the same way on any computer.

### What Does the Dockerfile Do?
The Dockerfile is like a recipe for building our API container:
1. Start with a Python base image
2. Install system tools we need
3. Copy our application code
4. Install Python dependencies
5. Create a secure user account
6. Set up the web server
7. Define how to start the application

### What Does docker-compose.yml Do?
Docker Compose is like a conductor for an orchestra. It coordinates multiple containers to work together:
- Starts the database first
- Waits for database to be ready
- Starts the API service
- Connects them through a network
- Manages shared storage
- Handles environment variables

## How to Get Started

### Step 1: Get the Code
```bash
# If you have git, clone the repository
git clone <repository-url>
cd Task-DE

# Or download and extract the zip file
# Then navigate to the Task-DE folder
```

### Step 2: Set Up Environment Variables
1. Copy the template file:
   ```bash
   cp environment-variables.txt .env
   ```

2. Edit the `.env` file and replace the dummy values:
   - `WEATHER_API_KEY`: Get a free API key from OpenWeatherMap
   - `DATABASE_URL`: Usually keep as is
   - `POSTGRES_PASSWORD`: Change to a secure password
   - Other values can stay as defaults

### Step 3: Build and Start Everything
```bash
# Build all containers and start services
docker-compose up --build -d
```

### Step 4: Load the Data
```bash
# Run the data ingestion to populate the database
docker-compose --profile data-load run --rm data_ingestion
```

### Step 5: Test the API
```bash
# Run the test script to verify everything works
python test_api.py
```

## Detailed Docker Commands

### Building and Starting Services
```bash
# Build and start all services in background
docker-compose up --build -d
```
**What this does**: Builds all containers from scratch and starts them in the background. The `-d` flag runs them detached (in background).

```bash
# Start only the database
docker-compose up db -d
```
**What this does**: Starts only the PostgreSQL database service, useful for debugging or when you only need the database.

```bash
# Start only the API
docker-compose up api -d
```
**What this does**: Starts only the Flask API service, useful when you want to restart just the API.

### Checking Status
```bash
# See all running containers
docker ps
```
**What this does**: Shows all currently running Docker containers with their status, ports, and names.

### Stopping and Cleaning Up
```bash
# Stop all services and remove volumes
docker-compose down --volumes --remove-orphans
```
**What this does**: Stops all services, removes the database data, and cleans up any orphaned containers.

```bash
# Remove specific images
docker rmi -f task-de-api task-de-data_ingestion
```
**What this does**: Forces removal of the API and data ingestion images, useful when you want to rebuild from scratch.

### Rebuilding
```bash
# Rebuild without using cache
docker-compose build --no-cache
```
**What this does**: Rebuilds all containers without using cached layers, ensuring you get the latest changes.

```bash
# Start services after rebuilding
docker-compose up -d
```
**What this does**: Starts all services after you've rebuilt the containers.

### Data Management
```bash
# Run data ingestion manually
docker-compose --profile data-load run --rm data_ingestion
```
**What this does**: Runs the data loading script manually, useful for reloading data or troubleshooting.

### Monitoring and Logs
```bash
# View API logs
docker-compose logs -f api
```
**What this does**: Shows real-time logs from the API service. Press Ctrl+C to stop viewing.

```bash
# View database logs
docker-compose logs -f db
```
**What this does**: Shows real-time logs from the database service.

```bash
# View all logs
docker-compose logs -f
```
**What this does**: Shows logs from all services simultaneously.

### Stopping Services
```bash
# Stop all services
docker-compose down
```
**What this does**: Stops all services but keeps the database data.

```bash
# Stop and remove volumes (deletes database data)
docker-compose down -v
```
**What this does**: Stops all services and permanently deletes the database data. Use with caution!

## Understanding the SQL File

The `init.sql` file sets up our database structure:

```sql
-- Creates the main table for storing legislator information
CREATE TABLE IF NOT EXISTS legislators (
    govtrack_id INTEGER PRIMARY KEY,  -- Unique identifier for each representative
    first_name VARCHAR(100),          -- Representative's first name
    last_name VARCHAR(100),           -- Representative's last name
    birthday DATE,                    -- Date of birth
    gender VARCHAR(10),               -- Gender (M/F)
    type VARCHAR(10),                 -- Type: 'sen' for Senator, 'rep' for Representative
    state VARCHAR(2),                 -- Two-letter state code
    district VARCHAR(10),             -- District number (for Representatives)
    party VARCHAR(50),                -- Political party
    url VARCHAR(500),                 -- Official website URL
    notes TEXT                        -- Custom notes field
);

-- Creates indexes for faster searching
CREATE INDEX IF NOT EXISTS idx_legislators_state ON legislators(state);
CREATE INDEX IF NOT EXISTS idx_legislators_party ON legislators(party);
CREATE INDEX IF NOT EXISTS idx_legislators_type ON legislators(type);
CREATE INDEX IF NOT EXISTS idx_legislators_birthday ON legislators(birthday);
```

## Using the Test API File

The `test_api.py` file is your quality assurance tool:

1. **Run it**: `python test_api.py`
2. **What it does**: Tests all 7 API endpoints automatically
3. **What you'll see**: 
   - Pass/fail status for each test
   - Sample JSON responses from each endpoint
   - Summary of all tests
4. **If tests fail**: Check the error messages and verify your services are running

## Environment Variables Setup

1. **Copy the template**:
   ```bash
   cp environment-variables.txt .env
   ```

2. **Edit the `.env` file** with your actual values:
   - `WEATHER_API_KEY`: Get from OpenWeatherMap (free)
   - `POSTGRES_PASSWORD`: Choose a secure password
   - Other values can stay as defaults

3. **Why we need these**: 
   - Weather API key for live weather data
   - Database credentials for security
   - Environment settings for production vs development

## Troubleshooting Common Issues

### "Connection refused" errors
- Make sure all services are running: `docker ps`
- Check if database is healthy: `docker-compose logs db`

### "No data" in API responses
- Run data ingestion: `docker-compose --profile data-load run --rm data_ingestion`
- Check if data was loaded: `docker-compose logs data_ingestion`

### "Weather API error"
- Verify your weather API key in the `.env` file
- Check if the API key is valid at OpenWeatherMap

### "Port already in use"
- Stop other services using port 5000 or 5432
- Or change ports in `docker-compose.yml`

## What's Next?

Once everything is running, you can:
1. **Explore the API**: Use tools like Postman or curl to test endpoints
2. **Build a frontend**: Create a web interface using the API
3. **Add features**: Extend the API with new endpoints
4. **Deploy**: Move to a cloud platform like AWS or Google Cloud
5. **Monitor**: Set up logging and monitoring for production use

This API provides a solid foundation for any application that needs political representative data. The containerized setup makes it easy to deploy anywhere, and the comprehensive test suite ensures reliability.