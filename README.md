# Lengauer's Bistro API

A RESTful API service that fetches, parses, and serves the daily menu from Lengauer's Bistro.

## Architecture

The application is split into two independent components:

1. **Python Sync Script**: Standalone script that downloads, parses, and stores menu data from PDF
2. **Go REST API**: High-performance API server that serves menu queries

This architecture enables flexible deployment - the sync script can run via cronjob independently of the API server.

### Docker Compose Services

When running with Docker Compose, three services are orchestrated:

- **postgres**: PostgreSQL 18 database for menu storage
- **api**: Go REST API server (accessible on port 8000)
- **sync**: Python sync script that runs in a loop (fetches PDF every 6 hours)

All services communicate via a shared Docker network, with the database health-checked before dependent services start.

## Features

- 📄 PDF parsing from the bistro's website (Python)
- 🗄️ PostgreSQL database storage
- 🚀 High-performance Go REST API
- 📅 Query menu by date
- 🏥 Health check endpoints
- 🔄 Automatic sync script (runs every 6 hours in Docker)
- 🐳 Docker Compose for easy deployment

## Project Structure

```
lengauers-bistro-api/
├── scripts/
│   └── sync_menu.py           # Standalone Python sync script (self-contained)
├── cmd/
│   └── api/
│       └── main.go            # Go API server entry point
├── internal/
│   ├── database/
│   │   ├── db.go              # Database connection pool
│   │   └── queries.go         # Database queries
│   ├── handlers/
│   │   └── handlers.go        # HTTP request handlers
│   └── models/
│       └── menu.go            # Data models
├── requirements.txt           # Python dependencies (for sync script)
├── go.mod                     # Go module definition
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Quick Start (Docker - Recommended)

The easiest way to run this application is using Docker Compose, which sets up everything including the database.

### Prerequisites

- Docker and Docker Compose installed

### Running with Docker Compose

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd lengauers-bistro-api
   ```

2. **Start all services:**

   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Go REST API server (port 8000)
   - Python sync script (runs every 6 hours)

3. **Verify the API is running:**

   ```bash
   curl http://localhost:8000/api/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2026-03-27T00:00:00Z"
   }
   ```

4. **Query the menu:**

   ```bash
   # Get available dates
   curl http://localhost:8000/api/menu/dates

   # Get menu for a specific date
   curl "http://localhost:8000/api/menu?date=2026-03-27"
   ```

5. **Manually trigger a sync (optional):**

   ```bash
   docker-compose exec sync python3 /app/scripts/sync_menu.py
   ```

6. **View logs:**

   ```bash
   # All services
   docker-compose logs -f

   # Just the API
   docker-compose logs -f api

   # Just the sync script
   docker-compose logs -f sync
   ```

6. **Stop services:**

   ```bash
   docker-compose down
   ```

### Configuration

Edit `docker-compose.yml` to customize:
- Database credentials (under `postgres` service)
- PDF URL (under `sync` and `api` services)
- Sync interval (modify the `sleep 21600` in sync command - currently 6 hours)
- API port mapping

### Troubleshooting Docker Deployment

**Check if services are running:**
```bash
docker-compose ps
```

**View API logs:**
```bash
docker-compose logs api
```

**Check database connection:**
```bash
docker-compose exec postgres psql -U bistro_user -d lengauers_bistro -c "SELECT COUNT(*) FROM menu_items;"
```

**Restart a specific service:**
```bash
docker-compose restart api
# or
docker-compose restart sync
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Access the database directly:**
```bash
docker-compose exec postgres psql -U bistro_user -d lengauers_bistro
```

### Production Deployment

For production, use `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Manual Setup (Without Docker)

If you prefer to run the services directly on your host:

### Prerequisites

- Python 3.9+
- Go 1.21+
- PostgreSQL 12+

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Build Go API:**

   ```bash
   go build -o bin/api cmd/api/main.go
   ```

4. **Set up PostgreSQL database:**

   ```bash
   # Create database
   createdb lengauers_bistro

   # Or using psql:
   psql -U postgres
   CREATE DATABASE lengauers_bistro;
   \q
   ```

   The database schema will be created automatically by the sync script on first run.

5. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Environment Variables

#### Database Configuration (Required for both Python script and Go API)

| Variable      | Description                       | Example         |
| ------------- | --------------------------------- | --------------- |
| `DB_HOST`     | PostgreSQL host                   | `localhost`     |
| `DB_PORT`     | PostgreSQL port                   | `5432`          |
| `DB_USER`     | Database user                     | `bistro_user`   |
| `DB_PASSWORD` | Database password                 | `bistro_pass`   |
| `DB_NAME`     | Database name                     | `lengauers_bistro` |

#### Python Sync Script Configuration

| Variable  | Default                                                        | Description        |
| --------- | -------------------------------------------------------------- | ------------------ |
| `PDF_URL` | https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf  | Source PDF URL     |

#### Go API Configuration

| Variable   | Default   | Description     |
| ---------- | --------- | --------------- |
| `API_HOST` | 0.0.0.0   | API server host |
| `API_PORT` | 8000      | API server port |

### Running the Application

#### 1. Sync Menu Data (Python Script)

Run the sync script to download and parse the menu PDF:

```bash
python3 scripts/sync_menu.py
```

