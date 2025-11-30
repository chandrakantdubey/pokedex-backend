import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import crud, schemas, models

def test_favorites():
    db = SessionLocal()
    try:
        # Get first user
        user = db.query(models.User).first()
        if not user:
            print("No user found. Please run create_users.sh first.")
            return

        print(f"Testing favorites for user: {user.username}")

        # Add favorite (Pikachu - ID 25)
        print("Adding Pikachu (ID 25) to favorites...")
        fav = crud.add_user_favorite(db, user.id, 25)
        print(f"Added favorite: Pokemon ID {fav.pokemon_id}")

        # Get favorites
        favorites = crud.get_user_favorites(db, user.id)
        print(f"User has {len(favorites)} favorites.")
        for f in favorites:
            print(f"- Pokemon ID: {f.pokemon_id}")

        # Remove favorite
        print("Removing Pikachu from favorites...")
        crud.remove_user_favorite(db, user.id, 25)
        
        # Verify removal
        favorites = crud.get_user_favorites(db, user.id)
        print(f"User has {len(favorites)} favorites after removal.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_favorites()
