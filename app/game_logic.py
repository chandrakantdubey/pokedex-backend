import math

def calculate_xp_for_level(growth_rate: str, level: int) -> int:
    """
    Calculate the total XP required to reach a specific level based on growth rate.
    Formulas based on Gen 3 mechanics.
    """
    if level <= 1:
        return 0
    
    n = level
    
    if growth_rate == "erratic":
        if n <= 50:
            return int((n**3 * (100 - n)) / 50)
        elif n <= 68:
            return int((n**3 * (150 - n)) / 100)
        elif n <= 98:
            return int((n**3 * math.floor((1911 - 10 * n) / 3)) / 500)
        else:
            return int((n**3 * (160 - n)) / 100)
            
    elif growth_rate == "fast":
        return int(4 * n**3 / 5)
        
    elif growth_rate == "medium-fast": # Normal Medium
        return int(n**3)
        
    elif growth_rate == "medium-slow":
        return int(6/5 * n**3 - 15 * n**2 + 100 * n - 140)
        
    elif growth_rate == "slow":
        return int(5 * n**3 / 4)
        
    elif growth_rate == "fluctuating":
        if n <= 15:
            return int(n**3 * (math.floor((n + 1) / 3) + 24) / 50)
        elif n <= 36:
            return int(n**3 * (n + 14) / 50)
        else:
            return int(n**3 * (math.floor(n / 2) + 32) / 50)
            
    else:
        # Default to medium-fast if unknown
        return int(n**3)

def calculate_level_from_xp(growth_rate: str, xp: int) -> int:
    """
    Calculate the level from total XP.
    This is a naive implementation iterating up to 100.
    """
    for level in range(1, 101):
        required_xp = calculate_xp_for_level(growth_rate, level)
        if xp < required_xp:
            return level - 1
    return 100

def calculate_stats(base_stats: dict, level: int):
    """
    Calculate Pokemon stats based on base stats and level.
    Simplified Gen 3 formula.
    """
    # { "hp": 45, "attack": 49, ... }
    stats = {}
    
    # HP
    base_hp = base_stats.get("hp", 10)
    stats["max_hp"] = math.floor(0.01 * (2 * base_hp + 31) * level) + level + 10
    stats["current_hp"] = stats["max_hp"]
    
    # Others
    for stat_name in ["attack", "defense", "special-attack", "special-defense", "speed"]:
        base = base_stats.get(stat_name, 10)
        # Convert hyphenated names to underscored for model compatibility
        key = stat_name.replace("-", "_")
        stats[key] = math.floor(0.01 * (2 * base + 31) * level) + 5
        
    return stats

def is_breeding_compatible(parent1_species: any, parent2_species: any):
    """
    Check if two Pokemon are compatible for breeding.
    - Ditto can breed with any non-Legendary/Undiscovered species.
    - Two Pokemon in the same egg group can breed if they are opposite genders.
    """
    # Egg Group ID 15 is 'Undiscovered' (Legendaries usually)
    undiscovered_id = 15
    ditto_species_id = 132
    
    # Check for undiscovered group
    p1_groups = [g.id for g in parent1_species.egg_groups]
    p2_groups = [g.id for g in parent2_species.egg_groups]
    
    if undiscovered_id in p1_groups or undiscovered_id in p2_groups:
        return False
        
    # Ditto logic
    if parent1_species.id == ditto_species_id or parent2_species.id == ditto_species_id:
        return True
        
    # Gender check
    # Simplified: parents must have a gender and be different
    # (Note: This function doesn't have gender data yet, so calling code must handle it)
    
    # Common egg group check
    common_groups = set(p1_groups).intersection(set(p2_groups))
    return len(common_groups) > 0

def generate_individual_values():
    """Generate random IVs from 0 to 31 for each stat."""
    import random
    return {
        "hp": random.randint(0, 31),
        "attack": random.randint(0, 31),
        "defense": random.randint(0, 31),
        "special_attack": random.randint(0, 31),
        "special_defense": random.randint(0, 31),
        "speed": random.randint(0, 31)
    }

def get_gender_from_rate(rate: int):
    """
    -1: Genderless
    0: Always male
    1-7: Mixed
    8: Always female
    """
    import random
    if rate == -1: return "Genderless"
    if rate == 0: return "Male"
    if rate == 8: return "Female"
    
    # rate is 1-7, representing chance of female in eighths
    if random.randint(1, 8) <= rate:
        return "Female"
    return "Male"
