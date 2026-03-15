import asyncio
import httpx
import os
import sys

sys.path.append(os.getcwd())
os.environ["DB_HOST"] = "localhost"

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal, engine, Base
from app import models

Base.metadata.create_all(bind=engine)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
MAX_CONCURRENCY = 20
CHUNK_SIZE = 50

# --- Helper Functions ---
def get_existing_ids(db, model):
    result = db.execute(select(model.id))
    return set(row[0] for row in result)

async def fetch_url(client, url, semaphore):
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

# --- Phase 1: Metadata & Static ---

async def seed_static_content(db):
    print("--- Seeding Static Content ---")
    gyms = [
        {"name": "Pewter Gym", "location": "Pewter City", "leader_name": "Brock", "type_specialty": "Rock", "badge_name": "Boulder Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/1.png"},
        {"name": "Cerulean Gym", "location": "Cerulean City", "leader_name": "Misty", "type_specialty": "Water", "badge_name": "Cascade Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/2.png"},
        {"name": "Vermilion Gym", "location": "Vermilion City", "leader_name": "Lt. Surge", "type_specialty": "Electric", "badge_name": "Thunder Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/3.png"},
        {"name": "Celadon Gym", "location": "Celadon City", "leader_name": "Erika", "type_specialty": "Grass", "badge_name": "Rainbow Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/4.png"},
        {"name": "Fuchsia Gym", "location": "Fuchsia City", "leader_name": "Koga", "type_specialty": "Poison", "badge_name": "Soul Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/5.png"},
        {"name": "Saffron Gym", "location": "Saffron City", "leader_name": "Sabrina", "type_specialty": "Psychic", "badge_name": "Marsh Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/6.png"},
        {"name": "Cinnabar Gym", "location": "Cinnabar Island", "leader_name": "Blaine", "type_specialty": "Fire", "badge_name": "Volcano Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/7.png"},
        {"name": "Viridian Gym", "location": "Viridian City", "leader_name": "Giovanni", "type_specialty": "Ground", "badge_name": "Earth Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/8.png"}
    ]
    current_gyms = set(row[0] for row in db.execute(select(models.Gym.name)))
    for g in gyms:
        if g["name"] not in current_gyms:
            db.add(models.Gym(**g))
            
    elite_four = [
        {"name": "Lorelei", "rank": 1, "specialty_type": "Ice", "image_url": "https://archives.bulbagarden.net/media/upload/1/1e/Lorelei_LGPE.png"},
        {"name": "Bruno", "rank": 2, "specialty_type": "Fighting", "image_url": "https://archives.bulbagarden.net/media/upload/a/aa/Bruno_LGPE.png"},
        {"name": "Agatha", "rank": 3, "specialty_type": "Ghost", "image_url": "https://archives.bulbagarden.net/media/upload/2/27/Agatha_LGPE.png"},
        {"name": "Lance", "rank": 4, "specialty_type": "Dragon", "image_url": "https://archives.bulbagarden.net/media/upload/8/8b/Lance_LGPE.png"}
    ]
    current_ef = set(row[0] for row in db.execute(select(models.EliteFourMember.name)))
    for m in elite_four:
        if m["name"] not in current_ef:
            db.add(models.EliteFourMember(**m))
    db.commit()

async def seed_metadata(db, client, semaphore):
    print("--- Seeding Metadata ---")
    existing_gens = get_existing_ids(db, models.Generation)
    gens = await fetch_url(client, f"{POKEAPI_BASE_URL}/generation", semaphore)
    if gens:
        for g in gens["results"]:
            gen_id = int(g["url"].split("/")[-2])
            if gen_id not in existing_gens:
                db.add(models.Generation(id=gen_id, name=g["name"]))
        db.commit()

    endpoints = {
        "type": models.Type,
        "stat": models.Stat,
        "egg-group": models.EggGroup,
        "growth-rate": models.GrowthRate,
        "nature": models.Nature,
        "region": models.Region
    }
    
    for endpoint, model in endpoints.items():
        print(f"Fetching {endpoint}...")
        existing_ids = get_existing_ids(db, model)
        data = await fetch_url(client, f"{POKEAPI_BASE_URL}/{endpoint}?limit=100", semaphore)
        if data:
            for item in data["results"]:
                item_id = int(item["url"].split("/")[-2])
                if item_id not in existing_ids:
                    db.add(model(id=item_id, name=item["name"]))
            db.commit()

# --- Phase 2: Independent Entities ---

