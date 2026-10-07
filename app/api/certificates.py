from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Recipient, RecipientStatus

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])


@router.get("/{certificate_id}")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    recipient = db.get(Recipient, certificate_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if recipient.status != RecipientStatus.SUCCESS or not recipient.certificate_path:
        raise HTTPException(status_code=409, detail="Certificate is not available")

    storage_root = Path(get_settings().storage_dir).resolve()
    file_path = Path(recipient.certificate_path).resolve()
    try:
        file_path.relative_to(storage_root)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid certificate storage path")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Certificate file is missing")
    return FileResponse(file_path, media_type="application/pdf", filename=f"certificate-{recipient.id}.pdf")
