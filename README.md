# Lengauer's Bistro API

A RESTful API service that automatically fetches, parses, and serves the daily menu from Lengauer's Bistro.

## Features

- 📄 Automatic PDF parsing from the bistro's website
- 🔄 Periodic synchronization (configurable interval)
- 🗄️ PostgreSQL database storage
- 🚀 FastAPI REST API
- 📅 Query menu by date
- 🏥 Health check endpoints

## Project Structure

```
lengauers-bistro-api/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py              # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy models
│   │   └── database.py        # Database connection
│   └── services/
│       ├── __init__.py
│       ├── pdf_parser.py      # PDF parsing logic
│       └── menu_service.py    # Business logic
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**

   ```bash
   # Create database
   createdb lengauers_bistro

   # Or using psql:
   psql -U postgres
   CREATE DATABASE lengauers_bistro;
   \q
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

   Key configuration options:
   - `DATABASE_URL`: PostgreSQL connection string
   - `PDF_URL`: URL of the menu PDF (default: https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf)
   - `SYNC_INTERVAL_HOURS`: How often to check for new menus (default: 6)
   - `API_HOST`: API host (default: 0.0.0.0)
   - `API_PORT`: API port (default: 8000)

### Running the Application

**Development mode:**

```bash
python -m src.main
```

**Production mode:**

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
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

### Manual Sync

```http
POST /api/menu/sync
```

Manually trigger a PDF download and parse operation.

**Response:**

```json
{
  "success": true,
  "date": "2026-02-03",
  "items_found": 6,
  "items_added": 6,
  "already_existed": false
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
  "timestamp": "2026-02-03T10:30:00"
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

1. **Startup**: The application initializes the database and performs an initial PDF sync
2. **Scheduled Sync**: Every N hours (configured via `SYNC_INTERVAL_HOURS`), the app:
   - Downloads the PDF from the configured URL
   - Parses the date and menu items
   - Checks if the menu for that date already exists in the database
   - If not, adds all menu items to the database
3. **API Requests**: Clients can query the menu for specific dates via the REST API

## Development

### Running Tests (if implemented)

```bash
pytest
```

### Code Structure

- **config.py**: Centralized configuration using environment variables
- **models.py**: SQLAlchemy database models
- **database.py**: Database connection and session management
- **pdf_parser.py**: PDF downloading and parsing logic
- **menu_service.py**: Business logic for menu operations
- **routes.py**: FastAPI route definitions
- **main.py**: Application initialization and scheduler setup

## Environment Variables Reference

| Variable            | Default                                                        | Description                  |
| ------------------- | -------------------------------------------------------------- | ---------------------------- |
| DATABASE_URL        | postgresql://postgres:postgres@localhost:5432/lengauers_bistro | PostgreSQL connection string |
| PDF_URL             | https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf  | Source PDF URL               |
| SYNC_INTERVAL_HOURS | 6                                                              | Sync frequency in hours      |
| API_HOST            | 0.0.0.0                                                        | API server host              |
| API_PORT            | 8000                                                           | API server port              |

## License

MIT

## Contributing

Feel free to submit issues or pull requests!
