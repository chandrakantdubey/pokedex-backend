from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association Tables
pokemon_types = Table(
    "pokemon_types_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("type_id", Integer, ForeignKey("types.id"))
)

pokemon_abilities = Table(
    "pokemon_abilities_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("ability_id", Integer, ForeignKey("abilities.id")),
    Column("is_hidden", Boolean, default=False)
)

pokemon_egg_groups = Table(
    "pokemon_egg_groups_association",
    Base.metadata,
    Column("species_id", Integer, ForeignKey("pokemon_species.id")),
    Column("egg_group_id", Integer, ForeignKey("egg_groups.id"))
)

# Core Metadata Models
class Generation(Base):
    __tablename__ = "generations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # generation-i, etc.

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    
class Stat(Base):
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class EggGroup(Base):
    __tablename__ = "egg_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class GrowthRate(Base):
    __tablename__ = "growth_rates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    formula = Column(String, nullable=True)

class Nature(Base):
    __tablename__ = "natures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    increased_stat_id = Column(Integer, ForeignKey("stats.id"), nullable=True)
    decreased_stat_id = Column(Integer, ForeignKey("stats.id"), nullable=True)

class Ability(Base):
    __tablename__ = "abilities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    effect = Column(String, nullable=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)

# Pokemon Data models
class PokemonSpecies(Base):
    __tablename__ = "pokemon_species"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    order = Column(Integer)
    gender_rate = Column(Integer) # -1 genderless, 0-8 scale
    capture_rate = Column(Integer)
    base_happiness = Column(Integer)
    is_baby = Column(Boolean)
    hatch_counter = Column(Integer)
    has_gender_differences = Column(Boolean)
    growth_rate_id = Column(Integer, ForeignKey("growth_rates.id"))
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    evolves_from_species_id = Column(Integer, ForeignKey("pokemon_species.id"), nullable=True)
    evolution_chain_id = Column(Integer, nullable=True) # Just ID for now, complex to model fully
    
    growth_rate = relationship("GrowthRate")
    generation = relationship("Generation")
    egg_groups = relationship("EggGroup", secondary=pokemon_egg_groups)
    varieties = relationship("Pokemon", back_populates="species")
    parent_species = relationship("PokemonSpecies", remote_side=[id])

class Pokemon(Base):
    __tablename__ = "pokemon"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    species_id = Column(Integer, ForeignKey("pokemon_species.id"))
    height = Column(Integer)
    weight = Column(Integer)
    base_experience = Column(Integer)
    order = Column(Integer)
    is_default = Column(Boolean)
    
    # Store sprites as JSON for flexibility
    sprites = Column(JSON)
    # Store stats as JSON for simple access, but could also relate to Stat table
    stats = Column(JSON) 
    
    species = relationship("PokemonSpecies", back_populates="varieties")
    types = relationship("Type", secondary=pokemon_types)
    abilities = relationship("Ability", secondary=pokemon_abilities)
    moves = relationship("PokemonMove", back_populates="pokemon")

# Moves
class Move(Base):
    __tablename__ = "moves"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type_id = Column(Integer, ForeignKey("types.id"), nullable=True)
    power = Column(Integer, nullable=True)
    pp = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    priority = Column(Integer, default=0)
    damage_class = Column(String, nullable=True) # physical, special, status
    effect_cvhance = Column(Integer, nullable=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    
    type = relationship("Type")
    generation = relationship("Generation")

class PokemonMove(Base):
    __tablename__ = "pokemon_moves"
    pokemon_id = Column(Integer, ForeignKey("pokemon.id"), primary_key=True)
    move_id = Column(Integer, ForeignKey("moves.id"), primary_key=True)
    learn_method = Column(String) # level-up, machine, etc
    level_learned_at = Column(Integer, nullable=True)
    
    pokemon = relationship("Pokemon", back_populates="moves")
    move = relationship("Move")

# Items & Berries
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cost = Column(Integer)
    fling_power = Column(Integer, nullable=True)
    category_name = Column(String) # Store name directly
    effect = Column(String, nullable=True)
    sprite_url = Column(String, nullable=True)

class Berry(Base):
    __tablename__ = "berries"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    name = Column(String, index=True)
    growth_time = Column(Integer)
    max_harvest = Column(Integer)
    natural_gift_power = Column(Integer)
    size = Column(Integer)
    smoothness = Column(Integer)
    soil_dryness = Column(Integer)
    firmness_name = Column(String) # soft, hard, etc.
    
    item = relationship("Item")

# User & Gameplay Models (Preserved)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    money = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pokemons = relationship("UserPokemon", back_populates="owner")
    battles = relationship("BattleHistory", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
    items = relationship("UserItem", back_populates="user")
    favorites = relationship("UserFavorite", back_populates="user")

class UserPokemon(Base):
    __tablename__ = "user_pokemon"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pokemon_id = Column(Integer, ForeignKey("pokemon.id"))
    nickname = Column(String, nullable=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    acquired_at = Column(DateTime, default=datetime.utcnow)
    is_in_party = Column(Boolean, default=False)

    owner = relationship("User", back_populates="pokemons")
    pokemon = relationship("Pokemon")

class BattleHistory(Base):
    __tablename__ = "battle_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opponent_name = Column(String)
    result = Column(String)
    money_earned = Column(Integer)
    battle_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="battles")

class Gym(Base):
    __tablename__ = "gyms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    leader_name = Column(String)
    type_specialty = Column(String)
    badge_name = Column(String)
    badge_image_url = Column(String)

class EliteFourMember(Base):
    __tablename__ = "elite_four"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rank = Column(Integer)
    specialty_type = Column(String)
    image_url = Column(String)

class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gym_id = Column(Integer, ForeignKey("gyms.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="badges")
    gym = relationship("Gym")

class UserItem(Base):
    __tablename__ = "user_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="items")
    item = relationship("Item")

class UserFavorite(Base):
    __tablename__ = "user_favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pokemon_id = Column(Integer, ForeignKey("pokemon.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    pokemon = relationship("Pokemon")
