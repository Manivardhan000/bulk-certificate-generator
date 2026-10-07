from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.job import GenerationJobCreate, GenerationJobDetail, GenerationJobResponse, RecipientResponse
from app.services.job_service import calculate_progress, create_job, get_job
from app.workers.generator import process_generation_job

router = APIRouter(prefix="/api/jobs", tags=["Generation Jobs"])


def job_response(job) -> GenerationJobResponse:
    return GenerationJobResponse(
        id=job.id,
        event_name=job.event_name,
        certificate_title=job.certificate_title,
        status=job.status,
        total_count=job.total_count,
        completed_count=job.completed_count,
        failed_count=job.failed_count,
        progress=calculate_progress(job),
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.post("", response_model=GenerationJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_generation_job(payload: GenerationJobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = create_job(db, payload)
    background_tasks.add_task(process_generation_job, job.id)
    return job_response(job)


@router.get("/{job_id}", response_model=GenerationJobResponse)
def get_generation_job(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job_response(job)


@router.get("/{job_id}/certificates", response_model=list[RecipientResponse])
def list_job_certificates(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return [
        RecipientResponse(
            id=r.id,
            name=r.name,
            email=r.email,
            status=r.status,
            error_message=r.error_message,
            download_url=f"/api/certificates/{r.id}" if r.certificate_path else None,
        )
        for r in job.recipients
    ]
