import os
import hashlib
import time
from typing import Dict, Any, Tuple
from fastapi import UploadFile
from ..config import settings

class SecureStorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, file: UploadFile, uploader_id: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Saves uploaded file into secure storage, computes SHA-256 integrity hash,
        and generates security audit metadata.
        """
        content = await file.read()
        file_size = len(content)
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Sanitize filename
        safe_filename = os.path.basename(file.filename or "uploaded_doc").replace(" ", "_")
        doc_id = f"doc_{sha256_hash[:12]}"
        stored_filename = f"{doc_id}_{safe_filename}"
        local_path = os.path.join(self.upload_dir, stored_filename)

        with open(local_path, "wb") as f:
            f.write(content)

        audit_meta = {
            "document_id": doc_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "local_path": local_path,
            "gcs_uri": f"gs://{settings.GCS_BUCKET_NAME}/{stored_filename}",
            "sha256_hash": sha256_hash,
            "file_size_bytes": file_size,
            "uploader_id": uploader_id,
            "uploaded_at": time.time(),
            "mime_type": file.content_type or "application/octet-stream"
        }
        
        return doc_id, local_path, audit_meta

storage_service = SecureStorageService()
