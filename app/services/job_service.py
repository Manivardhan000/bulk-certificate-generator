from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import GenerationJob, JobStatus, Recipient, RecipientStatus
from app.schemas.job import GenerationJobCreate


def create_job(db: Session, payload: GenerationJobCreate) -> GenerationJob:
    job = GenerationJob(
        event_name=payload.event_name,
        certificate_title=payload.certificate_title,
        total_count=len(payload.recipients),
        status=JobStatus.PENDING,
    )
    job.recipients = [Recipient(name=r.name, email=str(r.email)) for r in payload.recipients]
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> GenerationJob | None:
    return db.scalar(select(GenerationJob).where(GenerationJob.id == job_id))


def calculate_progress(job: GenerationJob) -> float:
    if job.total_count == 0:
        return 100.0
    return round(((job.completed_count + job.failed_count) / job.total_count) * 100, 2)


def start_job(db: Session, job_id: str) -> None:
    job = get_job(db, job_id)
    if not job or job.status != JobStatus.PENDING:
        return
    job.status = JobStatus.PROCESSING
    db.commit()


def mark_success(db: Session, recipient: Recipient, path: str) -> None:
    recipient.status = RecipientStatus.SUCCESS
    recipient.certificate_path = path
    recipient.error_message = None
    job = recipient.job
    job.completed_count += 1
    db.commit()


def mark_failure(db: Session, recipient: Recipient, error: str) -> None:
    recipient.status = RecipientStatus.FAILED
    recipient.error_message = error[:2000]
    job = recipient.job
    job.failed_count += 1
    db.commit()


def finish_job(db: Session, job_id: str) -> None:
    job = get_job(db, job_id)
    if not job:
        return
    if job.failed_count == 0 and job.completed_count == job.total_count:
        job.status = JobStatus.COMPLETED
    elif job.completed_count + job.failed_count == job.total_count:
        job.status = JobStatus.COMPLETED_WITH_ERRORS
    else:
        job.status = JobStatus.FAILED
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
