import numpy as np
import math

# World dimensions — must match agent.py and main.py
W, H = 800, 600

# ── Tuning constants ─────────────────────────────────────────────────────
# Change these to alter ecosystem balance

FOOD_VALUE   = 25    # energy prey gains when eating one food item
HUNT_VALUE   = 50    # energy predator gains from catching prey
EAT_RADIUS   = 10   # pixel distance to count as eating (collision circle)
MAX_FOOD     = 80    # maximum food items on screen at once
SPAWN_BATCH  = 3     # how many food items spawn each time
SPAWN_EVERY  = 40    # ticks between each spawn batch


class World:
    """
    Manages the environment: food positions, spawning, and all eating collisions.

    The world is a simple 2D rectangle (800 × 600 pixels).
    Food is stored as a list of (x, y) tuples — lightweight and fast.

    Balance guide:
      - More food (lower SPAWN_EVERY) → prey thrive → predators overpopulate
      - Less food (higher SPAWN_EVERY) → prey struggle → predators starve
      - Larger EAT_RADIUS → easier eating → less evolutionary pressure
    """

    def __init__(self):
        self.foods = []     # list of (x, y) tuples
        self.tick  = 0
        self._spawn_food(50)   # seed the world with 50 food items at start

    # ── Food management ──────────────────────────────────────────────────

    def _spawn_food(self, n=SPAWN_BATCH):
        """
        Add n new food items at random positions within the world.
        Stops if MAX_FOOD is already reached so the world doesn't
        fill up completely and remove all challenge.
        """
        for _ in range(n):
            if len(self.foods) < MAX_FOOD:
                x = np.random.uniform(15, W - 15)
                y = np.random.uniform(15, H - 15)
                self.foods.append((x, y))

    def update(self):
        """
        Called once per simulation tick from main.py.
        Handles timed food spawning.
        """
        self.tick += 1

        # Spawn a new batch of food every SPAWN_EVERY ticks
        if self.tick % SPAWN_EVERY == 0:
            self._spawn_food(SPAWN_BATCH)

    # ── Collision / eating ───────────────────────────────────────────────

    def check_eating(self, prey_list, pred_list):
        """
        Check all eating interactions for this tick.

        Two types of eating:
          1. Prey eat food   — prey gains FOOD_VALUE energy, food removed
          2. Predators eat prey — predator gains HUNT_VALUE energy, prey dies

        We iterate in reversed(range(...)) when deleting from a list because
        removing item at index i shifts everything after it — iterating
        backwards avoids skipping or double-processing items.
        """

        # ── Prey eat food ────────────────────────────────────────────────
        for prey in prey_list:
            if not prey.alive:
                continue

            # Check each food item against this prey's position
            for i in reversed(range(len(self.foods))):
                fx, fy = self.foods[i]
                distance = math.hypot(prey.x - fx, prey.y - fy)

                if distance < EAT_RADIUS:
                    # Eat it: gain energy (capped at 120), remove food
                    prey.energy = min(prey.energy + FOOD_VALUE, 120)
                    self.foods.pop(i)
                    break   # one food per tick per creature

        # ── Predators eat prey ───────────────────────────────────────────
        for pred in pred_list:
            if not pred.alive:
                continue

            for prey in prey_list:
                if not prey.alive:
                    continue

                distance = math.hypot(pred.x - prey.x, pred.y - prey.y)

                if distance < EAT_RADIUS:
                    # Hunt success: predator gains energy, prey dies
                    pred.energy = min(pred.energy + HUNT_VALUE, 150)
                    prey.alive  = False
                    break   # one kill per tick per predator
