# Bulk Certificate Generator

A FastAPI-based backend for generating certificates in bulk.

This project makes it easier to generate certificates for multiple participants at once instead of creating each certificate manually. Users can submit a certificate generation job with multiple recipients, and the application processes them in the background, generates PDF certificates, tracks the progress, and allows successfully generated certificates to be downloaded.

## What This Project Does

Imagine conducting a workshop with 100 participants and needing to generate a certificate for every participant.

Instead of creating 100 certificates manually, this application allows you to submit all the participants together as one job.

The application then:

- Accepts multiple recipients in one request
- Validates recipient information
- Creates a certificate generation job
- Processes recipients independently
- Generates PDF certificates
- Tracks the progress of the job
- Keeps track of successful and failed certificates
- Allows generated certificates to be downloaded

If one recipient fails, the remaining recipients can still be processed.

## How It Works

The basic flow of the application is:

Client
  |
  | POST /api/jobs
  v
FastAPI
  |
  | Validate request
  v
Database
  |
  | Create job and recipients
  v
Background Worker
  |
  | Process recipients
  v
Certificate Generator
  |
  | Generate PDF
  v
Update Recipient Status
  |
  v
Update Job Progress

The API returns a unique job ID when a certificate generation request is submitted.

The client can then use that job ID to check the progress of the generation job.

## Main Features

### Bulk Certificate Generation

Multiple recipients can be submitted in a single request.

Example request:

    {
      "event_name": "Aero Python Workshop",
      "certificate_title": "Certificate of Completion",
      "recipients": [
        {
          "name": "Mani",
          "email": "Mani@example.com"
        },
        {
          "name": "Rahul Kumar",
          "email": "rahul@example.com"
        }
      ]
    }

### Background Processing

Certificate generation is processed in the background.

Instead of making the client wait until every certificate is generated, the API immediately creates the job and returns a job ID.

The API responds with:

    202 Accepted

The client can use the returned job ID to check the current status.

### Independent Recipient Processing

Each recipient is processed separately.

For example, if there are 10 recipients and one certificate fails, the remaining 9 certificates can still be generated.

This prevents a single invalid recipient from stopping the complete batch.

### Progress Tracking

The application keeps track of:

- Total recipients
- Completed certificates
- Failed certificates
- Current job status
- Overall progress

### PDF Certificate Generation

Certificates are generated as PDF files using predefined templates.

The project uses ReportLab for PDF generation.

### Database Support

SQLAlchemy is used for database operations.

PostgreSQL is recommended for production use.

SQLite is also supported for local development and testing.

## Technology Stack

The project is built using:

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- PostgreSQL
- SQLite
- ReportLab
- Pytest
- Docker
- Docker Compose

### Why These Technologies?

Python is used as the main programming language.

FastAPI is used to build the REST API.

Pydantic is used for request validation.

SQLAlchemy is used to communicate with the database.

PostgreSQL is the recommended database for production.

SQLite can be used for local development and testing.

ReportLab is used to generate PDF certificates.

Pytest is used for automated testing.

Docker and Docker Compose are used to simplify setup and deployment.

## Project Structure

    bulk-certificate-generator/
    │
    ├── app/
    │   ├── api/
    │   ├── core/
    │   ├── db/
    │   ├── models/
    │   ├── schemas/
    │   ├── services/
    │   ├── workers/
    │   ├── __init__.py
    │   └── main.py
    │
    ├── generated/
    │   └── Generated certificate files
    │
    ├── templates/
    │   └── Certificate templates
    │
    ├── tests/
    │   ├── test_api.py
    │   ├── test_certificate_service.py
    │   └── test_worker.py
    │
    ├── .env.example
    ├── .gitignore
    ├── certificates.db
    ├── docker-compose.yml
    ├── Dockerfile
    ├── pyproject.toml
    ├── README.md
    └── requirements.txt

## Requirements

Before running the project, make sure you have:

- Python 3.12 or later
- Git
- Docker Desktop (recommended)

For local development, PostgreSQL can also be installed separately.

## Running With Docker

Docker is the easiest way to run the application.

### 1. Clone the Repository

    git clone https://github.com/Manivardhan000/bulk-certificate-generator.git

### 2. Open the Project Directory

    cd bulk-certificate-generator

### 3. Create the Environment File

On Windows PowerShell:

    Copy-Item .env.example .env

On macOS/Linux:

    cp .env.example .env

### 4. Start the Application

    docker compose up --build

After the containers start successfully, the API will be available at:

    http://localhost:8000

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

    http://localhost:8000/docs

