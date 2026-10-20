from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Incident
from app.schemas import IncidentCreate, IncidentRead, AnalysisResult, RetryUpdate, IncidentStatusUpdate
from app.services.analysis import analyze_incident

router = APIRouter()

@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(pipeline_name=payload.pipeline_name.strip(), error_message=payload.error_message.strip())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("", response_model=list[IncidentRead])
def list_incidents(
    status: str | None = Query(default=None, pattern="^(open|investigating|resolved|closed)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Incident).order_by(Incident.created_at.desc()).offset(offset).limit(limit)
    if status:
        stmt = stmt.where(Incident.status == status)
    return db.scalars(stmt).all()

@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/analyze", response_model=AnalysisResult)
def analyze(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return analyze_incident(db, incident)

@router.post("/{incident_id}/retry-count", response_model=IncidentRead)
def increment_retry_count(incident_id: int, payload: RetryUpdate, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.retry_count += payload.increment_by
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.patch("/{incident_id}/status", response_model=IncidentRead)
def update_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
