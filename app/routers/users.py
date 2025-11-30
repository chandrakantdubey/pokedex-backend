from fastapi import APIRouter, Depends
from .. import schemas, models, dependencies

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user

@router.get("/favorites", response_model=list[schemas.UserFavorite])
def read_favorites(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    from .. import crud
    return crud.get_user_favorites(db, user_id=current_user.id)

@router.post("/favorites", response_model=schemas.UserFavorite)
def add_favorite(favorite: schemas.UserFavoriteCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    from .. import crud
    return crud.add_user_favorite(db, user_id=current_user.id, pokemon_id=favorite.pokemon_id)

@router.delete("/favorites/{pokemon_id}")
def remove_favorite(pokemon_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    from .. import crud
    success = crud.remove_user_favorite(db, user_id=current_user.id, pokemon_id=pokemon_id)
    return {"success": success}
