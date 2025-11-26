import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app import models

def seed_items():
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        items = [
            {"name": "Poke Ball", "description": "A device for catching wild Pokemon.", "price": 200, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png", "category": "pokeball"},
            {"name": "Great Ball", "description": "A good, high-performance Ball.", "price": 600, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/great-ball.png", "category": "pokeball"},
            {"name": "Ultra Ball", "description": "An ultra-high-performance Ball.", "price": 1200, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png", "category": "pokeball"},
            {"name": "Potion", "description": "Restores 20 HP.", "price": 300, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/potion.png", "category": "medicine"},
            {"name": "Super Potion", "description": "Restores 50 HP.", "price": 700, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/super-potion.png", "category": "medicine"},
            {"name": "Hyper Potion", "description": "Restores 200 HP.", "price": 1200, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/hyper-potion.png", "category": "medicine"},
            {"name": "Revive", "description": "Revives a fainted Pokemon with half HP.", "price": 1500, "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/revive.png", "category": "medicine"},
        ]
        
        for item_data in items:
            existing = db.query(models.Item).filter(models.Item.name == item_data['name']).first()
            if not existing:
                item = models.Item(**item_data)
                db.add(item)
                print(f"Added Item: {item_data['name']}")
            else:
                print(f"Skipping Item: {item_data['name']}, already exists")

        db.commit()
        print("Item seeding completed!")
    except Exception as e:
        print(f"Error seeding items: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_items()