### ReDoc

    http://localhost:8000/redoc

### Health Check

    http://localhost:8000/health

The health endpoint can be used to quickly check whether the API is running.

## Running Locally Without Docker

If you don't want to use Docker, you can run the application directly with Python.

### 1. Create a Virtual Environment

    python -m venv .venv

### 2. Activate the Virtual Environment

Windows:

    .venv\Scripts\activate

macOS/Linux:

    source .venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Configure the Database

Create a .env file using .env.example.

For PostgreSQL:

    DATABASE_URL=postgresql://username:password@localhost:5432/certificates

For SQLite:

    DATABASE_URL=sqlite:///./certificates.db

### 5. Start the Application

    uvicorn app.main:app --reload

The API will be available at:

    http://localhost:8000

## API Usage

### Create a Certificate Generation Job

Endpoint:

    POST /api/jobs

Example request:

    {
      "event_name": "Aero Python Workshop",
      "certificate_title": "Certificate of Completion",
      "recipients": [
        {
          "name": "Mani",
          "email": "Mani@example.com"
        },
        {
          "name": "Rahul Kumar",
          "email": "rahul@example.com"
        }
      ]
    }

The API creates a new job and starts processing the certificates in the background.

A successful request returns:

    202 Accepted

The response contains a unique job ID.

## Check Job Status

Endpoint:

    GET /api/jobs/{job_id}

Replace {job_id} with the ID returned when the job was created.

Example response:

    {
      "id": "job-uuid",
      "event_name": "Aero Python Workshop",
      "certificate_title": "Certificate of Completion",
      "status": "PROCESSING",
      "total_count": 2,
      "completed_count": 1,
      "failed_count": 0,
      "progress": 50
    }

The progress value represents the percentage of recipients that have reached a final state.

Possible job statuses include:

    PENDING
    PROCESSING
    COMPLETED
    COMPLETED_WITH_ERRORS
    FAILED

## Download a Certificate

After a certificate has been generated successfully, it can be downloaded using:

    GET /api/certificates/{certificate_id}

The API returns the generated certificate as a PDF file.

## Certificate Generation Process

The certificate generation process uses a predefined template.

For each recipient, the worker:

1. Reads the recipient information
2. Validates the data
3. Loads the certificate template
4. Generates the PDF
5. Saves the generated certificate
6. Updates the recipient status
7. Updates the overall job progress

The API request and certificate generation process are separated so that the API can remain responsive while certificates are being generated.

## Error Handling

The application is designed to handle failures at the individual recipient level.

For example:

    Total recipients: 5
    Successful: 4
    Failed: 1

The remaining certificates can still be generated even if one recipient fails.

The final job status can be:

    COMPLETED_WITH_ERRORS

This approach is useful when processing large batches of certificates.

## Testing

The project uses Pytest for automated testing.

Run the complete test suite using:

    pytest -v

The tests cover important parts of the application, including:

- API endpoints
- Certificate generation
- Background worker processing

Example result:

    6 passed

## Database

The application uses SQLAlchemy for database operations.

PostgreSQL is recommended for production deployments.

SQLite can be used for local development and testing.

A local SQLite database file is included in the project:

    certificates.db

This can be useful for local experimentation.

For production deployments, PostgreSQL should be preferred.

## Environment Variables

The application uses environment variables for configuration.

Create a .env file based on .env.example.

Example:

    DATABASE_URL=postgresql://username:password@localhost:5432/certificates

Do not commit passwords, API keys, tokens, or other sensitive information to GitHub.

## Docker Commands

Start the application:

    docker compose up --build

Stop the application:

    docker compose down

Run the application in the background:

    docker compose up -d

## Why I Built This

Generating certificates manually can become repetitive and time-consuming when an event has a large number of participants.

This project was built to automate that process and explore how a backend application can handle bulk processing while keeping the API responsive.

While building this project, I worked with:

- REST APIs
- FastAPI
- Database design
- SQLAlchemy
- Background processing
- PDF generation
- Docker
- Automated testing
- Error handling

## Future Improvements

Some features that could be added in the future include:

- User authentication
- Multiple certificate templates
- Email delivery of certificates
- Web-based dashboard
- Job cancellation
- Retry support for failed certificates
- Cloud storage for generated certificates
- Redis/Celery-based distributed workers
- Better monitoring and logging
- Cloud deployment
- Certificate verification through a unique ID or QR code

## Author

Mani Vardhan

Backend / Full-Stack Developer

## License

This project is created for learning, development, and demonstration purposes.
