# Ecosystem Evolution Simulator

> A 2D world where prey and predators evolve neural network brains through natural selection.  
> No backprop. No labeled data. Just survival pressure.

**Built with:** Python · pygame · numpy · Genetic Algorithm · Neural Networks

---

## What Is This Project?

A 2D simulated ecosystem where prey and predators move, eat, and die in real time. Every creature is controlled by a small neural network. Creatures that survive longer reproduce — passing mutated copies of their network weights to offspring.

Over generations, brains evolve: prey learn to find food and flee predators, predators learn to hunt. Flocking, ambush tactics, and arms races emerge spontaneously — nobody programs these behaviors, they appear from selection pressure alone.

---

## Project File Structure

```
ecosystem/
├── neural.py       ← brain of every creature (neural net, mutate, crossover)
├── agent.py        ← prey & predator classes (sense, move, eat, die)
├── evolution.py    ← genetic algorithm (selection, crossover, mutation)
├── world.py        ← food spawning, environment, collision detection
└── main.py         ← entry point — pygame window, simulation loop, HUD
```

Write and run files **in this order:**

| # | File | Depends on |
|---|------|------------|
| 1 | `neural.py` | nothing — write this first |
| 2 | `agent.py` | `neural.py` |
| 3 | `evolution.py` | `agent.py` |
| 4 | `world.py` | nothing — independent |
| 5 | `main.py` | everything above |

---

## Prerequisites

- Python **3.8 or higher**
- pip

Check your Python version:

```bash
python3 --version
```

---

## Step-by-Step Setup & Run Guide

### Step 1 — Install dependencies

```bash
pip install pygame numpy
```

If that doesn't work, try:

```bash
pip3 install pygame numpy

# Or if using Anaconda:
conda activate base
pip install pygame numpy
```

Verify the install worked:

```bash
python3 -c "import pygame, numpy; print('All good!')"
```

---

### Step 2 — Create the project folder

```bash
mkdir ecosystem
cd ecosystem
```

Save all 5 Python files into this folder. Your structure should look like:

```
ecosystem/
├── neural.py
├── agent.py
├── evolution.py
├── world.py
└── main.py
```

---

### Step 3 — Run the simulation

```bash
python main.py
```

On Mac/Linux if `python` points to Python 2:

```bash
python3 main.py
```

Using Anaconda:

```bash
conda activate base
python main.py
```

If you have multiple Python versions and get import errors, run with the full path:

```bash
/opt/anaconda3/bin/python main.py
```

✅ **Success:** A dark pygame window opens with green dots (food), blue circles (prey), and red circles (predators).

---

## What You See on Screen

| Visual | What it is | Detail |
|--------|-----------|--------|
| 🟢 Green dots | Food | Spawns every 40 ticks, max 80 on screen |
| 🔵 Blue circles | Prey — normal energy | Seek food, flee predators |
| 🟡 Yellow circles | Prey — low energy (< 30) | Struggling, will die soon if it doesn't eat |
| 🔴 Red circles | Predators — normal | Chase and eat prey |
| 🔶 Bright red circles | Predators — high energy (> 100) | Well-fed hunter |
| 📊 HUD top-left | Live stats | Generation, tick, population counts, speed |
| ▬ Progress bar | Generation timer | Fills up to next evolution round |

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `SPACE` | Force an evolution round right now — skip to next generation |
| `R` | Full reset — new random brains, fresh world, back to generation 0 |
| `+` or `=` | Speed up simulation (up to 10× faster) |
| `-` | Slow down simulation |
| `ESC` | Quit |

---

## Expected Evolution Timeline

| Generation | What you see |
|-----------|-------------|
| 0 – 3 | Pure chaos. Creatures move randomly. Most prey die immediately. |
| 5 – 10 | Prey start drifting toward food. Predators begin chasing. Direction emerging. |
| 15 – 30 | Clear food-seeking in prey. Active pursuit by predators. Arms race begins. |
| 50+ | Flocking in prey, coordinated hunting in predators. Population oscillates in Lotka-Volterra cycles. |

---

## How the ML Works

### Neural network — the creature brain

Architecture: **6 inputs → 4 hidden neurons → 2 outputs**, fully connected, `tanh` activation.

