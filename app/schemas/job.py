from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.job import JobStatus, RecipientStatus


class RecipientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("name must not be empty")
        return value


class GenerationJobCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    certificate_title: str = Field(default="Certificate of Completion", min_length=2, max_length=200)
    recipients: list[RecipientCreate] = Field(min_length=1, max_length=5000)

    @field_validator("event_name", "certificate_title")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class RecipientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str
    status: RecipientStatus
    error_message: str | None = None
    download_url: str | None = None


class GenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    event_name: str
    certificate_title: str
    status: JobStatus
    total_count: int
    completed_count: int
    failed_count: int
    progress: float
    created_at: datetime
    completed_at: datetime | None = None


class GenerationJobDetail(GenerationJobResponse):
    recipients: list[RecipientResponse]
