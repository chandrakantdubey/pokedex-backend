import asyncio
import httpx
import os
import sys

sys.path.append(os.getcwd())

from sqlalchemy import update
from app.database import SessionLocal
from app import models

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
MAX_CONCURRENCY = 20
CHUNK_SIZE = 50

async def fetch_url(client, url, semaphore):
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

async def seed_evolution_details(db, client, semaphore):
    print("--- Seeding Evolution Details ---")
    # Fetch all evolution chains
    data = await fetch_url(client, f"{POKEAPI_BASE_URL}/evolution-chain?limit=1000", semaphore)
    if not data: return
    
    urls = [r["url"] for r in data["results"]]
    for i in range(0, len(urls), CHUNK_SIZE):
        chunk = urls[i:i+CHUNK_SIZE]
        tasks = [fetch_url(client, u, semaphore) for u in chunk]
        results = await asyncio.gather(*tasks)
        
        for chain_data in results:
            if not chain_data: continue
            
            def process_chain(node):
                species_url = node["species"]["url"]
                species_id = int(species_url.split("/")[-2])
                
                for evolution in node["evolves_to"]:
                    next_species_url = evolution["species"]["url"]
                    next_species_id = int(next_species_url.split("/")[-2])
                    
                    # Find level trigger
                    level = None
                    for detail in evolution["evolution_details"]:
                        if detail["trigger"]["name"] == "level-up":
                            level = detail["min_level"]
                            break
                    
                    # Update DB
                    db.execute(update(models.PokemonSpecies).where(models.PokemonSpecies.id == species_id).values(
                        evolution_level=level,
                        evolution_species_id=next_species_id
                    ))
                    
                    process_chain(evolution)
            
            process_chain(chain_data["chain"])
        db.commit()
        print(f"Evolution Chains: {i+len(chunk)}")

async def main():
    db = SessionLocal()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient(timeout=60.0) as client:
        await seed_evolution_details(db, client, semaphore)

    print("--- Evolution Seeding Completed ---")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
