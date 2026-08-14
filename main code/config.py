GRID_SIZE = 10

ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

GAMMA = 0.9   # discount factor

REWARDS = {
    "new_area": 10,
    "sample_collect": 20,
    "goal": 100,
    "step": -1,
    "gas": -10,
    "lava_close": -30,
    "crater": -100,
    "safe": -1
}

REWARD_DESCRIPTIONS = {
    "goal": ("🎯 Objective", 100, "Goal"),
    "crater": ("💥 Crater", -100, "Robot Destroyed"),
    "lava_close": ("🔥 Lava", -30, "Close to Lava"),
    "gas": ("☁️ Gas", -10, "Gas Zone"),
    "step": ("➡️ Step", -1, "Movement Cost"),
}
