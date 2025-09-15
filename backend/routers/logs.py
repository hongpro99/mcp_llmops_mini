from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.db import get_db

router = APIRouter()

@router.get("/logs", response_model=list[schemas.ChatLog])
def get_logs(db: Session = Depends(get_db)):
    return db.query(models.ChatLog).all()
