from app.database import SessionLocal, engine
from app import models

def seed_berries():
    db = SessionLocal()
    try:
        # Check if berries already exist
        if db.query(models.Berry).count() > 0:
            print("Berries already seeded.")
            return

        # Ensure items exist first or create them
        berry_items = [
            {"name": "Cheri Berry", "cost": 100, "category_name": "berry", "effect": "Cures paralysis."},
            {"name": "Chesto Berry", "cost": 100, "category_name": "berry", "effect": "Cures sleep."},
            {"name": "Pecha Berry", "cost": 100, "category_name": "berry", "effect": "Cures poison."},
            {"name": "Rawst Berry", "cost": 100, "category_name": "berry", "effect": "Cures burn."},
            {"name": "Aspear Berry", "cost": 100, "category_name": "berry", "effect": "Cures frostbite."},
            {"name": "Oran Berry", "cost": 200, "category_name": "berry", "effect": "Restores 10 HP."},
            {"name": "Sitrus Berry", "cost": 500, "category_name": "berry", "effect": "Restores 1/4 max HP."},
            {"name": "Lum Berry", "cost": 800, "category_name": "berry", "effect": "Cures any status condition."},
        ]

        for item_data in berry_items:
            # Check if item exists
            item = db.query(models.Item).filter(models.Item.name == item_data["name"]).first()
            if not item:
                item = models.Item(**item_data)
                db.add(item)
                db.flush()
            
            # Add Berry
            db_berry = models.Berry(
                item_id=item.id,
                name=item_data["name"],
                growth_time=24,
                max_harvest=5,
                natural_gift_power=60,
                size=20,
                smoothness=25,
                soil_dryness=15,
                firmness_name="soft"
            )
            db.add(db_berry)
        
        db.commit()
        print(f"Successfully seeded {len(berry_items)} berries.")
    except Exception as e:
        print(f"Error seeding berries: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_berries()
