# Simple Makefile for a Go project

# Build the application
all: build test

build:
	@echo "Building..."
	@go build -o bin/api cmd/api/main.go

# Run the application
run:
	@go run cmd/api/main.go

# Create and run full stack (DB + API)
docker-run:
	@if docker compose up --build -d 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose up --build -d; \
	fi

# Shutdown full stack
docker-down:
	@if docker compose down 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose down; \
	fi

# Start only database container
docker-db:
	@if docker compose up psql_bp -d 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose up psql_bp -d; \
	fi

# View logs from all containers
docker-logs:
	@if docker compose logs -f 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose logs -f; \
	fi

# View logs from API only
docker-logs-api:
	@if docker compose logs -f api 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose logs -f api; \
	fi

# Restart all services
docker-restart:
	@if docker compose restart 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose restart; \
	fi

# Build Docker image only (no start)
docker-build:
	@docker build -t lengauers-bistro-api:latest .

# Remove all containers and volumes (clean slate)
docker-clean:
	@if docker compose down -v 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose down -v; \
	fi
	@docker rmi lengauers-bistro-api:latest 2>/dev/null || true

# Check status of containers
docker-ps:
	@if docker compose ps 2>/dev/null; then \
		: ; \
	else \
		echo "Falling back to Docker Compose V1"; \
		docker-compose ps; \
	fi

# Test the application
test:
	@echo "Testing..."
	@go test ./... -v

# Test with coverage
test-coverage:
	@echo "Testing with coverage..."
	@go test ./... -cover -coverprofile=coverage.out
	@go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# Integrations Tests for the application
itest:
	@echo "Running integration tests..."
	@go test ./internal/database -v

# Clean the binary
clean:
	@echo "Cleaning..."
	@rm -f bin/api main
	@rm -f coverage.out coverage.html

# Live Reload
watch:
	@if command -v air > /dev/null; then \
            air; \
            echo "Watching...";\
        else \
            read -p "Go's 'air' is not installed on your machine. Do you want to install it? [Y/n] " choice; \
            if [ "$$choice" != "n" ] && [ "$$choice" != "N" ]; then \
                go install github.com/air-verse/air@latest; \
                air; \
                echo "Watching...";\
            else \
                echo "You chose not to install air. Exiting..."; \
                exit 1; \
            fi; \
        fi

# Format code
fmt:
	@echo "Formatting code..."
	@go fmt ./...

# Lint code (requires golangci-lint)
lint:
	@echo "Linting code..."
	@golangci-lint run || echo "golangci-lint not installed"

# Run the full development setup (DB in Docker, API locally with hot reload)
dev:
	@echo "Starting development environment..."
	@make docker-db
	@sleep 3
	@make watch

# Quick test of API endpoints
test-api:
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8080/health | grep -q "up" && echo "✓ Health endpoint OK" || echo "✗ Health endpoint failed"
	@curl -s "http://localhost:8080/menu?date=2026-02-03" | grep -q "\[" && echo "✓ Menu endpoint OK" || echo "✗ Menu endpoint failed"

# Help command
help:
	@echo "Available commands:"
	@echo "  make build           - Build the application binary"
	@echo "  make run             - Run the application locally"
	@echo "  make test            - Run all tests"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make clean           - Remove built binaries and test files"
	@echo "  make watch           - Run with hot reload (air)"
	@echo "  make fmt             - Format Go code"
	@echo "  make lint            - Lint Go code"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-run      - Start full stack (DB + API) in Docker"
	@echo "  make docker-down     - Stop all containers"
	@echo "  make docker-db       - Start only database container"
	@echo "  make docker-logs     - View all container logs"
	@echo "  make docker-logs-api - View API container logs"
	@echo "  make docker-restart  - Restart all containers"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-clean    - Remove containers, volumes, and images"
	@echo "  make docker-ps       - Show container status"
	@echo ""
	@echo "Development:"
	@echo "  make dev             - Start DB in Docker + API locally with hot reload"
	@echo "  make test-api        - Quick test of API endpoints"

.PHONY: all build run test test-coverage clean watch docker-run docker-down docker-db \
        docker-logs docker-logs-api docker-restart docker-build docker-clean docker-ps \
        itest fmt lint dev test-api help
