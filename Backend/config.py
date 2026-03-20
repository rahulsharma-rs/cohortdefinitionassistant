"""
Central configuration for the Cohort Refinement Assistant backend.
Loads settings from .env via python-dotenv.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # --- API Keys ---
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # --- LLM Settings ---
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # "google" or "openai"
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    # --- Database ---
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(os.path.dirname(__file__), "database/cohort.db"))

    # --- Vector DB ---
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", os.path.join(os.path.dirname(__file__), "vector_db"))

    # --- Catalog ---
    CATALOG_DIR = os.getenv("CATALOG_DIR", os.path.join(os.path.dirname(__file__), "catelogue"))
    CATALOG_DESCRIPTION_FILE = os.getenv(
        "CATALOG_DESCRIPTION_FILE", os.path.join(os.path.dirname(__file__), "EHR_Population_catelogue.txt")
    )

    # --- Flask ---
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # --- Workflow ---
    MAX_REVISION_ITERATIONS = int(os.getenv("MAX_REVISION_ITERATIONS", "3"))
