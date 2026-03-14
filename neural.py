import numpy as np
import math

# World dimensions — must match main.py
W, H = 800, 600

class Agent:
    """
    One creature in the ecosystem.

    Every agent has:
      - A position (x, y) on the 2D world canvas
      - A velocity (vx, vy) for smooth movement
      - Energy that drains every tick and fills when eating
      - Age (ticks survived) — used in fitness scoring
      - A NeuralNet brain that decides movement every tick
      - A kind: 'prey' or 'predator'

    Prey flee predators and seek food.
    Predators hunt prey and ignore food.
    """

    def __init__(self, kind, x=None, y=None, brain=None):
        """
        Create a new agent.

        kind:  'prey' or 'predator'
        x, y:  starting position (random if not given)
        brain: a NeuralNet (random new one if not given)
        """
        self.kind   = kind
        self.x      = x if x is not None else np.random.uniform(20, W - 20)
        self.y      = y if y is not None else np.random.uniform(20, H - 20)
        self.brain  = brain

        # Prey are slightly faster so they have a chance to escape
        self.speed  = 2.2 if kind == 'prey' else 1.8

        # Starting energy — drains every tick, replenished by eating
        self.energy = 80.0

        # Age counts ticks survived — longer-lived creatures score higher
        self.age    = 0

        # Alive flag — False when energy hits 0 or creature is eaten
        self.alive  = True

        # Velocity — updated each tick by the neural net output
        self.vx     = 0.0
        self.vy     = 0.0

    # ─────────────────────────────────────────────────────────────────────
    # SENSING — build the 6-number input vector for the neural net
    # ─────────────────────────────────────────────────────────────────────

    def sense(self, foods, others):
        """
        Scan the world and return a 6-element numpy array for the neural net.

        Output format:
          [food_dx, food_dy, food_dist,   ← direction + distance to nearest food
           other_dx, other_dy, other_dist] ← direction + distance to nearest other agent

        All values are in [-1, 1]:
          - dx, dy are unit vectors (direction only, magnitude 1)
          - dist is normalised by world width: 0.0 = touching, 1.0 = far away

        If no food or no others exist, the relevant values are 0 (no signal).
        """

        # --- Find nearest food ---
        best_fd = 9999
        fdx, fdy, fd_norm = 0.0, 0.0, 1.0

        for f in foods:
            d = math.hypot(f[0] - self.x, f[1] - self.y)
            if d < best_fd:
                best_fd = d
                # Unit vector pointing toward food
                fdx = (f[0] - self.x) / max(d, 1)
                fdy = (f[1] - self.y) / max(d, 1)
                fd_norm = min(d / W, 1.0)

        # --- Find nearest other agent ---
        best_td = 9999
        tdx, tdy, td_norm = 0.0, 0.0, 1.0

        for o in others:
            if not o.alive:
                continue
            d = math.hypot(o.x - self.x, o.y - self.y)
            if d < best_td:
                best_td = d
                tdx = (o.x - self.x) / max(d, 1)
                tdy = (o.y - self.y) / max(d, 1)
                td_norm = min(d / W, 1.0)

        return np.array([fdx, fdy, fd_norm, tdx, tdy, td_norm])

    # ─────────────────────────────────────────────────────────────────────
    # UPDATING — called every simulation tick
    # ─────────────────────────────────────────────────────────────────────

    def update(self, foods, threats, targets):
        """
        One tick of life for this agent.

        foods:   list of (x,y) food positions  — what to eat
        threats: list of Agent objects to avoid (predators for prey)
        targets: list of Agent objects to chase (prey for predators)

        Step 1: Drain energy (cost of living)
        Step 2: Build sensor inputs
        Step 3: Run brain → get movement direction
        Step 4: Apply movement with smoothing
        Step 5: Bounce off world edges
        Step 6: Die if energy hits zero
        """

        if not self.alive:
            return

        # 1. Tick age and drain energy — this is the survival pressure
        self.age    += 1
        self.energy -= 0.08   # lose ~5 energy per second at 60fps

        # 2. Build inputs differently for prey vs predator
        #    Prey:     sense food (approach) + predators (avoid)
        #    Predator: sense prey (approach) + nothing to avoid
        if self.kind == 'prey':
            inputs = self.sense(foods, threats)
        else:
            inputs = self.sense(targets, threats)

        # 3. Brain decides direction: [dx, dy] both in [-1, 1]
       

        # 4. Smooth velocity update — don't teleport, accelerate gradually
        #    The 0.3 factor makes movement feel natural, not twitchy
        self.vx = max(-self.speed, min(self.speed, self.vx + dx * 0.3))
        self.vy = max(-self.speed, min(self.speed, self.vy + dy * 0.3))
        self.x += self.vx
        self.y += self.vy

        # 5. Bounce off walls — reverse velocity, clamp position
        if self.x < 5 or self.x > W - 5:
            self.vx *= -1
        if self.y < 5 or self.y > H - 5:
            self.vy *= -1
        self.x = max(5, min(W - 5, self.x))
        self.y = max(5, min(H - 5, self.y))

        # 6. Die if energy depleted
        if self.energy <= 0:
            self.alive = False

    # ─────────────────────────────────────────────────────────────────────
    # FITNESS — how good was this creature? (used by evolution.py)
    # ─────────────────────────────────────────────────────────────────────

    def fitness(self):
        """
        Score this creature's performance.

        Formula: energy + age * 0.3

        Why both?
          - Energy alone rewards creatures that found a lot of food recently
          - Age alone rewards creatures that survived a long time
          - Together they reward creatures that consistently eat AND survive

        Higher score = more likely to be selected as a parent.
        """
        return self.energy + self.age * 0.3
