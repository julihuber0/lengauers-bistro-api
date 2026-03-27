## ADDED Requirements

### Requirement: API server starts and listens
The Go API server SHALL start and listen on a configured host and port.

#### Scenario: Server starts successfully
- **WHEN** the server is started with valid configuration
- **THEN** it listens on the configured host and port

#### Scenario: Port already in use
- **WHEN** the configured port is already in use
- **THEN** the server logs an error and exits with non-zero exit code

### Requirement: API uses gin-gonic framework
The API server SHALL be implemented using the gin-gonic web framework.

#### Scenario: Framework initialization
- **WHEN** the server starts
- **THEN** it initializes a gin router and registers routes

### Requirement: API reads database config from environment variables
The API server SHALL read database connection parameters from environment variables.

#### Scenario: Database connection established
- **WHEN** DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME are set
- **THEN** the server connects to PostgreSQL using these credentials

#### Scenario: Missing database configuration
- **WHEN** any required database environment variable is missing
- **THEN** the server logs an error and exits with non-zero exit code

### Requirement: API reads server config from environment variables
The API server SHALL read server configuration from environment variables.

#### Scenario: Custom host and port
- **WHEN** API_HOST and API_PORT environment variables are set
- **THEN** the server listens on the specified host and port

#### Scenario: Default configuration
- **WHEN** API_HOST and API_PORT are not set
- **THEN** the server uses defaults (0.0.0.0:8000)

### Requirement: API manages database connections efficiently
The API server SHALL use a connection pool for database access.

#### Scenario: Connection pooling
- **WHEN** multiple requests are handled concurrently
- **THEN** the server reuses connections from a pool

#### Scenario: Connection cleanup
- **WHEN** the server shuts down
- **THEN** all database connections are closed gracefully

### Requirement: API handles graceful shutdown
The API server SHALL handle shutdown signals gracefully.

#### Scenario: SIGTERM received
- **WHEN** the server receives SIGTERM or SIGINT signal
- **THEN** it completes in-flight requests and closes database connections before exiting

### Requirement: API provides structured logging
The API server SHALL output structured logs for debugging and monitoring.

#### Scenario: Request logging
- **WHEN** an API request is received
- **THEN** the server logs request method, path, status code, and duration

#### Scenario: Error logging
- **WHEN** an error occurs
- **THEN** the server logs the error with context (request ID, timestamp, error message)

### Requirement: API CORS configuration
The API server SHALL support CORS for cross-origin requests.

#### Scenario: CORS headers included
- **WHEN** a request is made from a different origin
- **THEN** the server includes appropriate CORS headers in the response

### Requirement: API serves health check endpoint
The API server SHALL provide a health check endpoint at GET /api/health.

#### Scenario: Health check request
- **WHEN** GET /api/health is requested
- **THEN** the server returns 200 OK with JSON: {"status": "healthy", "timestamp": "<ISO8601>"}

### Requirement: API serves menu retrieval endpoint
The API server SHALL provide a menu retrieval endpoint at GET /api/menu.

#### Scenario: Query by date
- **WHEN** GET /api/menu?date=YYYY-MM-DD is requested with valid date
- **THEN** the server returns 200 OK with menu items for that date

#### Scenario: Invalid date format
- **WHEN** GET /api/menu?date=invalid is requested
- **THEN** the server returns 400 Bad Request with error message

#### Scenario: No menu found
- **WHEN** GET /api/menu?date=2020-01-01 is requested for a date with no menu
- **THEN** the server returns 404 Not Found with error message

#### Scenario: Missing date parameter
- **WHEN** GET /api/menu is requested without date parameter
- **THEN** the server returns 400 Bad Request with error message

### Requirement: API serves available dates endpoint
The API server SHALL provide an endpoint to list available menu dates at GET /api/menu/dates.

#### Scenario: Get available dates
- **WHEN** GET /api/menu/dates is requested
- **THEN** the server returns 200 OK with JSON: {"dates": ["YYYY-MM-DD", ...]} in descending order

#### Scenario: No dates available
- **WHEN** GET /api/menu/dates is requested and database is empty
- **THEN** the server returns 200 OK with JSON: {"dates": []}

### Requirement: API serves root endpoint
The API server SHALL provide an informational endpoint at GET /.

#### Scenario: Root endpoint request
- **WHEN** GET / is requested
- **THEN** the server returns 200 OK with API information and available endpoints
