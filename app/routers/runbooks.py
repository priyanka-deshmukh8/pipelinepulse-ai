from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import RunbookCreate
from app.routers.auth import get_current_user
from app.models import User
from app.services.rag import add_knowledge, rag_is_configured

router = APIRouter(prefix="/api/v1/runbooks", tags=["Runbooks"])

@router.post("", status_code=201)
def ingest_runbook(payload: RunbookCreate, user: User = Depends(get_current_user)):
    if not rag_is_configured():
        raise HTTPException(status_code=503, detail="RAG is not configured. Set Azure OpenAI embedding deployment and vector connection.")
    try:
        vector_id = add_knowledge(
            f"Runbook: {payload.title}\nSource: {payload.source}\n\n{payload.content}",
            {"type": "runbook", "title": payload.title, "source": payload.source, "uploaded_by": user.email},
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Knowledge ingestion failed. Check vector database and embedding configuration.") from exc
    return {"status": "indexed", "vector_id": vector_id, "title": payload.title}
