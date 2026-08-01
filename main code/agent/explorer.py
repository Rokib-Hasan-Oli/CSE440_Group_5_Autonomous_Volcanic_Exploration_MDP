from config import REWARDS

class Explorer:
    def __init__(self, env, policy):
        self.env = env
        self.policy = policy
        self.path = []

    def _get_reward_description(self, reward_value):
        """Return readable reward description"""
        if reward_value == REWARDS["goal"]:
            return "🎯 GOAL (+100)"
        elif reward_value == REWARDS["crater"]:
            return "💥 CRATER (-100)"
        elif reward_value == REWARDS["lava_close"]:
            return "🔥 LAVA (-30)"
        elif reward_value == REWARDS["gas"]:
            return "☁️ GAS (-10)"
        else:
            return f"Safe (Movement Cost: {reward_value})"

    def run(self, start=(0,0)):
        x, y = start
        self.path.append((x,y))

        print(f"\n🤖 Agent Starting at: ({x}, {y})")
        print("=" * 60)

        print("📋 ROBOT'S REWARD SYSTEM:")
        print(f"  • Objective (Goal):           +{REWARDS['goal']:3d}")
        print(f"  • Crater (Robot Destroyed):   {REWARDS['crater']:4d}")
        print(f"  • Lava Zone (Close):          {REWARDS['lava_close']:4d}")
        print(f"  • Gas Zone:                   {REWARDS['gas']:4d}")
        print(f"  • Each Step (Time Cost):      {REWARDS['step']:4d}")
        print("=" * 60)

        for step in range(100):  # max 100 steps
            action = self.policy[x][y]
            cell_value = self.env.get_cell(x, y)
            reward_desc = self._get_reward_description(cell_value)

            actions = {0: "UP ↑", 1: "DOWN ↓", 2: "LEFT ←", 3: "RIGHT →"}

            print(f"\nStep {step + 1}:")
            print(f"  Position: ({x}, {y})")
            print(f"  Current Area: {reward_desc}")
            print(f"  🤔 Best Action: {actions[action]}")

            moves = {
                0: (-1, 0),  # up
                1: (1, 0),   # down
                2: (0, -1),  # left
                3: (0, 1)    # right
            }

            dx, dy = moves[action]
            nx, ny = x + dx, y + dy

            if not self.env.is_valid(nx, ny):
                print(f"  ⚠️ Out of bounds! Stopping.")
                break

            x, y = nx, ny
            self.path.append((x,y))

            next_value = self.env.get_cell(x, y)
            next_desc = self._get_reward_description(next_value)
            print(f"  ✓ Moved to: ({x}, {y}) | {next_desc}")

            if next_value == REWARDS["goal"]:
                print(f"  🎉 OBJECTIVE ACHIEVED!")
                break

        print("=" * 60)
        print(f"✅ Mission Complete! Path length: {len(self.path)} steps\n")

        return self.path
