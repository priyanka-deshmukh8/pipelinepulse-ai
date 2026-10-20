from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class IncidentCreate(BaseModel):
    pipeline_name: str = Field(min_length=1, max_length=200)
    error_message: str = Field(min_length=1, max_length=10000)

class RunbookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=20, max_length=20000)
    source: str = Field(default="user-provided", max_length=300)

class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pipeline_name: str
    error_message: str
    status: str
    failure_category: str
    root_cause: str | None
    remediation: str | None
    closure_note: str | None
    retry_count: int
    created_at: datetime
    updated_at: datetime

class AnalysisResult(BaseModel):
    incident_id: int
    failure_category: str
    root_cause: str
    remediation_steps: list[str]
    closure_note_draft: str
    evidence: list[dict]
    analysis_mode: str
    requires_human_review: bool = True

class RetryUpdate(BaseModel):
    increment_by: int = Field(default=1, ge=1, le=10)

class IncidentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(open|investigating|resolved|closed)$")
