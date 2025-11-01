import os
from typing import Optional

def get_available_model() -> str:
    """
    Detect available model with fallback chain
    Try models in order until one works
    """
    candidate_models = [
        "gemini-pro",  # Most stable/reliable
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
    ]
    
    # Check env variable override
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        return env_model
    
    # Default to most reliable
    return "gemini-pro"

def get_embedding_model() -> str:
    """Get embedding model - typically 'embedding-001'"""
    return os.getenv("GEMINI_EMBEDDING_MODEL", "embedding-001")
