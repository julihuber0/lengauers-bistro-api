# Docker Deployment Guide

## Dockerfile Features

Das Multi-Stage Dockerfile bietet:

- ✅ **Multi-Stage Build** - Kleineres finales Image (~15MB vs ~300MB)
- ✅ **Security** - Non-root User
- ✅ **Optimized** - Statically linked binary (CGO_ENABLED=0)
- ✅ **Health Check** - Automatische Gesundheitsprüfung
- ✅ **Layer Caching** - Schnellere Builds durch optimierte Layer-Reihenfolge

## Quick Start

### 1. Build & Run mit Docker Compose

```bash
# Build und starten aller Services
docker-compose up --build -d

# Logs anschauen
docker-compose logs -f api

# Status prüfen
docker-compose ps

# Stoppen
docker-compose down
```

### 2. Nur Datenbank starten

```bash
# Wenn Sie die API lokal entwickeln möchten
docker-compose up psql_bp -d
go run cmd/api/main.go
```

### 3. Manueller Docker Build

```bash
# Image bauen
docker build -t lengauers-bistro-api:latest .

# Container starten
docker run -d \
  --name bistro-api \
  -p 8080:8080 \
  -e BLUEPRINT_DB_HOST=host.docker.internal \
  -e BLUEPRINT_DB_PORT=5432 \
  -e BLUEPRINT_DB_DATABASE=blueprint \
  -e BLUEPRINT_DB_USERNAME=melkey \
  -e BLUEPRINT_DB_PASSWORD=password1234 \
  -e BLUEPRINT_DB_SCHEMA=public \
  lengauers-bistro-api:latest

# Logs anschauen
docker logs -f bistro-api

# Stoppen und entfernen
docker stop bistro-api
docker rm bistro-api
```

## Docker Compose Services

### Services

1. **psql_bp** - PostgreSQL 16 Datenbank
   - Port: 5432
   - Volume: Persistente Datenspeicherung
   - Health Check: Automatische Verfügbarkeitsprüfung

2. **api** - Bistro API Server
   - Port: 8080
   - Wartet auf gesunde Datenbank
   - Automatisches Restart bei Fehlern

### Networking

Beide Services kommunizieren über ein internes Bridge-Netzwerk (`bistro-network`):
- API erreicht Datenbank über Hostname `psql_bp`
- Keine direkte Verbindung von außen zur Datenbank nötig

## Environment Variables

Alle in `.env` definierten Variablen werden verwendet:

```env
# Server
PORT=8080
APP_ENV=local

# Database
BLUEPRINT_DB_HOST=localhost  # In Docker Compose: psql_bp
BLUEPRINT_DB_PORT=5432
BLUEPRINT_DB_DATABASE=blueprint
BLUEPRINT_DB_USERNAME=melkey
BLUEPRINT_DB_PASSWORD=password1234
BLUEPRINT_DB_SCHEMA=public

# Optional: PDF Fetching
PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf
FETCH_INTERVAL=1h
```

## Testing Docker Build

```bash
# Image bauen
docker build -t lengauers-bistro-api:test .

# Prüfen der Image-Größe
docker images lengauers-bistro-api:test

# Mit compose testen
docker-compose up --build

# API testen
curl http://localhost:8080/health
curl "http://localhost:8080/menu?date=2026-02-03"
```

## Production Deployment

### Mit Docker Compose (empfohlen)

```bash
# Auf dem Server
git clone <repository>
cd lengauers-bistro-api

# .env anpassen für Production
nano .env

# Starten
docker-compose up -d

# Logs überwachen
docker-compose logs -f
```

### Mit Docker Swarm

```bash
# Swarm initialisieren
docker swarm init

# Stack deployen
docker stack deploy -c docker-compose.yml bistro

# Status prüfen
docker stack services bistro
docker stack ps bistro
```

### Mit Kubernetes

Erstellen Sie Kubernetes Manifests basierend auf dem Docker Image:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bistro-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bistro-api
  template:
    metadata:
      labels:
        app: bistro-api
    spec:
      containers:
      - name: api
        image: lengauers-bistro-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: BLUEPRINT_DB_HOST
          value: postgres-service
        # ... weitere env vars
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
```

## Monitoring & Health Checks

### Docker Health Check

Das Dockerfile enthält einen eingebauten Health Check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
```

