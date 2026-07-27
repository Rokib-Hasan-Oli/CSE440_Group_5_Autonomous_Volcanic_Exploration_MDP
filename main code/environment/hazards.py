import random
from config import REWARDS

def generate_hazards(env):
    """Generate static hazards"""
    size = env.size

    # Lava zones (close to lava penalty)
    for _ in range(15):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        env.set_cell(x, y, REWARDS["lava_close"])  # -30

    # Gas zones (discourage but not fatal)
    for _ in range(10):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        env.set_cell(x, y, REWARDS["gas"])  # -10

    # Craters (fatal to robot)
    for _ in range(8):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        env.set_cell(x, y, REWARDS["crater"])  # -100

    # Goal - Achieving the objective
    env.set_cell(size-1, size-1, REWARDS["goal"])  # +100


def generate_dynamic_hazards(env):
    """Generate hazard locations that will change dynamically"""
    size = env.size
    
    # Generate initial hazard locations (without setting them yet)
    lava_locs = [(random.randint(0, size-1), random.randint(0, size-1)) for _ in range(15)]
    gas_locs = [(random.randint(0, size-1), random.randint(0, size-1)) for _ in range(10)]
    crater_locs = [(random.randint(0, size-1), random.randint(0, size-1)) for _ in range(8)]
    
    env.hazard_locations = {
        'lava': lava_locs,
        'gas': gas_locs,
        'crater': crater_locs
    }
    
    # Apply initial hazards
    apply_dynamic_hazards(env, step=0)
    
    # Goal - Achieving the objective
    env.set_cell(size-1, size-1, REWARDS["goal"])  # +100


def apply_dynamic_hazards(env, step):
    """Apply hazards that change every N steps"""
    size = env.size
    
    # Reset grid (keep goal)
    for i in range(size):
        for j in range(size):
            if env.grid[i, j] != REWARDS["goal"]:
                env.set_cell(i, j, REWARDS["step"])  # -1 (movement cost)
    
    # Re-apply goal
    env.set_cell(size-1, size-1, REWARDS["goal"])
    
    if hasattr(env, 'hazard_locations'):
        # Hazards shift every 3 steps
        shift = (step // 3) % 2
        
        # Apply lava zones
        for x, y in env.hazard_locations['lava']:
            nx = (x + shift) % size
            ny = (y + shift) % size
            env.set_cell(nx, ny, REWARDS["lava_close"])
        
        # Apply gas zones
        for x, y in env.hazard_locations['gas']:
            nx = (x + shift) % size
            ny = (y + shift) % size
            env.set_cell(nx, ny, REWARDS["gas"])
        
        # Apply craters
        for x, y in env.hazard_locations['crater']:
            nx = (x + shift) % size
            ny = (y + shift) % size
            env.set_cell(nx, ny, REWARDS["crater"])
