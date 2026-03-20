"""
Pre-build script to initialize the database and vector index during Docker build.
"""
import sys
import os

# Ensure backend directory is on import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from services.catalog_service import CatalogService
from services.vector_service import VectorService
from services.storage_service import StorageService

def build():
    print("Building deployment assets...")
    
    # 0. Sync from GCS (optional, requires credentials in build environment)
    storage = StorageService()
    storage.sync_catalog()
    
    # 1. Initialize database
    init_db()
    
    # 2. Ingest catalog
    catalog = CatalogService()
    catalog.ingest_all()
    
    # 3. Build vector index
    vector = VectorService()
    vector.build_index()
    
    print("Successfully built all assets.")

if __name__ == "__main__":
    build()
