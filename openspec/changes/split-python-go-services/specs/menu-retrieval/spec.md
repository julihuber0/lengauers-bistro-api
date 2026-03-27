## MODIFIED Requirements

### Requirement: Menu items are retrieved by date
The system SHALL return menu items for a specific date via GET /api/menu endpoint.

#### Scenario: Valid date query
- **WHEN** GET /api/menu?date=2026-02-03 is requested
- **THEN** the system returns 200 OK with JSON array of menu items: [{"id": int, "name": string, "category": "Gericht", "price": float}]

#### Scenario: Invalid date format
- **WHEN** GET /api/menu?date=invalid-date is requested
- **THEN** the system returns 400 Bad Request with error message "Invalid date format. Use YYYY-MM-DD"

#### Scenario: No menu found for date
- **WHEN** GET /api/menu?date=2020-01-01 is requested and no menu exists for that date
- **THEN** the system returns 404 Not Found with error message "No menu found for YYYY-MM-DD"

#### Scenario: Missing date parameter
- **WHEN** GET /api/menu is requested without date query parameter
- **THEN** the system returns 400 Bad Request with error message

### Requirement: Available menu dates are listed
The system SHALL return all dates that have menu items via GET /api/menu/dates endpoint.

#### Scenario: Dates exist
- **WHEN** GET /api/menu/dates is requested
- **THEN** the system returns 200 OK with JSON: {"dates": ["2026-02-03", "2026-02-02", ...]} in descending order

#### Scenario: No dates available
- **WHEN** GET /api/menu/dates is requested and no menu items exist
- **THEN** the system returns 200 OK with JSON: {"dates": []}

### Requirement: Health check endpoint available
The system SHALL provide a health check endpoint at GET /api/health.

#### Scenario: Health check
- **WHEN** GET /api/health is requested
- **THEN** the system returns 200 OK with JSON: {"status": "healthy", "timestamp": "<ISO8601 timestamp>"}

## REMOVED Requirements

### Requirement: Manual sync via POST endpoint
**Reason**: Sync functionality is decoupled into a standalone script to enable independent execution (cronjob) and reduce API server complexity.

**Migration**: Use the standalone Python script `scripts/sync_menu.py` directly, either via cronjob or manual execution. The API server no longer triggers sync operations.

### Requirement: Background scheduled sync
**Reason**: Scheduling is moved outside the application to be handled by system-level cronjob or task scheduler.

**Migration**: Set up a cronjob to execute `scripts/sync_menu.py` on the desired schedule (e.g., daily at 6 AM).
