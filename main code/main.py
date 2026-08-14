import sys

# Windows consoles may use a legacy codepage that can't print emoji
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from environment.grid_world import GridWorld
from environment.hazards import generate_dynamic_hazards
from mdp.mdp_solver import MDPSolver
from agent.explorer import Explorer
from utils.visualization import plot_grid
from config import REWARDS

def generate_journey_summary(env, path):
    """Generate a comprehensive summary of the agent's journey"""
    if not path:
        return
    
    start_pos = path[0]
    end_pos = path[-1]
    total_steps = len(path) - 1

    hazards_encountered = {"lava": 0, "gas": 0, "crater": 0}
    safe_steps = 0
    goal_reached = False
    
    for i, (x, y) in enumerate(path):
        cell_value = env.get_cell(x, y)
        if cell_value == REWARDS["lava_close"]:
            hazards_encountered["lava"] += 1
        elif cell_value == REWARDS["gas"]:
            hazards_encountered["gas"] += 1
        elif cell_value == REWARDS["crater"]:
            hazards_encountered["crater"] += 1
        elif cell_value == REWARDS["goal"]:
            goal_reached = True
        else:
            safe_steps += 1
    
    print("\n" + "🗺️  AGENT'S JOURNEY SUMMARY 🗺️".center(60))
    print("=" * 60)
    
    print(f"\n📍 MISSION OVERVIEW:")
    print(f"  • Starting Position:      ({start_pos[0]}, {start_pos[1]})")
    print(f"  • Ending Position:        ({end_pos[0]}, {end_pos[1]})")
    print(f"  • Total Distance:         {total_steps} steps")
    print(f"  • Manhattan Distance:     {abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])} blocks")
    
    print(f"\n⚠️  HAZARDS ENCOUNTERED:")
    print(f"  • Lava Zones Crossed:     {hazards_encountered['lava']}")
    print(f"  • Gas Clouds Entered:     {hazards_encountered['gas']}")
    print(f"  • Craters Hit:            {hazards_encountered['crater']}")
    print(f"  • Safe Steps Taken:       {safe_steps}")
    
    print(f"\n🎯 MISSION STATUS:")
    if goal_reached:
        print(f"  ✅ SUCCESS - Reached the goal!")
        total_reward = REWARDS["goal"] - (total_steps * 1)
        print(f"  💰 Final Reward:          {total_reward}")
        print(f"  🎉 Objective Achieved!")
    else:
        print(f"  ❌ FAILED - Did not reach the goal")
        print(f"  ⚠️  Mission incomplete")
    
    print(f"\n🤖 AGENT'S STRATEGY:")
    print(f"  • Used MDP Value Iteration to compute optimal policy")
    print(f"  • Navigated through volcano avoiding craters")
    print(f"  • Adapted to dynamic hazard placement")
    print(f"  • Made {total_steps} optimal decisions")
    
    print(f"\n📊 PATH TAKEN:")
    if len(path) > 6:
        print(f"  Start → {' → '.join([f'({p[0]},{p[1]})' for p in path[1:4]])} → ... → ({end_pos[0]}, {end_pos[1]})")
    else:
        print(f"  {' → '.join([f'({p[0]},{p[1]})' for p in path])}")
    
    print("\n" + "=" * 60)

def main():
    print("\n" + "="*50)
    print("🌋 VOLCANO GRID WORLD MDP 🌋".center(50))
    print("="*50 + "\n")
    
    while True:
        env = GridWorld()
        generate_dynamic_hazards(env)

        solver = MDPSolver(env)
        V, policy = solver.value_iteration()

        agent = Explorer(env, policy)
        path = agent.run()

        # 'yes' restarts, 'no' exits
        choice = plot_grid(env, path, animate=True, value_func=V, policy=policy)
        
        if choice == 'yes':
            print("\n" + "="*50)
            continue
        else:
            print("✅ Thank you for running! Goodbye!")
            break

if __name__ == "__main__":
    main()
