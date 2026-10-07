# Bulk Certificate Generator API

A production-oriented FastAPI backend for submitting bulk certificate-generation jobs, validating recipients, generating PDF certificates from a predefined template, tracking per-recipient outcomes, and downloading successful certificates.

## Why this design

The API is job-oriented because a single client request can contain many recipients. Each recipient is processed independently, so one generation failure does not stop the remaining valid recipients.

### Architecture

```text
Client
  |
  | POST /api/jobs
  v
FastAPI
  |
  +--> Pydantic validation
  |
  +--> PostgreSQL / SQLAlchemy
  |       |
  |       +--> generation_jobs
  |       +--> recipients
  |
  +--> Background task
          |
          +--> validate/process each recipient independently
          +--> ReportLab PDF generation
          +--> update recipient status
          +--> update aggregate job progress
```

## Technology

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Pydantic v2
- ReportLab
- pytest
- Docker / Docker Compose

## Requirements

- Python 3.12+
- Docker Desktop (recommended) or PostgreSQL

## Run with Docker

```bash
git clone <your-repository-url>
cd bulk-certificate-generator
cp .env.example .env
docker compose up --build
```

The API will be available at:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## Run locally without Docker

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `DATABASE_URL` to a PostgreSQL database, then run:

```bash
uvicorn app.main:app --reload
```

For quick local experimentation, the application also supports SQLite when `DATABASE_URL=sqlite:///./certificates.db`, although PostgreSQL is the intended deployment database.

## API

### 1. Create a generation job

`POST /api/jobs`

Example:

```json
{
  "event_name": "Aereo Python Workshop",
  "certificate_title": "Certificate of Completion",
  "recipients": [
    {
      "name": "Abhinav Sai",
      "email": "abhinav@example.com"
    },
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    }
  ]
}
```

The endpoint returns `202 Accepted` because generation is processed asynchronously.

Example response:

```json
{
  "id": "job-uuid",
  "event_name": "Aereo Python Workshop",
  "certificate_title": "Certificate of Completion",
  "status": "PENDING",
  "total_count": 2,
  "completed_count": 0,
  "failed_count": 0,
  "progress": 0.0,
  "created_at": "2026-10-07T12:00:00Z",
  "completed_at": null
}
```

### 2. Check job status

`GET /api/jobs/{job_id}`

The `progress` value represents the percentage of recipients that have reached a terminal state (`SUCCESS` or `FAILED`).

Possible job statuses:

- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `COMPLETED_WITH_ERRORS`
- `FAILED`

### 3. List certificate results

`GET /api/jobs/{job_id}/certificates`

Each recipient exposes its own status and, when successful, a download URL.

Possible recipient statuses:

- `PENDING`
- `PROCESSING`
- `SUCCESS`
- `FAILED`

### 4. Download a certificate

`GET /api/certificates/{certificate_id}`

Successful certificates are returned as PDF files.

## Validation and failure handling

Input is validated with Pydantic. Recipient names are normalized and emails are validated before a job is accepted.

During generation, every recipient is processed in an isolated `try/except` block. If one certificate fails, its error is stored against that recipient and processing continues for the remaining recipients.

For example:

```text
100 recipients
97 SUCCESS
3 FAILED

Job status: COMPLETED_WITH_ERRORS
Progress: 100%
```

This design directly addresses the requirement that an individual certificate failure should not unnecessarily prevent other valid certificates from being generated.

## Certificate template

A single predefined certificate template is implemented with ReportLab. The template contains:

- Certificate title
- Recipient name
- Event name
- Unique certificate ID

The template is deliberately generated in code so the repository remains self-contained and does not depend on an external binary template file.

## Database design

### `generation_jobs`

Stores the aggregate request/job:

- job ID
- event name
- certificate title
- status
- total count
- completed count
- failed count
- timestamps

### `recipients`

Stores the individual work items:

- recipient ID
- job ID
- name
- email
- status
- error message
- generated certificate path
- timestamp

The one-to-many relationship allows the API to report both aggregate progress and detailed per-recipient results.

## Testing

Run:

```bash
pytest -q
```

The test suite covers:

- Health endpoint
- Job creation
- Input validation
- Missing job handling
- Certificate PDF generation
- Progress calculation
- Individual recipient failure handling
- `COMPLETED_WITH_ERRORS` job state

## Design decisions

### Why FastAPI?

FastAPI provides strong request validation through Pydantic, automatic OpenAPI documentation, clear dependency injection, and good performance for API workloads.

### Why PostgreSQL?

The assignment requires a relational database. PostgreSQL is a production-grade relational database with strong transactional behavior and good support for structured job data.

### Why SQLAlchemy?

SQLAlchemy provides a clear ORM/data-access layer while retaining the ability to use PostgreSQL-specific capabilities when needed.

### Why background processing?

Bulk generation can take substantially longer than a normal API request. Returning `202 Accepted` and processing the job separately prevents the client from having to hold an HTTP connection open for the entire generation operation.

For this assignment, FastAPI `BackgroundTasks` keeps the system simple and avoids unnecessary infrastructure. For a multi-instance production deployment, a durable queue such as Celery/RQ with Redis or another managed queue would be preferable.

### Why per-recipient status?

A bulk operation should not be treated as all-or-nothing because one malformed recipient or one rendering problem should not block valid recipients. Individual status and error fields make failures observable and retryable.

### Why filesystem storage?

The assignment only requires generated certificates to be retrievable. Local filesystem storage keeps the implementation straightforward. A production deployment across multiple instances should use object storage such as S3-compatible storage and store object keys rather than local paths.

## Security and reliability considerations

- Secrets are provided through environment variables.
- `.env` is ignored by Git.
- Certificate downloads validate that the resolved path remains inside the configured storage directory.
- Input sizes are bounded by a maximum of 5,000 recipients per job.
- Individual generation failures are isolated.
- Database connections use `pool_pre_ping`.

## Future scope

1. Replace FastAPI BackgroundTasks with a durable worker queue.
2. Add Redis for queueing and distributed job processing.
3. Move PDFs to S3/object storage.
4. Add authentication and role-based access control.
5. Add job cancellation and retry APIs.
6. Add pagination for large recipient lists.
7. Add structured JSON logging and metrics.
8. Add database migrations with Alembic.
9. Add rate limiting and request quotas.
10. Add an email-delivery integration for sending certificates automatically.
11. Add Docker image scanning and CI/CD checks.

## Learning

This project demonstrates practical backend engineering concepts including REST API design, schema validation, relational data modeling, background processing, file generation, failure isolation, automated testing, Dockerization, and API documentation.

## Example curl request

```bash
curl -X POST http://localhost:8000/api/jobs \\
  -H "Content-Type: application/json" \\
  -d '{
    "event_name": "Aereo Python Workshop",
    "certificate_title": "Certificate of Completion",
    "recipients": [
      {"name": "Abhinav Sai", "email": "abhinav@example.com"},
      {"name": "Rahul Kumar", "email": "rahul@example.com"}
    ]
  }'
```

Then poll the returned job ID:

```bash
curl http://localhost:8000/api/jobs/<JOB_ID>
```

When generation finishes:

```bash
curl http://localhost:8000/api/jobs/<JOB_ID>/certificates
```

Download a successful certificate using the returned certificate ID:

```bash
curl -o certificate.pdf http://localhost:8000/api/certificates/<CERTIFICATE_ID>
```
