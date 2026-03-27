# Lengauer's Bistro API - Developer Guide

## Project Overview

A FastAPI service that automatically fetches and parses daily menus from Lengauer's Bistro PDF, stores them in PostgreSQL, and serves them via REST API. The service runs a background scheduler that periodically syncs the menu.

## Build, Test, and Run

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL required)
createdb lengauers_bistro

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Running
```bash
# Development mode (with auto-reload)
python -m src.main

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Start both API and PostgreSQL
docker-compose up

# Production deployment
docker-compose -f docker-compose.prod.yml up
```

### Testing
```bash
# Run tests (if implemented)
pytest

# Run specific test file
pytest tests/test_menu_service.py
```

## Architecture

### Application Lifecycle
1. **Startup** (`main.py` lifespan):
   - Initialize database tables via SQLAlchemy
   - Perform initial PDF sync
   - Start APScheduler background job (runs every N hours based on `SYNC_INTERVAL_HOURS`)

2. **Scheduled Sync** (background job):
   - Downloads PDF from configured URL
   - Parses date and menu items using pdfplumber
   - Only adds new items (checks for duplicates by date+name)
   - Logs sync status

3. **API Request Handling**:
   - FastAPI routes use dependency injection for DB sessions
   - MenuService handles business logic
   - Database sessions auto-commit/rollback via context managers

### Two DB Session Patterns
- **`get_db()`**: Context manager for use in background jobs/scripts
  ```python
  with get_db() as db:
      service = MenuService(db)
  ```

- **`get_db_session()`**: FastAPI dependency injection for routes
  ```python
  def endpoint(db: Session = Depends(get_db_session)):
  ```

### PDF Parsing Strategy
The PDF parser (`pdf_parser.py`) handles multi-line dish names that span across lines:
- Accumulates text lines until a price pattern is found
- Handles hyphenated words at line breaks
- Filters out header text and keywords (e.g., "Tageskarte", "Desserts")
- Supports multiple price formats: `€12.50`, `12,50 €`, `EUR 12.50`

## Code Conventions

### Database Models
- Use SQLAlchemy 2.0 `Mapped` typing annotations
- `to_dict()` method on models for API response serialization
- Unique constraints defined in `__table_args__`
- Example:
  ```python
  class MenuItem(Base):
      id: Mapped[int] = mapped_column(Integer, primary_key=True)
      date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
  ```

### Service Layer Pattern
- Business logic lives in `src/services/`
- Services accept SQLAlchemy Session in `__init__`
- Services handle database operations and external integrations
- Routes delegate to services, keeping route handlers thin

### Error Handling
- Services return dictionaries with `success` boolean and error messages
- Routes raise `HTTPException` with appropriate status codes
- Background jobs log errors but don't crash the scheduler

### Configuration
- All config via environment variables loaded in `config.py`
- Single `Config` class with class attributes
- Exported as singleton: `config = Config()`

### Logging
- Use Python's standard `logging` module
- Log important events: startup, sync results, errors
- Background jobs log to stdout (captured by Docker/systemd)

## Database Schema

### menu_items
| Column | Type  | Constraints                     |
|--------|-------|---------------------------------|
| id     | INT   | Primary key, auto-increment     |
| date   | DATE  | Not null, indexed               |
| name   | STR   | Not null                        |
| price  | FLOAT | Not null                        |

**Unique constraint**: `(date, name)` - prevents duplicate dishes on same day

## API Endpoints

| Method | Path              | Purpose                          |
|--------|-------------------|----------------------------------|
| GET    | /api/menu         | Get menu by date (`?date=YYYY-MM-DD`) |
| GET    | /api/menu/dates   | List all available menu dates    |
| POST   | /api/menu/sync    | Manually trigger PDF sync        |
| GET    | /api/health       | Health check                     |
| GET    | /                 | Root with API documentation      |

## Environment Variables

| Variable            | Default                                                        | Description                  |
|---------------------|----------------------------------------------------------------|------------------------------|
| DATABASE_URL        | postgresql://postgres:postgres@localhost:5432/lengauers_bistro | PostgreSQL connection string |
| PDF_URL             | https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf  | Source PDF URL               |
| SYNC_INTERVAL_HOURS | 6                                                              | Background sync frequency    |
| API_HOST            | 0.0.0.0                                                        | API server bind address      |
| API_PORT            | 8000                                                           | API server port              |

## Common Tasks

### Adding a New Endpoint
1. Add route function in `src/api/routes.py`
2. Use `@router.get/post()` decorator with `/api` prefix (already set)
3. Inject DB session: `db: Session = Depends(get_db_session)`
4. Delegate business logic to `MenuService` or create new service

### Adding Database Migrations
Currently using SQLAlchemy's `create_all()` for simple schema. For migrations:
1. Alembic is installed (`requirements.txt`)
2. Initialize: `alembic init alembic`
3. Configure `alembic.ini` with `DATABASE_URL`
4. Generate migration: `alembic revision --autogenerate -m "description"`
5. Apply: `alembic upgrade head`

### Modifying PDF Parser
- Edit `src/services/pdf_parser.py`
- Test with actual PDF: `PDFParserService.parse_pdf_from_url(url)`
- Adjust regex patterns in `parse_menu_items()` for different layouts
- Update `skip_keywords` list to filter unwanted sections

### Changing Sync Interval
- Set `SYNC_INTERVAL_HOURS` in `.env` or environment
- Restart application for change to take effect
- Or trigger manual sync: `POST /api/menu/sync`
