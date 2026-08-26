# Autonomous Volcanic Exploration using Markov Decision Process (MDP)

**Course:** CSE440 — Artificial Intelligence
**Institution:** North South University
**Group:** CSE440_Project_Group5

---

## Overview

This project designs an **autonomous exploration system** that uses a **Markov Decision Process (MDP)** to navigate a simulated volcanic terrain under uncertain and hazardous conditions — lava flows, craters, and toxic gas emissions.

The agent computes an optimal policy through **Value Iteration** and follows it from the start position to the objective. The goal is to **maximize exploration efficiency** (reach the objective in as few steps as possible) while **guaranteeing the safety** of the exploration agent (avoiding catastrophic hazards).

The system ships with a rich, animated visualization that shows the optimal policy, the computed value function, and a full performance summary of each mission.

---

## Objective

> Design an autonomous exploration system using a Markov Decision Process (MDP) for navigating through a simulated volcanic terrain while effectively managing uncertain environmental conditions, such as lava flows, craters, and gas emissions. The objective is to maximize the efficiency of exploration while ensuring the safety of the exploration agent.

---

## Team — CSE440_Project_Group5

| Student ID | Name | Email |
|------------|------|-------|
| 2211461642 | Md. Yousuf | md.yousuf01@northsouth.edu |
| 2211950642 |	MD. Rokib Hasan Oli | rokib.oli@northsouth.edu |
| 2131174642 | Safayat Ibrahim | safayat.ibrahim@northsouth.edu |
| 2131228042 | Tashfia Adiba Zaman Nizhum | tashfia.nizum@northsouth.edu |

---

## Key Features

- **MDP Value Iteration** — computes the optimal policy over a 10×10 volcanic grid using the Bellman optimality equation.
- **Uncertain, hazardous terrain** — lava zones, gas clouds, and craters are randomly placed on every run and can shift position over time.
- **Safety-aware navigation** — the reward structure strongly penalizes fatal hazards, steering the agent along safe, efficient routes.
- **Step-by-step reasoning** — the console prints the agent's position, terrain type, and chosen action at each step.
- **Professional visualization** — a three-panel dark-themed figure with an animated agent, policy arrows, a value-function heatmap, and a mission report.
- **Robust display** — opens an interactive window where supported, and automatically exports an animated GIF (or static image) when no GUI backend is available.

---

## Project Structure

```
CSE440_Project_Group5/
│
├── main code
│    ├── main.py             # Program entry point and simulation loop
│    ├── config.py           # Grid size, actions, discount factor, rewards
│    ├── requirements.txt       # Python dependencies
│    ├── REWARD_FUNCTION.md     # Reward system documentation
│    ├── requirements.txt       # Python dependencies
│    │
│    ├── agent/
│    │    └── explorer.py       # Agent that follows the optimal policy
│    │
│    ├── environment/
│    │     ├── grid_world.py         # 10×10 grid environment
│    │     └── hazards.py            # Random / dynamic hazard generation
│    │
│    ├──mdp/
│    │   └── mdp_solver.py           # Value Iteration solver
│    │
│    └── utils/
│          └── visualization.py       # Matplotlib visualization + animation
│
├── others
│    ├── Final Presentation PPTX
│    ├── Final Report PDF
│    └── One Minute Demo Video 
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Installation

**Prerequisites:** Python 3.8+

1. Navigate to the project folder.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `matplotlib`, `Pillow`.

---

## Usage

Run the simulation:

```bash
python main.py
```

**What happens:**

1. A 10×10 volcanic grid is created and hazards are randomly placed.
2. Value Iteration computes the optimal policy for the terrain.
3. The agent navigates from the start to the objective, printing each decision.
4. A visualization opens (or is exported) showing the policy, value heatmap, and mission summary.
5. Choose **Restart** to run a new simulation, or **Exit** to quit.

---

## MDP Formulation

The environment is modeled as a Markov Decision Process defined by the tuple **(S, A, P, R, γ)**:

| Component | Definition |
|-----------|------------|
| **States (S)** | Each cell `(x, y)` of the 10×10 grid — 100 states total. |
| **Actions (A)** | `UP`, `DOWN`, `LEFT`, `RIGHT`. |
| **Transition (P)** | Deterministic movement; an action that would leave the grid keeps the agent in place. |
| **Reward (R)** | The reward of the destination cell (goal, hazard, or movement cost). |
| **Discount (γ)** | `0.9` — balances immediate safety against long-term progress. |

**Bellman optimality update** (applied iteratively by the solver):

```
V(s) = max over a in A of [ R(s') + γ · V(s') ]      where s' = next_state(s, a)

π(s) = argmax over a in A of [ R(s') + γ · V(s') ]
```

Value Iteration runs for 100 sweeps over all states, converging to the optimal value function `V*` and the optimal policy `π*`. The agent then follows `π*` from the start position `(0, 0)` toward the objective at `(9, 9)`.

---

## Environment & Hazards

Hazards are generated randomly on each run and are designed to shift position over time, reflecting the uncertain nature of volcanic terrain:

| Terrain | Count per run | Meaning |
|---------|:-------------:|---------|
| Craters | 8 | Fatal — destroys the agent |
| Lava zones | 15 | Extreme danger |
| Gas clouds | 10 | Hazardous atmosphere |
| Objective | 1 | Located at the bottom-right corner `(9, 9)` |

All remaining cells are safe terrain with a small movement cost that encourages efficient exploration.

---

## Reward Function

The reward structure encodes the agent's safety priorities and exploration incentives. A summary:

| Element | Reward | Description |
|---------|:------:|-------------|
| Objective (Goal) | **+100** | Mission accomplished |
| Crater | **−100** | Catastrophic failure |
| Lava zone | **−30** | Extreme danger |
| Gas cloud | **−10** | Hazardous atmosphere |
| Each step | **−1** | Time / movement cost |

The full reward system, including exploration incentives and configuration details, is documented in **[REWARD_FUNCTION.md](REWARD_FUNCTION.md)**.

---

## Visualization

The visualization is a three-panel, dark-themed figure:

1. **Overall Performance** *(left)* — start and goal positions, total steps, a full reward breakdown, and the final mission status.
2. **Grid World — Optimal Policy** *(center)* — the color-coded terrain, hazard icons, policy arrows on every safe cell, and the animated agent tracing its path.
3. **Value Function Heatmap** *(right)* — the computed state values, where greener cells indicate higher value (closer to the objective).

**Animation behavior:** the view holds on the starting state for a few seconds, then plays the agent's route quickly before lingering on the completed path.

---

## Display Modes & Troubleshooting

| Issue | Explanation / Solution |
|-------|------------------------|
| Import errors | Install dependencies: `pip install -r requirements.txt` |
| No interactive window appears | On locked-down machines the Tk GUI backend can be blocked. The program automatically exports the run to `simulation.gif` (or `simulation.png`) and opens it — no action needed. |
| Want the live interactive window | Install a Qt backend: `python -m pip install PySide6`. The program will use it automatically if available. |
| Emoji not rendering | A font fallback is applied on Windows; harmless font warnings are suppressed. |

---

## Learning Outcomes

This project demonstrates:

- Formulating a real-world problem as a Markov Decision Process.
- Implementing the Value Iteration algorithm and the Bellman optimality equation.
- Designing a reward function that balances **efficiency** against **safety**.
- Handling uncertain, dynamic environments.
- Building clear, professional visualizations of an AI agent's reasoning.

---

## License

Educational project developed for the **CSE440 — Artificial Intelligence** course at **North South University**.