async def seed_moves_abilities_items(db, client, semaphore):
    print("--- Seeding Moves, Abilities, Items ---")
    
    # 1. Moves
    existing_moves = get_existing_ids(db, models.Move)
    data = await fetch_url(client, f"{POKEAPI_BASE_URL}/move?limit=2000", semaphore)
    if data:
        urls = [r["url"] for r in data["results"]]
        for i in range(0, len(urls), CHUNK_SIZE):
            chunk = urls[i:i+CHUNK_SIZE]
            tasks = [fetch_url(client, u, semaphore) for u in chunk]
            results = await asyncio.gather(*tasks)
            for m in results:
                if m and m["id"] not in existing_moves:
                    type_id = int(m["type"]["url"].split("/")[-2]) if m["type"] else None
                    gen_id = int(m["generation"]["url"].split("/")[-2]) if m["generation"] else None
                    db.add(models.Move(
                        id=m["id"], name=m["name"], type_id=type_id, power=m["power"], 
                        pp=m["pp"], accuracy=m["accuracy"], priority=m["priority"],
                        damage_class=m["damage_class"]["name"] if m["damage_class"] else None,
                        generation_id=gen_id, effect_cvhance=m["effect_chance"]
                    ))
            db.commit()
            print(f"Moves: {i+len(chunk)}")

    # 2. Abilities
    existing_abilities = get_existing_ids(db, models.Ability)
    data = await fetch_url(client, f"{POKEAPI_BASE_URL}/ability?limit=2000", semaphore)
    if data:
        urls = [r["url"] for r in data["results"]]
        for i in range(0, len(urls), CHUNK_SIZE):
            chunk = urls[i:i+CHUNK_SIZE]
            tasks = [fetch_url(client, u, semaphore) for u in chunk]
            results = await asyncio.gather(*tasks)
            for a in results:
                if a and a["id"] not in existing_abilities:
                    effect = next((e["effect"] for e in a["effect_entries"] if e["language"]["name"] == "en"), None)
                    gen_id = int(a["generation"]["url"].split("/")[-2]) if a["generation"] else None
                    db.add(models.Ability(id=a["id"], name=a["name"], effect=effect, generation_id=gen_id))
            db.commit()
            print(f"Abilities: {i+len(chunk)}")

    # 3. Items & Berries
    print("Fetching item categories...")
    existing_items = get_existing_ids(db, models.Item)
    existing_berries = get_existing_ids(db, models.Berry)
    
    # We'll fetch items from specific categories that are relevant
    categories = ["standard-balls", "special-balls", "revive", "healing", "status-cures", "berries"]
    for cat_name in categories:
        print(f"Fetching category: {cat_name}")
        cat_data = await fetch_url(client, f"{POKEAPI_BASE_URL}/item-category/{cat_name}", semaphore)
        if cat_data:
            urls = [r["url"] for r in cat_data["items"]]
            for i in range(0, len(urls), CHUNK_SIZE):
                chunk = urls[i:i + CHUNK_SIZE]
                tasks = [fetch_url(client, u, semaphore) for u in chunk]
                results = await asyncio.gather(*tasks)
                for item in results:
                    if item and item["id"] not in existing_items:
                        effect = next((e["short_effect"] for e in item["effect_entries"] if e["language"]["name"] == "en"), None)
                        db.add(models.Item(
                            id=item["id"],
                            name=item["name"],
                            cost=item["cost"],
                            fling_power=item["fling_power"],
                            category_name=cat_name,
                            effect=effect,
                            sprite_url=item["sprites"]["default"]
                        ))
                        # If it's a berry, fetch berry data
                        if cat_name == "berries" and item["id"] not in existing_berries:
                            berry_url = item["baby_trigger_for"] # Wait, berries have their own endpoint
                            # Better approach: fetching by item name isn't always 1:1, but PokeAPI has /berry endpoint
                            # We'll handle berries in a separate pass below for accuracy
                db.commit()

    # 4. Berries specific pass
    print("Fetching berries and ensuring items exist...")
    berry_list = await fetch_url(client, f"{POKEAPI_BASE_URL}/berry?limit=100", semaphore)
    if berry_list:
        urls = [r["url"] for r in berry_list["results"]]
        for i in range(0, len(urls), CHUNK_SIZE):
            chunk = urls[i:i+CHUNK_SIZE]
            tasks = [fetch_url(client, u, semaphore) for u in chunk]
            results = await asyncio.gather(*tasks)
            for b_data in results:
                if not b_data: continue
                if b_data["id"] in existing_berries: continue
                
                item_url = b_data["item"]["url"]
                item_id = int(item_url.split("/")[-2])
                
                # Ensure Item exists
                if item_id not in existing_items:
                    item_data = await fetch_url(client, item_url, semaphore)
                    if item_data:
                        effect = next((e["short_effect"] for e in item_data["effect_entries"] if e["language"]["name"] == "en"), None)
                        db.add(models.Item(
                            id=item_data["id"],
                            name=item_data["name"],
                            cost=item_data["cost"],
                            fling_power=item_data["fling_power"],
                            category_name="berries",
                            effect=effect,
                            sprite_url=item_data["sprites"]["default"]
                        ))
                        existing_items.add(item_id)
                        db.flush() # Ensure item is in DB before berry
                
                db.add(models.Berry(
                    id=b_data["id"],
                    item_id=item_id,
                    name=b_data["name"].capitalize() + " Berry",
                    growth_time=b_data["growth_time"],
                    max_harvest=b_data["max_harvest"],
                    natural_gift_power=b_data["natural_gift_power"],
                    size=b_data["size"],
                    smoothness=b_data["smoothness"],
                    soil_dryness=b_data["soil_dryness"],
                    firmness_name=b_data["firmness"]["name"]
                ))
                existing_berries.add(b_data["id"])
            db.commit()

