from sqlalchemy.orm import Session
from . import models, schemas, auth

# Pokemon
def get_pokemon(db: Session, pokemon_id: int):
    return db.query(models.Pokemon).filter(models.Pokemon.id == pokemon_id).first()

def get_pokemons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pokemon).offset(skip).limit(limit).all()

def create_pokemon(db: Session, pokemon: schemas.PokemonCreate):
    db_pokemon = models.Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

# User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    # Initial money: 1200
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password, money=1200)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Initial Items: 3 Poke Balls (ID 1)
    # Assuming Item ID 1 is Poke Ball. If not, we should query by name, but ID 1 is standard in our seed.
    initial_pokeballs = models.UserItem(user_id=db_user.id, item_id=1, quantity=3)
    db.add(initial_pokeballs)
    db.commit()
    
    return db_user

# Game
def add_user_pokemon(db: Session, user_id: int, pokemon_id: int, nickname: str = None):
    db_user_pokemon = models.UserPokemon(user_id=user_id, pokemon_id=pokemon_id, nickname=nickname)
    db.add(db_user_pokemon)
    db.commit()
    db.refresh(db_user_pokemon)
    return db_user_pokemon

def get_user_pokemons(db: Session, user_id: int):
    return db.query(models.UserPokemon).filter(models.UserPokemon.user_id == user_id).all()

def get_user_pokemon(db: Session, user_pokemon_id: int):
    return db.query(models.UserPokemon).filter(models.UserPokemon.id == user_pokemon_id).first()

def add_battle_history(db: Session, user_id: int, battle: schemas.BattleHistoryCreate):
    db_battle = models.BattleHistory(**battle.dict(), user_id=user_id)
    db.add(db_battle)
    
    # Update user money
    user = get_user(db, user_id)
    user.money += battle.money_earned
    
    db.commit()
    db.refresh(db_battle)
    return db_battle

def get_user_party(db: Session, user_id: int):
    return db.query(models.UserPokemon).filter(models.UserPokemon.user_id == user_id, models.UserPokemon.is_in_party == True).all()

def update_party_status(db: Session, user_pokemon: models.UserPokemon, is_in_party: bool):
    user_pokemon.is_in_party = is_in_party
    db.commit()
    db.refresh(user_pokemon)
    return user_pokemon

def add_xp(db: Session, user_pokemon_id: int, xp_amount: int):
    user_pokemon = get_user_pokemon(db, user_pokemon_id)
    if not user_pokemon:
        return None
    
    # Simple XP logic: level up every 100 XP * current_level (or simplified)
    # Using the logic from game_logic.py would be better but let's just update XP field
    # and let frontend or a separate logic handle leveling?
    # No, backend should handle leveling.
    
    # For now, just add to experience field.
    # We need to import calculate_xp_for_level or implement leveling logic here.
    # Let's assume linear leveling for simplicity or just store total XP.
    
    user_pokemon.experience += xp_amount
    
    # Check for level up
    # Threshold for level L is L^3 (Medium Fast) or similar.
    # Let's use a simple formula: Level = cubic root of XP?
    # Or just: Level up if XP >= Level * 100
    
    # Let's use a simple loop for now
    while True:
        xp_needed = user_pokemon.level * 100 # Simplified
        if user_pokemon.experience >= xp_needed:
            user_pokemon.experience -= xp_needed
            user_pokemon.level += 1
        else:
            break
            
    db.commit()
    db.refresh(user_pokemon)
    return user_pokemon

# World
def get_gyms(db: Session):
    return db.query(models.Gym).all()

def get_gym(db: Session, gym_id: int):
    return db.query(models.Gym).filter(models.Gym.id == gym_id).first()

def create_gym(db: Session, gym: schemas.GymCreate):
    db_gym = models.Gym(**gym.dict())
    db.add(db_gym)
    db.commit()
    db.refresh(db_gym)
    return db_gym

def get_elite_four(db: Session):
    return db.query(models.EliteFourMember).order_by(models.EliteFourMember.rank).all()

def create_elite_four_member(db: Session, member: schemas.EliteFourMemberCreate):
    db_member = models.EliteFourMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def add_user_badge(db: Session, user_id: int, gym_id: int):
    # Check if already earned
    existing = db.query(models.UserBadge).filter(models.UserBadge.user_id == user_id, models.UserBadge.gym_id == gym_id).first()
    if existing:
        return existing
        
    db_badge = models.UserBadge(user_id=user_id, gym_id=gym_id)
    db.add(db_badge)
    db.commit()
    db.refresh(db_badge)
    return db_badge

def get_user_badges(db: Session, user_id: int):
    return db.query(models.UserBadge).filter(models.UserBadge.user_id == user_id).all()

# Shop
def get_items(db: Session):
    return db.query(models.Item).all()

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_user_items(db: Session, user_id: int):
    return db.query(models.UserItem).filter(models.UserItem.user_id == user_id).all()

def add_user_item(db: Session, user_id: int, item_id: int, quantity: int):
    existing = db.query(models.UserItem).filter(models.UserItem.user_id == user_id, models.UserItem.item_id == item_id).first()
    if existing:
        existing.quantity += quantity
        db.commit()
        db.refresh(existing)
        return existing
    else:
        user_item = models.UserItem(user_id=user_id, item_id=item_id, quantity=quantity)
        db.add(user_item)
        db.commit()
        db.refresh(user_item)
        return user_item

def remove_user_item(db: Session, user_id: int, item_id: int, quantity: int = 1):
    existing = db.query(models.UserItem).filter(models.UserItem.user_id == user_id, models.UserItem.item_id == item_id).first()
    if existing and existing.quantity >= quantity:
        existing.quantity -= quantity
        db.commit()
        db.refresh(existing)
        return True
    return False

def deduct_money(db: Session, user_id: int, amount: int):
    user = get_user(db, user_id)
    if user.money >= amount:
        user.money -= amount
        db.commit()
        db.refresh(user)
        return True
    return False

# Favorites
def get_user_favorites(db: Session, user_id: int):
    return db.query(models.UserFavorite).filter(models.UserFavorite.user_id == user_id).all()

def add_user_favorite(db: Session, user_id: int, pokemon_id: int):
    existing = db.query(models.UserFavorite).filter(models.UserFavorite.user_id == user_id, models.UserFavorite.pokemon_id == pokemon_id).first()
    if existing:
        return existing
    
    db_favorite = models.UserFavorite(user_id=user_id, pokemon_id=pokemon_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def remove_user_favorite(db: Session, user_id: int, pokemon_id: int):
    db_favorite = db.query(models.UserFavorite).filter(models.UserFavorite.user_id == user_id, models.UserFavorite.pokemon_id == pokemon_id).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return True
    return False
