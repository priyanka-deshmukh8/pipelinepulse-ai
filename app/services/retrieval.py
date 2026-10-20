"""Small, transparent lexical retrieval baseline; replace with embeddings/vector search in the next milestone."""
import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Incident

STOPWORDS = {"the", "and", "for", "with", "from", "this", "that", "was", "were", "into", "error", "failed", "failure"}

def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(t) > 2 and t not in STOPWORDS}

def find_similar_incidents(db: Session, incident: Incident, limit: int = 3) -> list[Incident]:
    candidates = db.scalars(
        select(Incident).where(Incident.id != incident.id, Incident.status.in_(["resolved", "closed"]))
        .order_by(Incident.created_at.desc()).limit(100)
    ).all()
    query_tokens = tokens(f"{incident.pipeline_name} {incident.error_message}")
    ranked = []
    for candidate in candidates:
        candidate_tokens = tokens(f"{candidate.pipeline_name} {candidate.error_message} {candidate.root_cause or ''} {candidate.remediation or ''}")
        score = len(query_tokens & candidate_tokens) / max(1, len(query_tokens | candidate_tokens))
        if score > 0:
            ranked.append((score, candidate))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]
