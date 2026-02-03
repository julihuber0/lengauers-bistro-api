"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lengauers_bistro")
    
    # PDF Source
    PDF_URL = os.getenv("PDF_URL", "https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf")
    
    # Sync Configuration
    SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", "6"))
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))


config = Config()
