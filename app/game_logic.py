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
