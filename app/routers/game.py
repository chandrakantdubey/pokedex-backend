from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random
from .. import crud, schemas, models, dependencies
from ..game_logic import calculate_xp_for_level

router = APIRouter(
    prefix="/game",
    tags=["game"],
)

@router.post("/catch", response_model=schemas.UserPokemon)
def catch_pokemon(pokemon_data: schemas.UserPokemonCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    try:
        # Verify pokemon exists
        pokemon = crud.get_pokemon(db, pokemon_id=pokemon_data.pokemon_id)
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        
        # Check for Poke Ball (ID 1)
        # In a real app, we might allow different balls, but for now ID 1 is standard
        if not crud.remove_user_item(db, user_id=current_user.id, item_id=1, quantity=1):
            raise HTTPException(status_code=400, detail="No Poke Balls left!")
        
        
        user_pokemon = crud.add_user_pokemon(db=db, user_id=current_user.id, pokemon_id=pokemon_data.pokemon_id, nickname=pokemon_data.nickname)
        
        # Calculate next level XP
        growth_rate = pokemon.growth_rate or "medium-fast"
        user_pokemon.next_level_xp = calculate_xp_for_level(growth_rate, user_pokemon.level + 1)
        
        return user_pokemon
    except Exception as e:
        print(f"Error in catch_pokemon: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/my-pokemon", response_model=List[schemas.UserPokemon])
def read_my_pokemon(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    user_pokemons = crud.get_user_pokemons(db, user_id=current_user.id)
    
    # Enrich with XP data
    for up in user_pokemons:
        growth_rate = up.pokemon.growth_rate or "medium-fast"
        up.next_level_xp = calculate_xp_for_level(growth_rate, up.level + 1)
        
    return user_pokemons

@router.post("/battle", response_model=schemas.BattleHistory)
def record_battle(battle_data: schemas.BattleHistoryCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.add_battle_history(db=db, user_id=current_user.id, battle=battle_data)

@router.get("/party", response_model=List[schemas.UserPokemon])
def get_party(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    party = crud.get_user_party(db, user_id=current_user.id)
    
    # Enrich with XP data
    for up in party:
        growth_rate = up.pokemon.growth_rate or "medium-fast"
        up.next_level_xp = calculate_xp_for_level(growth_rate, up.level + 1)
        
    return party

@router.post("/party/set", response_model=schemas.UserPokemon)
def set_party_status(update_request: schemas.PartyUpdateRequest, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    user_pokemon = crud.get_user_pokemon(db, user_pokemon_id=update_request.user_pokemon_id)
    if not user_pokemon or user_pokemon.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Pokemon not found in your collection")
    
    # Check party limit if adding
    if update_request.is_in_party:
        current_party = crud.get_user_party(db, user_id=current_user.id)
        if len(current_party) >= 6:
            raise HTTPException(status_code=400, detail="Party is full (max 6)")
            
    return crud.update_party_status(db, user_pokemon, update_request.is_in_party)

@router.get("/encounter", response_model=schemas.Pokemon)
def wild_encounter(db: Session = Depends(dependencies.get_db)):
    # Simple random encounter logic
    # In a real app, this would be based on location/rarity
    # Get total count (approx) or pick random ID
    # Since IDs are 1-1010, pick random
    random_id = random.randint(1, 151) # Stick to Gen 1 for safety if scraper incomplete
    pokemon = crud.get_pokemon(db, pokemon_id=random_id)
    if not pokemon:
        # Fallback
        pokemon = crud.get_pokemon(db, pokemon_id=1)
        
    return pokemon

@router.post("/pokemon/{user_pokemon_id}/xp", response_model=schemas.UserPokemon)
def gain_xp(user_pokemon_id: int, xp_data: schemas.XPUpdate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    user_pokemon = crud.get_user_pokemon(db, user_pokemon_id=user_pokemon_id)
    if not user_pokemon or user_pokemon.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Pokemon not found")
        
    updated_pokemon = crud.add_xp(db, user_pokemon_id, xp_data.xp_amount)
    
    # Enrich with next level XP for frontend
    growth_rate = updated_pokemon.pokemon.growth_rate or "medium-fast"
    updated_pokemon.next_level_xp = calculate_xp_for_level(growth_rate, updated_pokemon.level + 1)
    
    return updated_pokemon
