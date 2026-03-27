#!/bin/bash
# Test script for Go API server

set -e

echo "=== Testing Go API Server ==="

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=bistro_user
export DB_PASSWORD=bistro_pass
export DB_NAME=lengauers_bistro
export API_HOST=localhost
export API_PORT=8080

echo "Building Go API..."
go build -o bin/api cmd/api/main.go

echo "Starting API server in background..."
./bin/api &
API_PID=$!

# Give server time to start
sleep 3

echo ""
echo "Running API tests..."

# Test health endpoint
echo "Test 1: GET /api/health"
if curl -s http://localhost:8080/api/health | grep -q "healthy"; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    kill $API_PID
    exit 1
fi

# Test root endpoint
echo "Test 2: GET /"
if curl -s http://localhost:8080/ | grep -q "Lengauer"; then
    echo "✓ Root endpoint passed"
else
    echo "✗ Root endpoint failed"
    kill $API_PID
    exit 1
fi

# Test menu dates endpoint
echo "Test 3: GET /api/menu/dates"
if curl -s http://localhost:8080/api/menu/dates | grep -q "dates"; then
    echo "✓ Menu dates endpoint passed"
else
    echo "✗ Menu dates endpoint failed"
    kill $API_PID
    exit 1
fi

# Test menu endpoint with missing date
echo "Test 4: GET /api/menu (missing date parameter)"
if curl -s http://localhost:8080/api/menu | grep -q "Missing required parameter"; then
    echo "✓ Correctly handles missing date parameter"
else
    echo "✗ Failed to handle missing date parameter"
    kill $API_PID
    exit 1
fi

# Test menu endpoint with invalid date
echo "Test 5: GET /api/menu?date=invalid"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/menu?date=invalid)
if [ "$STATUS" = "400" ]; then
    echo "✓ Correctly returns 400 for invalid date"
else
    echo "✗ Failed to return 400 for invalid date (got $STATUS)"
    kill $API_PID
    exit 1
fi

echo ""
echo "Stopping server..."
kill $API_PID
wait $API_PID 2>/dev/null || true

echo ""
echo "=== Go API Server Tests Complete ==="
