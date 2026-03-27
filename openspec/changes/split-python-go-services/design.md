## Context

The current application is a monolithic FastAPI server that:
1. Serves REST API endpoints for menu retrieval
2. Downloads and parses PDF menus using pdfplumber
3. Runs a background scheduler (APScheduler) for periodic sync
4. Stores menu data in PostgreSQL

The application has become difficult to deploy flexibly - the PDF sync logic is tightly coupled to the API server, making it impossible to run sync independently (e.g., as a cronjob separate from the API server). Additionally, the current Python-based API could benefit from Go's performance characteristics and simpler deployment model.

**Current State:**
- Language: Python (FastAPI)
- PDF Parser: pdfplumber + requests
- Database: PostgreSQL via SQLAlchemy
- Scheduler: APScheduler (in-process)
- Endpoints: GET `/api/menu`, GET `/api/menu/dates`, POST `/api/menu/sync`, GET `/api/health`

**Constraints:**
- Must maintain same database schema (menu_items table)
- Must preserve existing menu data
- Must maintain API compatibility for GET endpoints
- Sync script must be executable independently via cronjob

## Goals / Non-Goals

**Goals:**
- Decouple PDF sync from API server into standalone Python script
- Reimplement REST API in Go using gin-gonic for better performance
- Enable flexible deployment (sync via cronjob, API as separate service)
- Use environment variables for all database credentials
- Maintain backward compatibility for GET endpoints

**Non-Goals:**
- Changing the database schema or menu data structure
- Adding new features or endpoints (only maintaining existing GET endpoints)
- Implementing authentication or authorization
- Supporting the POST `/api/menu/sync` endpoint (explicitly removed)

## Decisions

### 1. Split Architecture: Standalone Script + API Server

**Decision:** Create two independent components:
- Python script: `scripts/sync_menu.py` for PDF download/parse/insert
- Go API server: `cmd/api/main.go` for serving menu queries

**Rationale:**
- Allows sync to run on schedule (cronjob) independently of API server
- Enables horizontal scaling of API server without scheduler conflicts
- Simpler deployment model - each component has single responsibility
- Reduces memory footprint of API server (no PDF parsing dependencies)

**Alternatives Considered:**
- Microservices with message queue: Overkill for this simple use case
- Keep monolith, add cronjob endpoint: Still couples deployment, doesn't solve memory/dependency issues

### 2. Keep Python for Sync Script

**Decision:** Maintain Python for PDF parsing script (reuse existing `pdf_parser.py` and `menu_service.py`)

**Rationale:**
- pdfplumber is mature and works well for current PDF format
- Existing parsing logic is complex and well-tested
- No performance requirement for sync (runs once per day)
- Avoids rewriting working code

**Alternatives Considered:**
- Rewrite in Go: Requires finding Go PDF library and reimplementing parsing logic (high risk, low reward)

### 3. Use gin-gonic for Go API

**Decision:** Use gin-gonic web framework for the Go REST API

**Rationale:**
- Popular, mature framework with excellent documentation
- High performance with minimal overhead
- Simple routing and middleware support
- Similar ergonomics to FastAPI for endpoint definitions

**Alternatives Considered:**
- Standard library net/http: More verbose, missing convenient features
- Echo framework: Similar but less popular/maintained
- Fiber: Fast but API differs significantly from standard patterns

### 4. Environment Variables for Database Config

**Decision:** Use separate environment variables for database credentials: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

**Rationale:**
- More flexible than single DATABASE_URL (easier to configure in different environments)
- Standard pattern for Go applications
- Compatible with cronjob execution (easier to pass individual env vars)
- Aligns with 12-factor app principles

**Alternatives Considered:**
- Keep DATABASE_URL: Less granular, harder to override individual components

### 5. Remove POST /api/menu/sync Endpoint

**Decision:** Remove the manual sync endpoint; sync only via direct script execution

**Rationale:**
- Sync should be controlled externally (cronjob/manual execution), not via API
- Reduces API server complexity and attack surface
- Aligns with separation of concerns (API serves data, doesn't modify it)

**Alternatives Considered:**
- Keep endpoint in Go: Adds PDF parsing dependencies to Go server, defeats purpose of split

### 6. Database Access Pattern

**Decision:**
- Python script: Use SQLAlchemy (existing models) for database insertion
- Go API: Use sqlx or pgx for read-only database queries

**Rationale:**
- Python script can reuse existing database models and logic
- Go API only needs simple SELECT queries (no ORM needed)
- Keeps Go binary small and dependencies minimal

**Alternatives Considered:**
- GORM for Go: Adds overhead for simple read operations, larger binary

## Risks / Trade-offs

### Risk: PDF Parsing Breakage
**Impact:** If PDF format changes, sync script fails silently  
**Mitigation:** Add logging to script output, monitor cronjob execution, add alerting on failure

### Risk: Database Connection Management
**Impact:** Two separate processes accessing database could cause connection issues  
**Mitigation:** Use connection pooling in both, ensure proper connection cleanup, configure max connections appropriately

### Trade-off: Two Codebases
**Impact:** Need to maintain Python and Go code separately  
**Benefit:** Each language used for its strength (Python for PDF parsing, Go for API performance)

### Risk: Breaking Change for Clients
**Impact:** Clients using POST `/api/menu/sync` will break  
**Mitigation:** Document in release notes, provide migration guide (use cronjob or manual script execution)

### Trade-off: Increased Deployment Complexity
**Impact:** Two separate components to deploy and manage  
**Benefit:** More flexible deployment options (scale API independently, run sync on different schedule)

## Migration Plan

### Phase 1: Create Go API (parallel to existing)
1. Implement Go API with gin-gonic (same endpoints as existing GET routes)
2. Test against existing database
3. Verify API compatibility

### Phase 2: Create Standalone Python Script
1. Extract sync logic from `menu_service.py` into `scripts/sync_menu.py`
2. Add environment variable configuration
3. Test script execution independently

### Phase 3: Deploy and Switch
1. Deploy Go API server (test in parallel with Python API)
2. Set up cronjob for Python sync script
3. Switch traffic to Go API
4. Remove Python API server
5. Update documentation

### Rollback Strategy
- Keep Python API code in repository (tagged release)
- Can redeploy Python API if Go API has critical issues
- Database schema unchanged, so no data migration needed

## Open Questions

1. **Cronjob schedule:** How often should sync run? (Current: every 6 hours)
   - Recommendation: Once per day (e.g., 6 AM) since menu typically updates daily

2. **Error handling in sync script:** Should script exit with non-zero on failure or continue?
   - Recommendation: Exit non-zero on failure for cronjob monitoring

3. **Go database driver:** Use lib/pq or pgx?
   - Recommendation: pgx (better performance, more actively maintained)

4. **Logging in Go API:** Use structured logging (e.g., zerolog)?
   - Recommendation: Yes, use zerolog for consistent structured logs
