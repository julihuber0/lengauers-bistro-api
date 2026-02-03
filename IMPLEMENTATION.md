# Lengauers Bistro API - Implementation Documentation

## Übersicht

Diese API wurde mit einer skalierbaren, layered Architektur implementiert, die Best Practices für große Go-Projekte folgt.

## Projektstruktur

```
lengauers-bistro-api/
├── cmd/
│   └── api/
│       └── main.go                 # Application entry point
├── internal/
│   ├── config/
│   │   └── config.go              # Configuration management
│   ├── database/
│   │   ├── database.go            # Database connection (SQL + GORM)
│   │   └── database_test.go
│   ├── models/
│   │   └── menu.go                # Data models (DailyMenu)
│   ├── repository/
│   │   ├── menu.go                # Database operations
│   │   └── menu_test.go
│   ├── service/
│   │   ├── menu.go                # Business logic (PDF parsing)
│   │   └── menu_test.go
│   ├── handler/
│   │   └── menu.go                # HTTP handlers
│   ├── scheduler/
│   │   └── scheduler.go           # Background job scheduler
│   └── server/
│       ├── server.go              # Server initialization
│       ├── routes.go              # Route registration
│       └── routes_test.go
├── .env                            # Environment variables
├── docker-compose.yml              # PostgreSQL container
├── go.mod
├── go.sum
└── README.md
```

## Architecture Layers

### 1. **Models Layer** (`internal/models/`)
- Definiert Datenstrukturen
- GORM Tags für Datenbankschema
- JSON Tags für API-Responses

### 2. **Repository Layer** (`internal/repository/`)
- Datenbankoperationen (CRUD)
- Isoliert Datenbanklogik
- Interface-basiert für einfaches Testen

### 3. **Service Layer** (`internal/service/`)
- Business-Logik
- PDF-Parsing
- Datenvalidierung und -transformation

### 4. **Handler Layer** (`internal/handler/`)
- HTTP Request/Response Handling
- Input-Validierung
- Fehlerbehandlung

### 5. **Scheduler Layer** (`internal/scheduler/`)
- Periodische Background-Jobs
- PDF-Fetching
- Graceful Shutdown Support

## Key Features

### PDF Menu Parser
- Automatisches Parsing der Tageskarte PDF
- Extrahiert Datum, Gerichte und Preise
- Robust gegen Formatänderungen
- Filtert irrelevante Einträge (z.B. "Aufschlag")

### Database
- PostgreSQL mit GORM ORM
- Automatische Migrations
- Upsert-Operationen (Insert oder Update)
- Unique Constraint auf (Datum + Name)

### API Endpoints

#### GET /menu?date=YYYY-MM-DD
Gibt das Menü für ein bestimmtes Datum zurück.

**Request:**
```bash
curl "http://localhost:8080/menu?date=2026-02-03"
```

**Response:**
```json
[
  {
    "date": "2026-02-03T00:00:00Z",
    "name": "Schnitzel mit Pommes",
    "category": "Gerichte",
    "price": 9.90
  },
  {
    "date": "2026-02-03T00:00:00Z",
    "name": "Currywurst mit Kartoffelsalat",
    "category": "Gerichte",
    "price": 7.50
  }
]
```

#### GET /health
Health-Check Endpoint für Monitoring.

**Response:**
```json
{
  "status": "up",
  "message": "It's healthy",
  "open_connections": "1",
  "in_use": "0",
  "idle": "1"
}
```

## Configuration

Alle Konfigurationen werden über Umgebungsvariablen in `.env` gesteuert:

```env
# Server
PORT=8080

# Database
BLUEPRINT_DB_HOST=localhost
BLUEPRINT_DB_PORT=5432
BLUEPRINT_DB_DATABASE=blueprint
BLUEPRINT_DB_USERNAME=melkey
BLUEPRINT_DB_PASSWORD=password1234
BLUEPRINT_DB_SCHEMA=public

# PDF Fetching (optional, defaults shown)
PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf
FETCH_INTERVAL=1h
```

## Running the Application

### 1. Start PostgreSQL
```bash
docker-compose up -d
```

### 2. Run the Application
```bash
go run cmd/api/main.go
```

Oder mit kompiliertem Binary:
```bash
go build -o bin/api cmd/api/main.go
./bin/api
```

### 3. Mit Air (Hot Reload)
```bash
air
```

## Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test ./... -cover

# Run specific package tests
go test ./internal/service -v
go test ./internal/repository -v
```

## Dependencies

### Core
- **gin-gonic/gin** - HTTP web framework
- **gorm.io/gorm** - ORM
- **gorm.io/driver/postgres** - PostgreSQL driver
- **ledongthuc/pdf** - PDF parsing

### Testing
- **stretchr/testify** - Testing assertions
- **gorm.io/driver/sqlite** - In-memory DB for tests

## Database Schema

### daily_menus Table
```sql
CREATE TABLE daily_menus (
    id SERIAL PRIMARY KEY,
    menu_date DATE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'Gerichte',
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (menu_date, name)
);
```

## Scheduler Behavior

- **Start:** Läuft sofort beim Startup einmal
- **Interval:** Standard 1 Stunde (konfigurierbar)
- **Fehlerbehandlung:** Loggt Fehler, stoppt aber nicht
- **Graceful Shutdown:** Stoppt bei Server-Shutdown

## Error Handling

- Alle Fehler werden geloggt
- API gibt spezifische HTTP Status Codes zurück:
  - `400 Bad Request` - Ungültige Parameter
  - `500 Internal Server Error` - Server/DB Fehler
  - `200 OK` - Erfolgreiche Anfrage

## Best Practices Implemented

1. ✅ **Separation of Concerns** - Klare Layer-Trennung
2. ✅ **Dependency Injection** - Services werden injected
3. ✅ **Interface-based Design** - Einfaches Mocking für Tests
4. ✅ **Configuration Management** - Zentrale Config-Verwaltung
5. ✅ **Error Handling** - Konsistente Fehlerbehandlung
6. ✅ **Testing** - Unit Tests für kritische Komponenten
7. ✅ **Graceful Shutdown** - Sauberes Herunterfahren
8. ✅ **CORS Support** - Für Frontend-Integration
9. ✅ **Database Migrations** - Automatische Schema-Updates
10. ✅ **Logging** - Strukturiertes Logging

## Future Improvements

- [ ] Add authentication/authorization
- [ ] Implement caching layer (Redis)
- [ ] Add metrics (Prometheus)
- [ ] Implement request tracing
- [ ] Add more comprehensive error types
- [ ] Implement rate limiting
- [ ] Add OpenAPI/Swagger documentation
- [ ] Implement webhook notifications für neue Menüs
- [ ] Add support für mehrere Restaurants

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs psql_bp

# Restart
docker-compose restart
```

### PDF Parsing Issues
- Überprüfe PDF-URL in `.env`
- Teste manuell ob PDF erreichbar ist
- Prüfe Logs für spezifische Parse-Fehler

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>
```

## Contact & Support

Bei Fragen zur Implementierung siehe Code-Kommentare oder erstelle ein Issue.
