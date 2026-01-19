from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Base Models ---
class TypeBase(BaseModel):
    id: int
    name: str

class AbilityBase(BaseModel):
    id: int
    name: str
    effect: Optional[str] = None

class StatBase(BaseModel):
    id: int
    name: str

class EggGroupBase(BaseModel):
    id: int
    name: str

class GrowthRateBase(BaseModel):
    id: int
    name: str
    formula: Optional[str] = None

class NatureBase(BaseModel):
    id: int
    name: str
    increased_stat_id: Optional[int] = None
    decreased_stat_id: Optional[int] = None

# --- Item & Berry ---
class ItemBase(BaseModel):
    id: int
    name: str
    cost: Optional[int] = 0
    category_name: Optional[str] = None
    effect: Optional[str] = None
    sprite_url: Optional[str] = None

class BerryBase(BaseModel):
    id: int
    name: str
    growth_time: int
    max_harvest: int
    size: int
    smoothness: int
    soil_dryness: int
    firmness_name: str
    item: Optional[ItemBase] = None

# --- Pokemon Models ---
class PokemonSpeciesBase(BaseModel):
    id: int
    name: str
    order: Optional[int] = None
    gender_rate: Optional[int] = None
    capture_rate: Optional[int] = None
    base_happiness: Optional[int] = None
    is_baby: Optional[bool] = False
    growth_rate: Optional[GrowthRateBase] = None
    
    class Config:
        from_attributes = True

class MoveBase(BaseModel):
    id: int
    name: str
    type_id: Optional[int] = None
    power: Optional[int] = None
    accuracy: Optional[int] = None
    pp: Optional[int] = None
    damage_class: Optional[str] = None
    
    class Config:
        from_attributes = True

class PokemonBase(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    base_experience: Optional[int] = None
    types: List[TypeBase] = []
    abilities: List[AbilityBase] = []
    stats: Optional[Dict[str, Any]] = None 
    sprites: Optional[Dict[str, Any]] = None
    species: Optional[PokemonSpeciesBase] = None

    class Config:
        from_attributes = True

class PokemonDetail(PokemonBase):
    moves_learned: List[MoveBase] = [] 

# --- User & Game Models ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserDisplay(UserBase):
    id: int
    is_active: bool
    money: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserPokemonDisplay(BaseModel):
    id: int
    nickname: Optional[str] = None
    level: int
    experience: int
    pokemon: PokemonBase
    
    class Config:
        from_attributes = True
