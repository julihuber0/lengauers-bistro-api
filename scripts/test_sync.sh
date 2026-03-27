#!/bin/bash
# Test script for Python sync script

set -e

echo "=== Testing Python Sync Script ==="

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=bistro_user
export DB_PASSWORD=bistro_pass
export DB_NAME=lengauers_bistro
export PDF_URL=https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf

echo "Testing with environment variables:"
echo "  DB_HOST=$DB_HOST"
echo "  DB_PORT=$DB_PORT"
echo "  DB_USER=$DB_USER"
echo "  DB_NAME=$DB_NAME"
echo "  PDF_URL=$PDF_URL"
echo ""

# Test 1: Missing environment variable
echo "Test 1: Testing error handling for missing env vars..."
unset DB_HOST
if python3 scripts/sync_menu.py 2>&1 | grep -q "Missing required environment variable"; then
    echo "✓ Correctly handles missing DB_HOST"
else
    echo "✗ Failed to handle missing DB_HOST"
    exit 1
fi
export DB_HOST=localhost

# Test 2: Run sync script
echo ""
echo "Test 2: Running sync script..."
python3 scripts/sync_menu.py

echo ""
echo "=== Python Sync Script Tests Complete ==="
