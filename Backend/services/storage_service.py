import os
from google.cloud import storage
from config import Config

class StorageService:
    """Manages synchronization of clinical catalog files from GCS."""

    def __init__(self):
        self.bucket_name = Config.CATALOG_BUCKET
        self.local_dir = Config.CATALOG_DIR
        self.client = None
        
        if self.bucket_name:
            try:
                self.client = storage.Client()
                if not os.path.exists(self.local_dir):
                    os.makedirs(self.local_dir)
            except Exception as e:
                print(f"[ERROR] Failed to initialize GCS client: {e}")

    def sync_catalog(self):
        """
        Downloads all CSV and TXT files from the specified GCS bucket.
        Returns True if any files were changed/downloaded.
        """
        if not self.client or not self.bucket_name:
            print("[INFO] GCS Bucket not configured, skipping sync.")
            return False

        print(f"[INFO] Syncing clinical catalog from GCS bucket: {self.bucket_name}")
        changed = False
        
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blobs = bucket.list_blobs()
            
            for blob in blobs:
                # Only sync clinical data files
                if not (blob.name.endswith(".csv") or blob.name.endswith(".txt")):
                    continue
                
                local_path = os.path.join(self.local_dir, os.path.basename(blob.name))
                
                # Check if download is needed (crude check: size mismatch)
                should_download = True
                if os.path.exists(local_path):
                    local_size = os.path.getsize(local_path)
                    if local_size == blob.size:
                        should_download = False
                
                if should_download:
                    print(f"  [SYNC] Downloading {blob.name} ...")
                    blob.download_to_filename(local_path)
                    changed = True
            
            if not changed:
                print("  [OK] Local catalog is up to date.")
            
            return changed
            
        except Exception as e:
            print(f"[ERROR] GCS Sync failed: {e}")
            return False
