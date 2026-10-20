from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class IncidentCreate(BaseModel):
    pipeline_name: str = Field(min_length=1, max_length=200)
    error_message: str = Field(min_length=1, max_length=10000)

class IncidentAnalyzeRequest(BaseModel):
    include_historical_context: bool = True

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
    similar_incidents: list[dict]
    requires_human_review: bool = True

class RetryUpdate(BaseModel):
    increment_by: int = Field(default=1, ge=1, le=10)

class IncidentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(open|investigating|resolved|closed)$")
