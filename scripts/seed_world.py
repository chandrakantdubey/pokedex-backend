import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app import models

def seed_world_data():
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Gyms Data (Kanto)
        gyms = [
            {"name": "Pewter City Gym", "location": "Pewter City", "leader_name": "Brock", "type_specialty": "Rock", "badge_name": "Boulder Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/1.png"},
            {"name": "Cerulean City Gym", "location": "Cerulean City", "leader_name": "Misty", "type_specialty": "Water", "badge_name": "Cascade Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/2.png"},
            {"name": "Vermilion City Gym", "location": "Vermilion City", "leader_name": "Lt. Surge", "type_specialty": "Electric", "badge_name": "Thunder Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/3.png"},
            {"name": "Celadon City Gym", "location": "Celadon City", "leader_name": "Erika", "type_specialty": "Grass", "badge_name": "Rainbow Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/4.png"},
            {"name": "Fuchsia City Gym", "location": "Fuchsia City", "leader_name": "Koga", "type_specialty": "Poison", "badge_name": "Soul Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/5.png"},
            {"name": "Saffron City Gym", "location": "Saffron City", "leader_name": "Sabrina", "type_specialty": "Psychic", "badge_name": "Marsh Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/6.png"},
            {"name": "Cinnabar Island Gym", "location": "Cinnabar Island", "leader_name": "Blaine", "type_specialty": "Fire", "badge_name": "Volcano Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/7.png"},
            {"name": "Viridian City Gym", "location": "Viridian City", "leader_name": "Giovanni", "type_specialty": "Ground", "badge_name": "Earth Badge", "badge_image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/8.png"},
        ]
        
        for gym_data in gyms:
            existing = db.query(models.Gym).filter(models.Gym.name == gym_data['name']).first()
            if not existing:
                gym = models.Gym(**gym_data)
                db.add(gym)
                print(f"Added Gym: {gym_data['name']}")
            else:
                print(f"Skipping Gym: {gym_data['name']}, already exists")

        # Elite Four Data (Kanto)
        elite_four = [
            {"name": "Lorelei", "rank": 1, "specialty_type": "Ice", "image_url": "https://archives.bulbagarden.net/media/upload/1/1d/Lorelei_LGPE.png"},
            {"name": "Bruno", "rank": 2, "specialty_type": "Fighting", "image_url": "https://archives.bulbagarden.net/media/upload/9/9a/Bruno_LGPE.png"},
            {"name": "Agatha", "rank": 3, "specialty_type": "Ghost", "image_url": "https://archives.bulbagarden.net/media/upload/c/c9/Agatha_LGPE.png"},
            {"name": "Lance", "rank": 4, "specialty_type": "Dragon", "image_url": "https://archives.bulbagarden.net/media/upload/d/d3/Lance_LGPE.png"},
            {"name": "Blue (Champion)", "rank": 5, "specialty_type": "Multi", "image_url": "https://archives.bulbagarden.net/media/upload/f/f3/Blue_LGPE.png"},
        ]

        for member_data in elite_four:
            existing = db.query(models.EliteFourMember).filter(models.EliteFourMember.name == member_data['name']).first()
            if not existing:
                member = models.EliteFourMember(**member_data)
                db.add(member)
                print(f"Added Elite Four: {member_data['name']}")
            else:
                print(f"Skipping Elite Four: {member_data['name']}, already exists")

        db.commit()
        print("World seeding completed!")
    except Exception as e:
        print(f"Error seeding world: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_world_data()
