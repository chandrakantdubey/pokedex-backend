from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Move Schemas
class MoveBase(BaseModel):
    name: str
    type: str
    power: Optional[int] = None
    accuracy: Optional[int] = None
    pp: Optional[int] = None
    damage_class: Optional[str] = None

class Move(MoveBase):
    id: int

    class Config:
        from_attributes = True

class PokemonMoveBase(BaseModel):
    learn_method: str
    level_learned_at: Optional[int] = None
    move: Move

    class Config:
        from_attributes = True

# Pokemon Schemas
class PokemonBase(BaseModel):
    name: str
    height: int
    weight: int
    types: List[str]
    stats: Dict[str, int]
    sprites: Dict[str, Any]
    abilities: List[str]
    growth_rate: Optional[str] = None
    evolution_trigger: Optional[str] = None

class PokemonCreate(PokemonBase):
    pass

class Pokemon(PokemonBase):
    id: int
    evolves_from_id: Optional[int] = None
    moves: List[PokemonMoveBase] = []

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    money: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Game Schemas
class UserPokemonBase(BaseModel):
    pokemon_id: int
    nickname: Optional[str] = None

class UserPokemonCreate(UserPokemonBase):
    pass

class UserPokemon(UserPokemonBase):
    id: int
    user_id: int
    level: int
    experience: int
    acquired_at: datetime
    pokemon: Pokemon
    next_level_xp: Optional[int] = None # Calculated field
    is_in_party: bool

    class Config:
        from_attributes = True

class BattleHistoryBase(BaseModel):
    opponent_name: str
    result: str
    money_earned: int

class BattleHistoryCreate(BattleHistoryBase):
    pass

class BattleHistory(BattleHistoryBase):
    id: int
    user_id: int
    battle_date: datetime

    class Config:
        from_attributes = True

# World Schemas
class GymBase(BaseModel):
    name: str
    location: str
    leader_name: str
    type_specialty: str
    badge_name: str
    badge_image_url: str

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
    image_url: str

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
    gym: Gym

    class Config:
        from_attributes = True

# Shop Schemas
class ItemBase(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    category: str

class ItemCreate(ItemBase):
    pass

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
    item: Item

    class Config:
        from_attributes = True

class BuyItemRequest(BaseModel):
    item_id: int
    quantity: int = 1

class PartyUpdateRequest(BaseModel):
    user_pokemon_id: int
    is_in_party: bool

class XPUpdate(BaseModel):
    xp_amount: int
