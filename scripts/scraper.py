import requests
import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app import models

def fetch_all_pokemon_data(limit=1010):
    base_url = f"https://pokeapi.co/api/v2/pokemon?limit={limit}"
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to fetch pokemon list")
        return []
    
    data = response.json()
    results = data['results']
    
    return results

def get_or_create_move(db: Session, move_name: str, move_url: str):
    existing = db.query(models.Move).filter(models.Move.name == move_name).first()
    if existing:
        return existing
    
    print(f"Fetching move: {move_name}")
    response = requests.get(move_url)
    if response.status_code == 200:
        data = response.json()
        move = models.Move(
            name=data['name'],
            type=data['type']['name'],
            power=data['power'],
            accuracy=data['accuracy'],
            pp=data['pp'],
            damage_class=data['damage_class']['name'] if data['damage_class'] else None
        )
        db.add(move)
        db.commit()
        db.refresh(move)
        return move
    return None

def process_pokemon(db: Session, name: str, url: str):
    # Check if exists
    existing = db.query(models.Pokemon).filter(models.Pokemon.name == name).first()
    if existing:
        print(f"Skipping {name}, already exists")
        return

    print(f"Fetching details for {name}...")
    response = requests.get(url)
    if response.status_code != 200:
        return

    detail_data = response.json()
    
    # Fetch Species Data for Growth Rate and Evolution
    species_url = detail_data['species']['url']
    species_response = requests.get(species_url)
    growth_rate = "medium-fast"
    evolves_from_name = None
    
    if species_response.status_code == 200:
        species_data = species_response.json()
        growth_rate = species_data['growth_rate']['name']
        if species_data['evolves_from_species']:
            evolves_from_name = species_data['evolves_from_species']['name']

    # Resolve evolves_from_id
    evolves_from_id = None
    if evolves_from_name:
        parent = db.query(models.Pokemon).filter(models.Pokemon.name == evolves_from_name).first()
        if parent:
            evolves_from_id = parent.id

    # Create Pokemon
    pokemon = models.Pokemon(
        id=detail_data['id'],
        name=detail_data['name'],
        height=detail_data['height'],
        weight=detail_data['weight'],
        types=[t['type']['name'] for t in detail_data['types']],
        stats={s['stat']['name']: s['base_stat'] for s in detail_data['stats']},
        sprites={
            "front_default": detail_data['sprites']['front_default'],
            "back_default": detail_data['sprites']['back_default'],
            "other": detail_data['sprites'].get('other', {})
        },
        abilities=[a['ability']['name'] for a in detail_data['abilities']],
        growth_rate=growth_rate,
        evolves_from_id=evolves_from_id
    )
    db.add(pokemon)
    db.commit()
    db.refresh(pokemon)

    # Process Moves (Limit to first 20 to save time/space for demo, or all for full)
    # For this task, let's do level-up moves only to be efficient
    for move_entry in detail_data['moves']:
        learn_method = move_entry['version_group_details'][-1]['move_learn_method']['name']
        level_learned_at = move_entry['version_group_details'][-1]['level_learned_at']
        
        if learn_method == "level-up":
            move_name = move_entry['move']['name']
            move_url = move_entry['move']['url']
            
            move = get_or_create_move(db, move_name, move_url)
            if move:
                pm = models.PokemonMove(
                    pokemon_id=pokemon.id,
                    move_id=move.id,
                    learn_method=learn_method,
                    level_learned_at=level_learned_at
                )
                db.add(pm)
    
    db.commit()
    print(f"Processed {name}")

def seed_database():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        
        # Fetch list
        # LIMITING TO 151 + Evolutions for speed in this demo context, 
        # but the code supports all. User asked for ALL, so we should try a larger batch
        # or at least set the structure to support it.
        # Let's do Gen 1 (151) fully with moves first to verify, then user can run for more.
        # Actually user said "not just 151 get them all".
        # I will set limit to 1010 but iterate carefully.
        
        pokemon_list = fetch_all_pokemon_data(limit=1010)
        
        for item in pokemon_list:
            process_pokemon(db, item['name'], item['url'])
            
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
