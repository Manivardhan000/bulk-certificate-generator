from app.models import GenerationJob, JobStatus, Recipient, RecipientStatus
from app.services.job_service import calculate_progress, create_job, finish_job, mark_failure, mark_success, start_job
from app.schemas.job import GenerationJobCreate


def test_job_progress_and_failure_isolation(db_session, tmp_path, monkeypatch):
    payload = GenerationJobCreate(
        event_name="Test Event",
        recipients=[
            {"name": "Alice Example", "email": "alice@example.com"},
            {"name": "Bob Example", "email": "bob@example.com"},
        ],
    )
    job = create_job(db_session, payload)
    start_job(db_session, job.id)
    assert job.status == JobStatus.PROCESSING

    recipients = list(job.recipients)
    mark_success(db_session, recipients[0], str(tmp_path / "alice.pdf"))
    mark_failure(db_session, recipients[1], "template rendering failed")
    db_session.refresh(job)

    assert job.completed_count == 1
    assert job.failed_count == 1
    assert calculate_progress(job) == 100.0
    finish_job(db_session, job.id)
    db_session.refresh(job)
    assert job.status == JobStatus.COMPLETED_WITH_ERRORS
    assert recipients[1].status == RecipientStatus.FAILED
    assert recipients[1].error_message == "template rendering failed"
