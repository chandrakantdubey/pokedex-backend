from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
)

@router.get("/items", response_model=List[schemas.Item])
def read_items(db: Session = Depends(dependencies.get_db)):
    return crud.get_items(db)

@router.post("/buy", response_model=schemas.UserItem)
def buy_item(buy_request: schemas.BuyItemRequest, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    item = crud.get_item(db, item_id=buy_request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    total_cost = item.cost * buy_request.quantity
    
    if not crud.deduct_money(db, user_id=current_user.id, amount=total_cost):
        raise HTTPException(status_code=400, detail="Insufficient funds")
        
    return crud.add_user_item(db=db, user_id=current_user.id, item_id=buy_request.item_id, quantity=buy_request.quantity)

@router.get("/bag", response_model=List[schemas.UserItem])
def read_bag(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.get_user_items(db, user_id=current_user.id)
