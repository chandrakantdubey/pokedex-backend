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

class PokemonCreate(PokemonBase):
    pass

class PokemonDetail(PokemonBase):
    moves_learned: List[MoveBase] = []

# --- World Models ---
class GymBase(BaseModel):
    name: str
    location: str
    leader_name: str
    type_specialty: str
    badge_name: str
    badge_image_url: Optional[str] = None

class GymCreate(GymBase):
    pass

class Gym(GymBase):
    id: int
    class Config:
        from_attributes = True

class EliteFourMemberBase(BaseModel):
    name: str
    rank: int
    specialty_type: str
    image_url: Optional[str] = None

class EliteFourMemberCreate(EliteFourMemberBase):
    pass

class EliteFourMember(EliteFourMemberBase):
    id: int
    class Config:
        from_attributes = True

class UserBadgeBase(BaseModel):
    gym_id: int

class UserBadge(UserBadgeBase):
    id: int
    user_id: int
    earned_at: datetime
    gym: Optional[Gym] = None
    class Config:
        from_attributes = True

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
    next_level_xp: Optional[int] = 0 # Computed field
    pokemon: PokemonBase

    class Config:
        from_attributes = True

class UserPokemonCreate(BaseModel):
    pokemon_id: int
    nickname: Optional[str] = None

class BattleHistoryBase(BaseModel):
    opponent_name: str
    result: str 
    money_earned: int = 0

class BattleHistoryCreate(BattleHistoryBase):
    pass

class BattleHistory(BattleHistoryBase):
    id: int
    user_id: int
    battle_date: datetime
    class Config:
        from_attributes = True

class PartyUpdateRequest(BaseModel):
    user_pokemon_id: int
    is_in_party: bool

class XPUpdate(BaseModel):
    xp_amount: int

# --- Shop Models ---
class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True

class UserItemBase(BaseModel):
    item_id: int
    quantity: int

class UserItem(UserItemBase):
    id: int
    user_id: int
    item: Optional[Item] = None
    class Config:
        from_attributes = True

class BuyItemRequest(BaseModel):
    item_id: int
    quantity: int

# --- User Favorites ---
class UserFavoriteBase(BaseModel):
    pokemon_id: int

class UserFavoriteCreate(UserFavoriteBase):
    pass

class UserFavorite(UserFavoriteBase):
    id: int
    user_id: int
    pokemon: Optional[PokemonBase] = None
    
    class Config:
        from_attributes = True

# --- Aliases ---
User = UserDisplay
UserPokemon = UserPokemonDisplay
Pokemon = PokemonDetail
