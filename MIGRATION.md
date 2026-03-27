# Migration Guide: v1.0 (FastAPI) to v2.0 (Go API)

## Overview

Version 2.0 introduces a significant architectural change by splitting the monolithic FastAPI application into two independent components:
- **Python Sync Script**: Standalone script for PDF fetching and parsing
- **Go REST API**: High-performance API server for menu queries

## Breaking Changes

### 1. POST /api/menu/sync Endpoint Removed

**What changed:**
- The `POST /api/menu/sync` endpoint has been removed
- Manual sync is now triggered by running the standalone Python script directly

**Migration:**
```bash
# Old way (v1.0):
curl -X POST http://localhost:8000/api/menu/sync

# New way (v2.0):
python3 scripts/sync_menu.py
```

**For automated sync:**
- v1.0: Used in-process APScheduler
- v2.0: Use system cronjob (see scripts/crontab.example)

### 2. Environment Variables Changed

**What changed:**
- `DATABASE_URL` replaced with individual `DB_*` variables
- `SYNC_INTERVAL_HOURS` no longer needed (handled by cronjob schedule)

**Migration:**

Old `.env` (v1.0):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/lengauers_bistro
SYNC_INTERVAL_HOURS=6
PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf
API_HOST=0.0.0.0
API_PORT=8000
```

New `.env` (v2.0):
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=lengauers_bistro

# Python Script
PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf

# Go API
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Deployment Architecture

**v1.0:** Single Python process (FastAPI + APScheduler)
**v2.0:** Two independent components
- Go API server (runs continuously)
- Python sync script (runs via cronjob)

## Compatible (No Changes Required)

✅ **All GET endpoints remain compatible:**
- `GET /api/menu?date=YYYY-MM-DD`
- `GET /api/menu/dates`
- `GET /api/health`
- `GET /`

✅ **Database schema unchanged** - existing data works as-is

✅ **Response formats unchanged** - client code doesn't need updates

## Step-by-Step Migration

### 1. Backup Current Database

```bash
pg_dump lengauers_bistro > backup_$(date +%Y%m%d).sql
```

### 2. Update Code

```bash
git pull origin main  # or download v2.0
```

### 3. Install Dependencies

```bash
# Python dependencies (reduced)
pip install -r requirements.txt

# Build Go API
go build -o bin/api cmd/api/main.go
```

### 4. Update Environment Variables

```bash
# Update your .env file with new format (see above)
cp .env.example .env
# Edit .env with your values
```

### 5. Stop Old Service

```bash
# If running via systemd
sudo systemctl stop lengauers-api

# If running manually
pkill -f "uvicorn src.main:app"
```

### 6. Start Go API Server

```bash
# Test first
./bin/api

# Then set up systemd service
sudo cp scripts/lengauers-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lengauers-api
sudo systemctl start lengauers-api
sudo systemctl status lengauers-api
```

### 7. Set Up Sync Cronjob

```bash
# Edit crontab
crontab -e

# Add line (adjust paths):
0 6 * * * cd /opt/lengauers-bistro-api && /usr/bin/python3 scripts/sync_menu.py >> /var/log/lengauers-sync.log 2>&1
```

### 8. Test Everything

```bash
# Test sync script manually
python3 scripts/sync_menu.py

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/menu/dates
curl "http://localhost:8000/api/menu?date=2026-02-03"
```

### 9. Update Client Code (if using POST /api/menu/sync)

If your clients were triggering manual sync via the API:

```javascript
// Old code (v1.0)
fetch('http://api.example.com/api/menu/sync', { method: 'POST' })
  .then(res => res.json())
  .then(data => console.log(data));

// New approach (v2.0)
// Option 1: Remove manual sync (rely on cronjob)
// Option 2: Create a webhook endpoint that triggers the script via SSH/exec
// Option 3: Direct script execution if client has server access
```

## Rollback Plan

If you need to rollback to v1.0:

```bash
# Stop v2.0 services
sudo systemctl stop lengauers-api
crontab -e  # Remove sync cronjob

# Restore v1.0 code
git checkout v1.0

# Reinstall dependencies
pip install -r requirements.txt

# Update .env back to old format
# Restart old service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Benefits of v2.0

- ✅ Better performance (Go is faster than Python for HTTP serving)
- ✅ Smaller memory footprint for API server
- ✅ Independent scaling (scale API separately from sync)
- ✅ More flexible deployment (cronjob schedule, multiple sync instances, etc.)
- ✅ Clearer separation of concerns
- ✅ Easier to monitor and debug (separate processes/logs)

## Support

For issues with migration, please open a GitHub issue with:
- Your current v1.0 setup
- Error messages or unexpected behavior
- Relevant logs from sync script or API server