```
inputs  = [food_dx, food_dy, food_dist, threat_dx, threat_dy, threat_dist]
hidden  = tanh(inputs @ W1)    # (6,) @ (6,4) → (4,)
outputs = tanh(hidden @ W2)    # (4,) @ (4,2) → (2,)  →  [move_dx, move_dy]
```

The weights `W1` and `W2` are the **genes** — they are inherited, crossed over, and mutated during evolution. No backpropagation is used.

### Genetic algorithm — how evolution works

Every **200 ticks**, the GA runs:

1. Filter to alive agents only (dead = cannot reproduce)
2. Sort by fitness: `score = energy + age × 0.3`
3. Top **33%** become the parent pool
4. **Elitism:** copy the single best agent unchanged to the next generation
5. Breed the rest: pick 2 random parents → crossover weights 50/50 → mutate with Gaussian noise (rate `0.12`)
6. New generation starts with reset energy and random positions but evolved brains

---

## Tuning Parameters

Edit these constants to balance your ecosystem:

| File | Constant | Default | Effect |
|------|----------|---------|--------|
| `main.py` | `N_PREY` | `30` | Starting prey count |
| `main.py` | `N_PRED` | `8` | Starting predator count |
| `main.py` | `EVOLVE_EVERY` | `200` | Ticks between generations |
| `world.py` | `FOOD_VALUE` | `25` | Energy prey gains per food |
| `world.py` | `HUNT_VALUE` | `50` | Energy predator gains per kill |
| `world.py` | `SPAWN_EVERY` | `40` | Ticks between food spawns |
| `world.py` | `MAX_FOOD` | `80` | Max food items on screen |
| `agent.py` | `self.energy -= 0.08` | `0.08` | Energy drain per tick |
| `evolution.py` | `rate=0.12` | `0.12` | Mutation strength |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`

Your terminal is using a different Python than where pygame is installed.

```bash
# Use Anaconda's Python directly:
conda activate base
python main.py

# Or with full path:
/opt/anaconda3/bin/python main.py
```

---

### `TypeError: 'Agent' object is not subscriptable`

Replace your `agent.py` with the latest version. The `sense()` method needs to handle both food tuples `(x, y)` and Agent objects.

---

### All prey die immediately

Reduce the energy drain in `agent.py`:

```python
# Change this line (around line 126):
self.energy -= 0.08
# To:
self.energy -= 0.04
```

---

### Predators go extinct

In `world.py`, increase `HUNT_VALUE`:

```python
HUNT_VALUE = 70   # was 50
```

Or reduce `N_PRED` in `main.py` to `4`.

---

### Nothing evolves after 50+ generations

Lower mutation rate in `evolution.py`:

```python
child_brain = child_brain.mutate(rate=0.08)   # was 0.12
```

---

### Pylance red import errors in VS Code

These are **editor warnings only** — the code runs fine. To fix them:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type **Python: Select Interpreter**
3. Choose the interpreter that matches where you installed pygame (e.g. `base (3.12.2) /opt/anaconda3/bin/python`)

---

## Next Steps

- Add **speed gene** and **vision range gene** as heritable traits alongside neural weights
- Add **terrain** — walls, rivers, food-rich patches using a 2D numpy grid
- Add **seasonal food cycles** — feast and famine alternating every 500 ticks
- Upgrade to **NEAT** (`pip install neat-python`) — let network topology evolve too
- Add **live population graphs** using `pygame.draw.line` across tick history
- Export evolution data to **CSV** and visualize trait drift with `matplotlib`

---

## Learning Resources

| Resource | Best for |
|----------|---------|
| [nry.me — Evolving Simple Organisms](https://nry.me) | Start here — almost identical project from scratch |
| [DataCamp — Genetic Algorithm in Python](https://www.datacamp.com/tutorial/genetic-algorithm-python) | Deep dive into GA mechanics |
| [neat-python docs](https://neat-python.readthedocs.io) | When you're ready for Phase 3 topology evolution |
| [neuroevolutionbook.com](https://neuroevolutionbook.com) | Advanced — co-evolution, NEAT, adversarial setups |

---

*Ecosystem Evolution Simulator — neuroevolution with no backprop, no labeled data, just survival.*
