import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import GenerationJob, Recipient, RecipientStatus
from app.services.certificate_service import CertificateService
from app.services.job_service import finish_job, mark_failure, mark_success, start_job

logger = logging.getLogger(__name__)


def process_generation_job(job_id: str) -> None:
    db: Session = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if not job:
            logger.error("Generation job %s not found", job_id)
            return
        start_job(db, job_id)
        service = CertificateService()

        recipients = list(db.query(Recipient).filter(Recipient.job_id == job_id).all())
        for recipient in recipients:
            if recipient.status != RecipientStatus.PENDING:
                continue
            try:
                recipient.status = RecipientStatus.PROCESSING
                db.commit()
                path = service.generate(
                    certificate_id=recipient.id,
                    recipient_name=recipient.name,
                    event_name=job.event_name,
                    certificate_title=job.certificate_title,
                )
                mark_success(db, recipient, path)
            except Exception as exc:  # isolate a single recipient failure
                db.rollback()
                failed = db.get(Recipient, recipient.id)
                if failed:
                    mark_failure(db, failed, str(exc))
                logger.exception("Certificate generation failed for recipient %s", recipient.id)
        finish_job(db, job_id)
    except Exception:
        db.rollback()
        logger.exception("Unexpected generation job failure: %s", job_id)
        job = db.get(GenerationJob, job_id)
        if job:
            from app.models import JobStatus
            job.status = JobStatus.FAILED
            db.commit()
    finally:
        db.close()
