#!/bin/bash

# This script is run by Render to start the backend service.

# The path where Render's persistent disk is mounted and where we told our Python code to look.
VECTOR_STORE_PATH="/var/data/vectorstore/chroma"

# Check if a key file from ChromaDB already exists. If it does, we skip initialization.
if [ -f "$VECTOR_STORE_PATH/chroma.sqlite3" ]; then
    echo "Vector store already exists. Skipping initialization."
else
    echo "Vector store not found. Initializing..."
    # Run the python script to create and populate the database.
    # This will only run ONCE on the very first deployment.
    python scripts/init_vector_store.py
fi

# After the check is complete, start the FastAPI server.
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000