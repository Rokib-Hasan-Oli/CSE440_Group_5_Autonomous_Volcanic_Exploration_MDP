# Reward Function

**Project:** Autonomous Volcanic Exploration using MDP
**Course:** CSE440 — Artificial Intelligence, North South University
**Group:** CSE440_Project_Group5

---

## Purpose

The reward function is the core of the agent's decision-making. It quantifies how *good* or *bad* each outcome is, encoding the two competing priorities of the mission:

- **Efficiency** — reach the objective in as few steps as possible.
- **Safety** — avoid hazards, with catastrophic outcomes penalized most heavily.

The MDP solver uses these rewards, together with the discount factor, to derive an optimal policy that steers the agent along safe and efficient routes.

---

## Reward Structure

The rewards that drive navigation across the volcanic terrain:

| Situation | Reward | Symbol | Rationale |
|-----------|:------:|:------:|-----------|
| **Achieving the objective** | **+100** | 🎯 | Mission accomplished — the primary goal |
| **Falling into a crater** | **−100** | 💥 | Catastrophic — the agent is destroyed |
| **Moving close to lava** | **−30** | 🔥 | Extreme danger zone |
| **Entering a gas zone** | **−10** | ☁️ | Hazardous atmosphere |
| **Each step (time cost)** | **−1** | ⏱️ | Discourages wandering; rewards efficiency |

### Extended Exploration Incentives

The configuration also defines exploration-oriented rewards that support the broader autonomous-exploration objective:

| Situation | Reward | Symbol | Rationale |
|-----------|:------:|:------:|-----------|
| **Collecting scientific samples** | **+20** | 🧪 | Gathering mission data |
| **Discovering a new area** | **+10** | 🗺️ | Exploring unmapped terrain |

---

## Design Rationale

The reward magnitudes are chosen to produce clear, safety-aware behavior:

- **Crater (−100) mirrors the goal (+100).** A fatal mistake is as significant as completing the mission, so the agent will take a longer route rather than risk destruction.
- **Graded hazards (−30 lava, −10 gas).** Danger is proportional. The agent avoids lava more strongly than gas, but will accept a minor hazard if it saves many steps.
- **Step cost (−1).** A small, constant penalty makes the agent prefer shorter paths, directly serving exploration efficiency.

This balance means the agent does not blindly rush to the goal — it weighs the cost of each step against the danger of the surrounding terrain.

---

## Configuration

The rewards are defined in [`config.py`](config.py):

```python
REWARDS = {
    "new_area": 10,        # 🗺️  Discovering a new area
    "sample_collect": 20,  # 🧪  Collecting scientific samples
    "goal": 100,           # 🎯  Achieving the objective
    "step": -1,            # ⏱️  Movement / time cost
    "gas": -10,            # ☁️  Gas zone
    "lava_close": -30,     # 🔥  Close to lava
    "crater": -100,        # 💥  Crater (agent destroyed)
    "safe": -1,            #     Safe terrain
}
```

The discount factor is also configured there:

```python
GAMMA = 0.9   # balances immediate safety vs. future reward
```

---

## How the Reward Drives the Policy

1. **Value Iteration** repeatedly applies the Bellman optimality update, propagating reward information outward from the objective across the grid.
2. **Discount factor (γ = 0.9)** ensures the agent values reaching the objective soon, while still planning several steps ahead to route around hazards.
3. **Optimal policy (π\*)** — for every cell, the action with the highest expected return is selected. High-value cells form a safe "gradient" leading to the goal.
4. **Agent execution** — the agent follows π\*, and the console reports the reward category of each cell it enters.
5. **Visualization** — the value-function heatmap makes the learned rewards visible: greener (higher-value) cells lie along the safest, most efficient path to the objective.

---

## Total Reward of a Mission

The reward accumulated over a completed run is:

```
Total Reward = Goal (+100)
             + Step Cost   (number of steps × −1)
             + Hazard Penalties (sum of any lava / gas / crater cells entered)
```

**Example:** an 18-step route that crosses one lava zone:

```
100 (goal) + (18 × −1) + (−30 lava) = 52
```

This total is reported in the visualization's **Overall Performance** panel at the end of each mission.

---

**Summary:** Navigate to the objective (🎯) as efficiently as possible while avoiding the hazards of the volcanic terrain (🔥 💥 ☁️).
