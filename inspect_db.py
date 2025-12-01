import sys
import os
from sqlalchemy import create_engine, inspect

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine

def inspect_db():
    inspector = inspect(engine)
    columns = inspector.get_columns('user_pokemon')
    print("Columns in user_pokemon:")
    for column in columns:
        print(f"- {column['name']} ({column['type']})")

if __name__ == "__main__":
    inspect_db()