The script will:
- Download the PDF from the configured URL
- Parse the menu date and items
- Insert new items into the database (skipping duplicates)
- Exit with code 0 on success, non-zero on failure

**Running via Cronjob:**

Add to your crontab to run daily at 6 AM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed):
0 6 * * * cd /path/to/lengauers-bistro-api && /usr/bin/python3 scripts/sync_menu.py >> /var/log/menu-sync.log 2>&1
```

**Note:** When using Docker Compose, the sync script runs automatically every 6 hours. No cronjob setup needed.

#### 2. Start Go API Server

**Development mode:**

```bash
./bin/api
```

**With custom configuration:**

```bash
export API_HOST=localhost
export API_PORT=3000
./bin/api
```

**Production deployment (systemd):**

Create `/etc/systemd/system/lengauers-api.service`:

```ini
[Unit]
Description=Lengauer's Bistro API Server
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/lengauers-bistro-api
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_USER=bistro_user"
Environment="DB_PASSWORD=bistro_pass"
Environment="DB_NAME=lengauers_bistro"
Environment="API_HOST=0.0.0.0"
Environment="API_PORT=8000"
ExecStart=/opt/lengauers-bistro-api/bin/api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable lengauers-api
sudo systemctl start lengauers-api
sudo systemctl status lengauers-api
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Get Menu by Date

```http
GET /api/menu?date=2026-02-03
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Kartoffelcremesuppe",
    "category": "Gericht",
    "price": 3.2
  },
  {
    "id": 2,
    "name": "Currywurstpfanne mit Pommes",
    "category": "Gericht",
    "price": 6.9
  }
]
```

**Error Responses:**

- `400 Bad Request`: Invalid date format or missing date parameter
- `404 Not Found`: No menu found for the specified date

### Get Available Dates

```http
GET /api/menu/dates
```

**Response:**

```json
{
  "dates": ["2026-02-03", "2026-02-02"]
}
```

### Health Check

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T10:30:00Z"
}
```

### Root Endpoint

```http
GET /
```

**Response:**

```json
{
  "name": "Lengauer's Bistro API",
  "version": "2.0.0",
  "endpoints": {
    "health": "/api/health",
    "get_menu": "/api/menu?date=YYYY-MM-DD",
    "available_dates": "/api/menu/dates"
  }
}
```

## Database Schema

### menu_items table

| Column | Type    | Description         |
| ------ | ------- | ------------------- |
| id     | INTEGER | Primary key         |
| date   | DATE    | Menu date           |
| name   | STRING  | Dish name           |
| price  | FLOAT   | Dish price in euros |

**Constraints:**

- Unique constraint on (date, name) to prevent duplicates

## How It Works

1. **Sync Script Execution**: The Python script runs (manually or via cronjob):
   - Downloads the PDF from the configured URL
   - Parses the date and menu items using pdfplumber
   - Checks if menu items for that date already exist
   - Inserts only new items (skips duplicates)
   - Exits with appropriate status code

2. **API Requests**: The Go API server:
   - Maintains a connection pool to PostgreSQL
   - Serves read-only queries for menu data
   - Handles requests with structured logging
   - Gracefully shuts down on SIGTERM/SIGINT

## Migration from v1.0 (FastAPI)

**Breaking Changes:**

- ❌ `POST /api/menu/sync` endpoint removed
- ✅ Sync is now done via standalone script execution
- ✅ All GET endpoints remain compatible

**Migration Steps:**

1. Update environment variables from `DATABASE_URL` to individual `DB_*` variables
2. Replace FastAPI server with Go API server
3. Set up cronjob for `scripts/sync_menu.py` instead of relying on in-process scheduler
4. If you were using `POST /api/menu/sync`, replace with direct script execution

## Development

### Running Tests

```bash
# Test Python sync script (requires database)
./scripts/test_sync.sh

# Test Go API (requires database)
./scripts/test_api.sh
```

### Code Structure

**Python:**
- **scripts/sync_menu.py**: Standalone sync script (self-contained, includes all PDF parsing and database models)

**Go:**
- **cmd/api/main.go**: API server entry point with middleware and routing
- **internal/database/db.go**: Database connection pool management
- **internal/database/queries.go**: SQL queries for menu data
- **internal/handlers/handlers.go**: HTTP request handlers
- **internal/models/menu.go**: Data models and response formatting

## Environment Variables Reference

### Database (Required for both sync script and API)

| Variable      | Example              | Description                  |
| ------------- | -------------------- | ---------------------------- |
| DB_HOST       | localhost            | PostgreSQL host              |
| DB_PORT       | 5432                 | PostgreSQL port              |
| DB_USER       | bistro_user          | Database user                |
| DB_PASSWORD   | bistro_pass          | Database password            |
| DB_NAME       | lengauers_bistro     | Database name                |

### Python Sync Script

| Variable | Default                                                        | Description        |
| -------- | -------------------------------------------------------------- | ------------------ |
| PDF_URL  | https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf  | Source PDF URL     |

### Go API Server

| Variable   | Default   | Description     |
| ---------- | --------- | --------------- |
| API_HOST   | 0.0.0.0   | API server host |
| API_PORT   | 8000      | API server port |
| GIN_MODE   | release   | Gin mode (debug/release) |

## License

MIT

## Contributing

Feel free to submit issues or pull requests!
