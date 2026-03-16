from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies
from typing import List

router = APIRouter(
    prefix="/berries",
    tags=["berries"],
)

@router.get("/", response_model=List[schemas.BerryBase])
def read_berries(db: Session = Depends(dependencies.get_db)):
    return crud.get_berries(db)
