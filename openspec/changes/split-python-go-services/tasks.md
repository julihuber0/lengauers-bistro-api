## 1. Python Sync Script Setup

- [x] 1.1 Create scripts/ directory if it doesn't exist
- [x] 1.2 Create scripts/sync_menu.py as standalone executable script
- [x] 1.3 Add shebang and make script executable (chmod +x)
- [x] 1.4 Update requirements.txt to remove FastAPI, uvicorn, apscheduler dependencies
- [x] 1.5 Keep necessary dependencies: pdfplumber, requests, SQLAlchemy, psycopg2-binary, python-dotenv

## 2. Python Sync Script - Database Configuration

- [x] 2.1 Implement environment variable reading for DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- [x] 2.2 Add validation to ensure all required database env vars are present
- [x] 2.3 Create database connection function using SQLAlchemy with individual env vars
- [x] 2.4 Add error handling for missing database credentials (exit with non-zero code)

## 3. Python Sync Script - PDF Parsing Logic

- [x] 3.1 Import existing PDFParserService from src/services/pdf_parser.py
- [x] 3.2 Import existing MenuItem model from src/database/models.py
- [x] 3.3 Implement PDF_URL environment variable with default fallback
- [x] 3.4 Add PDF download and parsing using PDFParserService.parse_pdf_from_url()
- [x] 3.5 Add error handling for PDF download failures (exit with non-zero code)
- [x] 3.6 Add error handling for missing date in PDF (exit with non-zero code)
- [x] 3.7 Add error handling for no menu items found (exit with non-zero code)

## 4. Python Sync Script - Database Insertion

- [x] 4.1 Implement database insertion logic (check for existing items by date + name)
- [x] 4.2 Skip duplicate menu items and log count of skipped items
- [x] 4.3 Insert new menu items and log count of items added
- [x] 4.4 Commit transaction and handle database errors

## 5. Python Sync Script - Logging and Output

- [x] 5.1 Add logging configuration (console output to stdout/stderr)
- [x] 5.2 Log PDF URL being downloaded
- [x] 5.3 Log date extracted from PDF
- [x] 5.4 Log number of items parsed
- [x] 5.5 Log number of items added to database
- [x] 5.6 Log number of items skipped (duplicates)
- [x] 5.7 Log errors with descriptive messages
- [x] 5.8 Exit with code 0 on success, non-zero on failure

## 6. Go Project Setup

- [x] 6.1 Initialize Go module in project root (go mod init)
- [x] 6.2 Create cmd/api/ directory structure
- [x] 6.3 Create cmd/api/main.go as entry point
- [x] 6.4 Add gin-gonic dependency (go get github.com/gin-gonic/gin)
- [x] 6.5 Add PostgreSQL driver dependency (go get github.com/jackc/pgx/v5)
- [x] 6.6 Create internal/database/ directory for database code
- [x] 6.7 Create internal/handlers/ directory for HTTP handlers
- [x] 6.8 Create internal/models/ directory for data models

## 7. Go API - Database Layer

- [x] 7.1 Create database connection pool in internal/database/db.go
- [x] 7.2 Implement environment variable reading for DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- [x] 7.3 Add connection pool configuration (max connections, idle connections)
- [x] 7.4 Implement graceful connection close on shutdown
- [x] 7.5 Add error handling for missing database configuration
- [x] 7.6 Create MenuItem struct in internal/models/menu.go matching database schema

## 8. Go API - Database Queries

- [x] 8.1 Implement GetMenuByDate(date string) query in internal/database/queries.go
- [x] 8.2 Implement GetAllDatesWithMenu() query in internal/database/queries.go
- [x] 8.3 Add error handling for database query failures
- [x] 8.4 Map database rows to MenuItem structs

## 9. Go API - HTTP Handlers

- [x] 9.1 Create health check handler at GET /api/health
- [x] 9.2 Create menu retrieval handler at GET /api/menu
- [x] 9.3 Implement date parameter parsing and validation
- [x] 9.4 Return 400 Bad Request for invalid date format
- [x] 9.5 Return 404 Not Found when no menu exists for date
- [x] 9.6 Return 400 Bad Request for missing date parameter
- [x] 9.7 Create available dates handler at GET /api/menu/dates
- [x] 9.8 Create root endpoint handler at GET /
- [x] 9.9 Format responses as JSON matching existing API contract

## 10. Go API - Server Configuration

- [x] 10.1 Implement environment variable reading for API_HOST and API_PORT
- [x] 10.2 Set defaults (0.0.0.0:8000) when env vars not provided
- [x] 10.3 Initialize gin router with middleware
- [x] 10.4 Add CORS middleware configuration
- [x] 10.5 Register all route handlers
- [x] 10.6 Implement graceful shutdown on SIGTERM/SIGINT

## 11. Go API - Logging

- [x] 11.1 Add structured logging library (go get github.com/rs/zerolog)
- [x] 11.2 Configure zerolog for console output
- [x] 11.3 Add request logging middleware (method, path, status, duration)
- [x] 11.4 Add error logging with context
- [x] 11.5 Log server startup and shutdown events

## 12. Testing and Validation

- [x] 12.1 Test Python sync script with environment variables
- [x] 12.2 Test Python sync script downloads and parses PDF correctly
- [x] 12.3 Test Python sync script inserts items into database
- [x] 12.4 Test Python sync script handles duplicates correctly
- [x] 12.5 Test Python sync script error handling (missing env vars, download failures)
- [x] 12.6 Test Go API server starts and listens on configured port
- [x] 12.7 Test GET /api/health returns correct response
- [x] 12.8 Test GET /api/menu?date=YYYY-MM-DD returns menu items
- [x] 12.9 Test GET /api/menu with invalid date returns 400
- [x] 12.10 Test GET /api/menu with non-existent date returns 404
- [x] 12.11 Test GET /api/menu/dates returns available dates
- [x] 12.12 Test Go API graceful shutdown

## 13. Documentation and Cleanup

- [x] 13.1 Update README.md with new architecture (Python script + Go API)
- [x] 13.2 Document environment variables for Python script
- [x] 13.3 Document environment variables for Go API
- [x] 13.4 Add example cronjob configuration for sync script
- [x] 13.5 Update API endpoints documentation (remove POST /api/menu/sync)
- [x] 13.6 Create .env.example with new environment variable format
- [x] 13.7 Remove old Python API code from src/ directory
- [x] 13.8 Update Dockerfile if present to build Go application
- [x] 13.9 Update docker-compose files if present

## 14. Deployment Preparation

- [x] 14.1 Create example systemd service file for Go API (if deploying on Linux)
- [x] 14.2 Create example cronjob entry for sync script
- [x] 14.3 Add migration notes for breaking changes (POST endpoint removal)
- [x] 14.4 Test full deployment flow (sync script + API server)
