import sys
import os
from sqlalchemy import inspect

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine

def inspect_db():
    inspector = inspect(engine)

    # Get all tables
    tables = inspector.get_table_names()
    print("Tables in database:")

    for table in tables:
        print(f"\nTable: {table}")

        # List columns for each table
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")

if __name__ == "__main__":
    inspect_db()