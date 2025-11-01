#!/bin/bash

# On Hugging Face, the storage is persistent by default. No need for special paths.
VECTOR_STORE_PATH="vectorstore/chroma"

# Check if the vector store already exists.
if [ -f "$VECTOR_STORE_PATH/chroma.sqlite3" ]; then
    echo "Vector store already exists. Skipping initialization."
else
    echo "Vector store not found. Initializing..."
    python scripts/init_vector_store.py
fi

# Start the FastAPI backend in the background
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit frontend in the foreground
echo "Starting Streamlit frontend..."
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0