## Why

The current monolithic FastAPI application tightly couples PDF parsing, scheduled syncing, and the REST API. This architecture makes it difficult to run the sync logic independently (e.g., as a cronjob) and limits language choice for performance-critical API serving. Splitting into separate services enables better deployment flexibility, clearer separation of concerns, and the ability to leverage Go's performance for the API layer.

## What Changes

- **BREAKING**: Remove the `POST /api/menu/sync` endpoint from the API (manual sync will be handled via direct script execution)
- **BREAKING**: Replace FastAPI-based REST API with a Go-based API using gin-gonic framework
- Split PDF fetching/parsing into a standalone Python script that can be executed independently
- Remove background scheduler (APScheduler) from the application - sync will be handled externally via cronjob
- Change database credential configuration to use environment variables (instead of DATABASE_URL)
- Maintain existing GET endpoints: `/api/menu`, `/api/menu/dates`, `/api/health`
- Keep the same database schema and menu data structure

## Capabilities

### New Capabilities
- `python-sync-script`: Standalone Python script for PDF downloading, parsing, and database insertion
- `go-rest-api`: Go-based REST API server using gin-gonic for menu retrieval

### Modified Capabilities
- `menu-retrieval`: Existing menu query functionality reimplemented in Go (same API contract, different implementation)

## Impact

**Code:**
- Remove: `src/main.py`, `src/api/routes.py`, all FastAPI-related code
- Remove: Background scheduler and lifespan management
- Remove: POST `/api/menu/sync` endpoint
- Add: Standalone Python script `scripts/sync_menu.py` (or similar)
- Add: Go application in `cmd/api/` with gin-gonic server
- Keep: `src/database/models.py`, `src/services/pdf_parser.py` (for use in standalone script)

**APIs:**
- Remove POST `/api/menu/sync` (breaking change for clients using manual sync)
- Keep GET `/api/menu?date=YYYY-MM-DD`
- Keep GET `/api/menu/dates`
- Keep GET `/api/health`

**Dependencies:**
- Python: Remove FastAPI, uvicorn, APScheduler; Keep pdfplumber, requests, SQLAlchemy, psycopg2
- Go: Add gin-gonic, PostgreSQL driver (lib/pq or pgx)

**Deployment:**
- Python script will run via cronjob or manual execution
- Go API server runs as standalone service
- Database credentials configured via environment variables: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
