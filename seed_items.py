from app.database import SessionLocal, engine
from app import models

def seed_items():
    db = SessionLocal()
    try:
        # Check if items already exist
        if db.query(models.Item).count() > 0:
            print("Items already seeded.")
            return

        items = [
            # Poke Balls
            {"name": "poke-ball", "cost": 200, "category_name": "pokeball", "effect": "A device for catching wild Pokémon. It's thrown like a ball at a Pokémon, comfortably encapsulating its target."},
            {"name": "great-ball", "cost": 600, "category_name": "pokeball", "effect": "A good, high-performance Poké Ball that provides a higher Pokémon catch rate than a standard Poké Ball."},
            {"name": "ultra-ball", "cost": 1200, "category_name": "pokeball", "effect": "An ultra-high-performance Poké Ball that provides a higher Pokémon catch rate than a Great Ball."},
            
            # Medicine
            {"name": "potion", "cost": 300, "category_name": "medicine", "effect": "A spray-type medicine for treating wounds. It can be used to restore 20 HP to a single Pokémon."},
            {"name": "super-potion", "cost": 700, "category_name": "medicine", "effect": "A spray-type medicine for treating wounds. It can be used to restore 60 HP to a single Pokémon."},
            {"name": "hyper-potion", "cost": 1200, "category_name": "medicine", "effect": "A spray-type medicine for treating wounds. It can be used to restore 120 HP to a single Pokémon."},
            {"name": "revive", "cost": 1500, "category_name": "medicine", "effect": "A medicine that can be used to revive a single Pokémon that has fainted. It also restores half the Pokémon's max HP."},
        ]

        for item_data in items:
            db_item = models.Item(**item_data)
            db.add(db_item)
        
        db.commit()
        print(f"Successfully seeded {len(items)} items.")
    except Exception as e:
        print(f"Error seeding items: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_items()
