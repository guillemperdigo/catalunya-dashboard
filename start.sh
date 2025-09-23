#!/bin/bash

# Generate mock data if not exists
if [ ! -d "data/prices" ] || [ -z "$(ls -A data/prices)" ]; then
    echo "Generating mock data..."
    python scripts/gen_mock_data.py
fi

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