# --- Phase 3: Species & Pokemon (Split) ---

async def seed_species_basic(db, client, semaphore):
    print("--- Seeding Species (Basic) ---")
    existing_species = get_existing_ids(db, models.PokemonSpecies)
    
    data = await fetch_url(client, f"{POKEAPI_BASE_URL}/pokemon-species?limit=2000", semaphore)
    if data:
        results = data["results"]
        for i in range(0, len(results), CHUNK_SIZE):
            chunk = results[i:i+CHUNK_SIZE]
            tasks = [fetch_url(client, r["url"], semaphore) for r in chunk]
            s_results = await asyncio.gather(*tasks)
            
            for s_data in s_results:
                if not s_data: continue
                if s_data["id"] in existing_species: continue
                
                growth_rate_id = int(s_data["growth_rate"]["url"].split("/")[-2]) if s_data["growth_rate"] else None
                gen_id = int(s_data["generation"]["url"].split("/")[-2]) if s_data["generation"] else None
                
                # Insert basic species data WITHOUT evolves_from_species_id first
                # Or insert with it if parent exists? No, circularity possible? 
                # Actually, evolution tree is directed acyclic, so if we sort by ID usually parents come first.
                # But to be safe, let's just insert.
                
                # We can insert evolves_from_id safely IF the parent ID < current ID usually, 
                # but sometimes Gen 4 evolves from Gen 1. 
                # Best practice: Insert plain, then update links.
                
                db.add(models.PokemonSpecies(
                    id=s_data["id"],
                    name=s_data["name"],
                    order=s_data["order"],
                    gender_rate=s_data["gender_rate"],
                    capture_rate=s_data["capture_rate"],
                    base_happiness=s_data["base_happiness"],
                    is_baby=s_data["is_baby"],
                    hatch_counter=s_data["hatch_counter"],
                    has_gender_differences=s_data["has_gender_differences"],
                    growth_rate_id=growth_rate_id,
                    generation_id=gen_id
                    # evolves_from_species_id set in later pass
                ))
    db.commit()
    print(f"Species Basic: {i+len(chunk)}")

async def seed_natures_details(db, client, semaphore):
    print("--- Polishing Nature Details ---")
    natures = db.query(models.Nature).all()
    for n in natures:
        data = await fetch_url(client, f"{POKEAPI_BASE_URL}/nature/{n.id}", semaphore)
        if data:
            n.increased_stat_id = int(data["increased_stat"]["url"].split("/")[-2]) if data["increased_stat"] else None
            n.decreased_stat_id = int(data["decreased_stat"]["url"].split("/")[-2]) if data["decreased_stat"] else None
    db.commit()

async def update_species_links(db, client, semaphore):
    print("--- Updating Species Links (Evolution & Egg Groups) ---")
    species = db.query(models.PokemonSpecies).all()
    valid_egg_groups = get_existing_ids(db, models.EggGroup)
    
    urls = [f"{POKEAPI_BASE_URL}/pokemon-species/{s.id}" for s in species]
    for i in range(0, len(urls), CHUNK_SIZE):
        chunk_urls = urls[i:i + CHUNK_SIZE]
        tasks = [fetch_url(client, u, semaphore) for u in chunk_urls]
        results = await asyncio.gather(*tasks)
        for data in results:
            if not data: continue
            s = db.query(models.PokemonSpecies).get(data["id"])
            if not s: continue
            
            # Evolution
            if data["evolves_from_species"]:
                parent_id = int(data["evolves_from_species"]["url"].split("/")[-2])
                s.evolves_from_species_id = parent_id
            
            # Egg Groups
            for eg in data["egg_groups"]:
                eg_id = int(eg["url"].split("/")[-2])
                if eg_id in valid_egg_groups:
                    exists = db.execute(select(models.pokemon_egg_groups).where(
                        models.pokemon_egg_groups.c.species_id == s.id,
                        models.pokemon_egg_groups.c.egg_group_id == eg_id
                    )).first()
                    if not exists:
                        db.execute(models.pokemon_egg_groups.insert().values(species_id=s.id, egg_group_id=eg_id))
        db.commit()
        print(f"Species Links: {i+len(chunk_urls)}")

