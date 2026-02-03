# Lengauers Bistro API - Quick Start

## 🚀 Schnellstart mit Docker

Die einfachste Methode zum Starten der Anwendung:

```bash
# Repository klonen
git clone <repository>
cd lengauers-bistro-api

# Mit Docker Compose starten
docker-compose up -d

# Logs anschauen
docker-compose logs -f api

# API testen
curl http://localhost:8080/health
curl "http://localhost:8080/menu?date=2026-02-03"
```

Das war's! 🎉

## 📋 Voraussetzungen

- **Docker** und **Docker Compose**
- Oder: **Go 1.25+** und **PostgreSQL 16** für lokale Entwicklung

## 🐳 Docker Deployment

### Vollständiger Stack (empfohlen)

```bash
# Build und Start
docker-compose up --build -d

# Status prüfen
docker-compose ps

# Logs verfolgen
docker-compose logs -f

# Stoppen
docker-compose down
```

### Nur Datenbank (für lokale Entwicklung)

```bash
# Nur PostgreSQL starten
docker-compose up psql_bp -d

# API lokal ausführen
go run cmd/api/main.go
```

### Docker Image Details

- **Image-Größe:** ~23 MB (Multi-Stage Build)
- **Base:** Alpine Linux
- **Sicherheit:** Non-root User
- **Health Check:** Automatisch integriert

Siehe [DOCKER.md](DOCKER.md) für detaillierte Docker-Dokumentation.

## 💻 Lokale Entwicklung (ohne Docker)

### 1. Datenbank starten

```bash
docker-compose up psql_bp -d
```

### 2. Abhängigkeiten installieren

```bash
go mod download
```

### 3. Anwendung starten

```bash
# Standard
go run cmd/api/main.go

# Mit Hot Reload (Air)
air
```

### 4. Tests ausführen

```bash
# Alle Tests
go test ./...

# Mit Coverage
go test ./... -cover -v

# Spezifische Packages
go test ./internal/service -v
go test ./internal/repository -v
```

## 📚 API Endpoints

### GET /health
Health-Check für Monitoring

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "up",
  "message": "It's healthy",
  "open_connections": "1"
}
```

### GET /menu?date=YYYY-MM-DD
Tagesmenü für ein bestimmtes Datum abrufen

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
  }
]
```

## ⚙️ Konfiguration

Alle Einstellungen werden über `.env` gesteuert:

```env
# Server
PORT=8080
APP_ENV=local

# Datenbank
BLUEPRINT_DB_HOST=localhost
BLUEPRINT_DB_PORT=5432
BLUEPRINT_DB_DATABASE=blueprint
BLUEPRINT_DB_USERNAME=melkey
BLUEPRINT_DB_PASSWORD=password1234
BLUEPRINT_DB_SCHEMA=public

# PDF Parser (Optional)
PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf
FETCH_INTERVAL=1h
```

## 🏗️ Projektstruktur

```
lengauers-bistro-api/
├── cmd/api/              # Application entry point
├── internal/
│   ├── config/          # Configuration management
│   ├── database/        # Database connection (SQL + GORM)
│   ├── models/          # Data models
│   ├── repository/      # Data access layer
│   ├── service/         # Business logic & PDF parsing
│   ├── handler/         # HTTP handlers
│   ├── scheduler/       # Background jobs
│   └── server/          # Server setup & routes
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Complete stack definition
└── .env                 # Environment variables
```

## 🔄 Background Jobs

Die Anwendung fetcht automatisch die PDF-Tageskarte:
- **Beim Start:** Einmalig sofort
- **Periodisch:** Standard alle 60 Minuten (konfigurierbar)
- **Fehlerbehandlung:** Fehler werden geloggt, App läuft weiter

## 🧪 Testing

```bash
# Unit Tests
go test ./internal/repository -v
go test ./internal/service -v

# Integration Tests
go test ./internal/server -v

# Alle Tests mit Coverage
go test ./... -cover
```

## 📖 Dokumentation

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Detaillierte Architektur & Implementation
- **[DOCKER.md](DOCKER.md)** - Docker Deployment Guide
- **[Makefile](Makefile)** - Build & Test Commands

## 🔧 Nützliche Commands

```bash
# Build Binary
go build -o bin/api cmd/api/main.go

# Run Binary
./bin/api

# Format Code
go fmt ./...

# Lint (mit golangci-lint)
golangci-lint run

# Database Reset
docker-compose down -v
docker-compose up -d
```

## 🐛 Troubleshooting

### Port bereits belegt
```bash
# Port in .env ändern
echo "PORT=8081" >> .env
```

### Datenbank Verbindungsfehler
```bash
# PostgreSQL Status prüfen
docker-compose ps
docker-compose logs psql_bp

# Neu starten
docker-compose restart psql_bp
```

### PDF Parsing Fehler
```bash
# Logs prüfen
docker-compose logs api | grep PDF

# URL in .env überprüfen/ändern
PDF_URL=https://example.com/menu.pdf
```

## 🚀 Production Deployment

### Mit Docker Compose (empfohlen)

```bash
# Auf dem Server
git clone <repository>
cd lengauers-bistro-api

# .env für Production anpassen
nano .env

# Starten
docker-compose up -d

# Monitoring
docker-compose logs -f
```

### Erweiterte Optionen

Siehe [DOCKER.md](DOCKER.md) für:
- Kubernetes Deployment
- Docker Swarm
- CI/CD Integration
- Backup & Restore
- Security Best Practices

## 📊 Monitoring

### Health Checks

```bash
# HTTP Health Check
curl http://localhost:8080/health

# Docker Health Check
docker inspect lengauers-bistro-api-api-1 | grep Health
```

### Logs

```bash
# Alle Logs
docker-compose logs

# Nur API
docker-compose logs -f api

# Nur DB
docker-compose logs -f psql_bp
```

## 🤝 Contributing

1. Fork das Repository
2. Feature Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Changes committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request öffnen

## 📝 License

Dieses Projekt ist lizenziert unter [MIT License](LICENSE).

## 🔗 Links

- **Repository:** [GitHub](https://github.com/...)
- **Issues:** [GitHub Issues](https://github.com/.../issues)
- **Documentation:** [Wiki](https://github.com/.../wiki)

## 👨‍💻 Entwickelt mit

- [Go](https://golang.org/) - Programming Language
- [Gin](https://gin-gonic.com/) - Web Framework
- [GORM](https://gorm.io/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Docker](https://www.docker.com/) - Containerization

---

**Viel Erfolg! 🎉**

Bei Fragen siehe [IMPLEMENTATION.md](IMPLEMENTATION.md) oder öffne ein Issue.
