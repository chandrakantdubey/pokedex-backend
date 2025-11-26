import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app import models

def migrate():
    print("Creating new tables (items, user_items)...")
    Base.metadata.create_all(bind=engine)
    
    print("Altering user_pokemon table...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE user_pokemon ADD COLUMN is_in_party BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Column 'is_in_party' added.")
        except Exception as e:
            print(f"Error altering table (might already exist): {e}")

if __name__ == "__main__":
    migrate()