Status prüfen:
```bash
docker ps  # Zeigt "healthy" oder "unhealthy"
docker inspect bistro-api | grep -A 10 Health
```

### Logs

```bash
# Alle Logs
docker-compose logs

# Nur API Logs
docker-compose logs api

# Live Logs folgen
docker-compose logs -f api

# Letzte 100 Zeilen
docker-compose logs --tail=100 api
```

## Optimization Tips

### Build Performance

```bash
# Cache nutzen (schnellere Rebuilds)
docker build --cache-from lengauers-bistro-api:latest -t lengauers-bistro-api:latest .

# BuildKit aktivieren (schneller)
DOCKER_BUILDKIT=1 docker build -t lengauers-bistro-api:latest .
```

### Image Größe reduzieren

Das aktuelle Multi-Stage Build produziert bereits sehr kleine Images:
- Builder Stage: ~300MB (wird verworfen)
- Final Image: ~15-20MB

Weitere Optimierungen:
```dockerfile
# UPX komprimierung (optional, im Dockerfile auskommentiert)
RUN apk add --no-cache upx
RUN upx --best --lzma /app/bin/api
```

### Resource Limits

In `docker-compose.yml` hinzufügen:

```yaml
services:
  api:
    # ... existing config
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
```

## Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker-compose logs api

# Interaktive Shell im Container
docker run -it --rm lengauers-bistro-api:latest /bin/sh

# Netzwerk prüfen
docker network inspect lengauers-bistro-api_bistro-network
```

### Datenbankverbindung fehlschlägt

```bash
# Datenbank Health Check
docker-compose ps

# PostgreSQL Logs
docker-compose logs psql_bp

# Connection von API Container testen
docker-compose exec api ping psql_bp
```

### Port bereits belegt

```bash
# Port in .env ändern
echo "PORT=8081" >> .env

# Oder in docker-compose.yml
ports:
  - "8081:8080"
```

### Volume Probleme

```bash
# Volumes neu erstellen
docker-compose down -v
docker-compose up -d

# Volumes manuell löschen
docker volume ls
docker volume rm lengauers-bistro-api_psql_volume_bp
```

## Security Best Practices

1. ✅ **Non-root User** - Container läuft als User `appuser`
2. ✅ **Read-only Filesystem** - Kann mit `--read-only` flag aktiviert werden
3. ✅ **No Secrets in Image** - Env vars statt hardcoded credentials
4. ✅ **Minimal Base Image** - Alpine Linux (~5MB)
5. ✅ **Health Checks** - Automatische Erkennung von Problemen

### Production Security Enhancements

```bash
# Secrets Management mit Docker Secrets
echo "password1234" | docker secret create db_password -

# In docker-compose.yml
secrets:
  db_password:
    external: true

services:
  api:
    secrets:
      - db_password
    environment:
      BLUEPRINT_DB_PASSWORD_FILE: /run/secrets/db_password
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t lengauers-bistro-api:${{ github.sha }} .
    
    - name: Run tests
      run: docker run lengauers-bistro-api:${{ github.sha }} go test ./...
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push lengauers-bistro-api:${{ github.sha }}
```

## Backup & Restore

### Database Backup

```bash
# Backup erstellen
docker-compose exec psql_bp pg_dump -U melkey blueprint > backup.sql

# Oder mit timestamp
docker-compose exec psql_bp pg_dump -U melkey blueprint > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T psql_bp psql -U melkey blueprint < backup.sql
```

### Volume Backup

```bash
# Volume in tar archivieren
docker run --rm -v lengauers-bistro-api_psql_volume_bp:/data -v $(pwd):/backup alpine tar czf /backup/db_backup.tar.gz /data

# Restore
docker run --rm -v lengauers-bistro-api_psql_volume_bp:/data -v $(pwd):/backup alpine tar xzf /backup/db_backup.tar.gz -C /
```

## Performance Monitoring

```bash
# Resource Usage
docker stats

# Nur API Container
docker stats bistro-api

# Inspect
docker inspect bistro-api
```

## Updates & Rollbacks

```bash
# Update mit neuem Image
docker-compose pull
docker-compose up -d

# Rollback zum vorherigen Image
docker tag lengauers-bistro-api:latest lengauers-bistro-api:backup
docker-compose down
docker-compose up -d
```
