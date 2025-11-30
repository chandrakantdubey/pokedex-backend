from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    height = Column(Integer)
    weight = Column(Integer)
    types = Column(JSON)
    stats = Column(JSON)
    sprites = Column(JSON)
    abilities = Column(JSON)
    growth_rate = Column(String, nullable=True)
    evolves_from_id = Column(Integer, ForeignKey("pokemon.id"), nullable=True)
    evolution_trigger = Column(String, nullable=True)

    moves = relationship("PokemonMove", back_populates="pokemon")
    parent = relationship("Pokemon", remote_side=[id], backref="evolutions")

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
    result = Column(String) # "win", "loss"
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
    rank = Column(Integer) # 1-4, 5=Champion
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

class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    power = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    pp = Column(Integer, nullable=True)
    damage_class = Column(String, nullable=True)

class PokemonMove(Base):
    __tablename__ = "pokemon_moves"

    pokemon_id = Column(Integer, ForeignKey("pokemon.id"), primary_key=True)
    move_id = Column(Integer, ForeignKey("moves.id"), primary_key=True)
    learn_method = Column(String) # level-up, machine, tutor
    level_learned_at = Column(Integer, nullable=True)

    pokemon = relationship("Pokemon", back_populates="moves")
    move = relationship("Move")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    category = Column(String) # pokeball, medicine, battle

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

# Update User relationship
User.favorites = relationship("UserFavorite", back_populates="user")
