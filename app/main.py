from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Lead
from app.priority import calculate_priority, now_moscow
from app.schemas import LeadCreate, LeadRead, Priority


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Дом и Уют — заявки", lifespan=lifespan)


@app.post("/leads", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    created_at = payload.created_at or now_moscow()
    if created_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="created_at must include a timezone offset")

    priority = calculate_priority(
        source=payload.source,
        text=payload.text,
        amount=payload.amount,
        created_at=created_at,
    )
    lead = Lead(
        source=payload.source,
        text=payload.text,
        amount=payload.amount,
        created_at=created_at,
        priority=priority,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@app.get("/leads/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.get("/leads", response_model=list[LeadRead])
def list_leads(
    priority: Priority | None = Query(default=None), db: Session = Depends(get_db)
) -> list[Lead]:
    priority_order = case(
        (Lead.priority == Priority.HIGH, 1),
        (Lead.priority == Priority.MEDIUM, 2),
        else_=3,
    )
    query = select(Lead).order_by(priority_order, Lead.created_at.desc())
    if priority is not None:
        query = query.where(Lead.priority == priority)
    return list(db.scalars(query))