async def seed_pokemon_and_links(db, client, semaphore):
    print("--- Seeding Pokemon & Links ---")
    
    # Reload IDs for validation
    valid_species = get_existing_ids(db, models.PokemonSpecies)
    valid_pokemon = get_existing_ids(db, models.Pokemon)
    valid_moves = get_existing_ids(db, models.Move)
    valid_types = get_existing_ids(db, models.Type)
    valid_abilities = get_existing_ids(db, models.Ability)
    valid_egg = get_existing_ids(db, models.EggGroup)
    
    # 1. Metadata Links (Egg Groups & Evolution)
    # Rerun species fetch? Faster to iterate our local list if we had it.
    # We need API data again for links.
    
    data = await fetch_url(client, f"{POKEAPI_BASE_URL}/pokemon?limit=2000", semaphore)
    if not data: return
    
    all_pokemon_urls = data["results"]
    
    for i in range(0, len(all_pokemon_urls), CHUNK_SIZE):
        chunk = all_pokemon_urls[i:i+CHUNK_SIZE]
        tasks = [fetch_url(client, r["url"], semaphore) for r in chunk]
        p_results = await asyncio.gather(*tasks)
        valid_p = [p for p in p_results if p]
        
        # 1. Seed Pokemon Variety
        for p in valid_p:
            if p["id"] in valid_pokemon: continue
            
            species_id = int(p["species"]["url"].split("/")[-2])
            if species_id not in valid_species: continue
            
            pokemon = models.Pokemon(
                id=p["id"],
                name=p["name"],
                species_id=species_id,
                height=p["height"],
                weight=p["weight"],
                base_experience=p["base_experience"],
                order=p["order"],
                is_default=p["is_default"],
                sprites=p["sprites"],
                stats={s["stat"]["name"]: s["base_stat"] for s in p["stats"]}
            )
            db.add(pokemon) # Object added
            db.flush() # Force DB insert so ID exists for associations
            
            # Assoc Types
            for t in p["types"]:
                t_id = int(t["type"]["url"].split("/")[-2])
                if t_id in valid_types:
                    db.execute(models.pokemon_types.insert().values(pokemon_id=p["id"], type_id=t_id))
            
            # Assoc Abilities
            for a in p["abilities"]:
                a_id = int(a["ability"]["url"].split("/")[-2])
                if a_id in valid_abilities:
                    db.execute(models.pokemon_abilities.insert().values(pokemon_id=p["id"], ability_id=a_id, is_hidden=a["is_hidden"]))

            # Assoc Moves
            for m in p["moves"]:
                m_id = int(m["move"]["url"].split("/")[-2])
                if m_id in valid_moves:
                    method = m["version_group_details"][0]["move_learn_method"]["name"]
                    level = m["version_group_details"][0]["level_learned_at"]
                    db.add(models.PokemonMove(pokemon_id=p["id"], move_id=m_id, learn_method=method, level_learned_at=level))
        
        try:
            db.commit()
            print(f"Pokemon & Links: {i+len(chunk)}")
        except Exception as e:
            db.rollback()
            print(f"Error in chunk {i}: {e}")

    # 2. Update Species with Evolution & Egg Groups (Separate pass using species API)
    # Ideally tracked earlier, but for now let's just do a quick pass if needed.
    # Omitting for speed as Pokemon are seeded. Evolution links can be done by fetching species again or keeping a map.
    # User focused on "Pokemon and Attack" mostly.

async def main():
    db = SessionLocal()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient(timeout=60.0) as client:
        await seed_static_content(db)
        await seed_metadata(db, client, semaphore)
        await seed_natures_details(db, client, semaphore)
        await seed_moves_abilities_items(db, client, semaphore)
        await seed_species_basic(db, client, semaphore)
        await update_species_links(db, client, semaphore)
        await seed_pokemon_and_links(db, client, semaphore)

    print("--- Full Seeding Completed ---")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
