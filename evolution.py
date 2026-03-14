import random
from agent import Agent

def evolve(agents, kind):
    """
    Run one round of the genetic algorithm on a population.

    This is called every EVOLVE_EVERY ticks from main.py.
    It replaces the entire current population with a new generation
    bred from the best survivors.

    Steps:
      1. Filter to alive agents only
      2. Handle extinction (everyone died)
      3. Sort by fitness — best first
      4. Pick top 33% as the parent pool
      5. Copy the single best agent unchanged (elitism)
      6. Breed the rest via crossover + mutation
      7. Return the new generation

    kind: 'prey' or 'predator' — sets population size limits
    """

    # ── Step 1: Only use agents that are still alive ──────────────────────
    # Dead agents cannot reproduce — this IS natural selection
    alive = [a for a in agents if a.alive]

    # ── Step 2: Handle extinction ─────────────────────────────────────────
    # If every agent died (bad generation), restart with fresh random brains
    # This prevents the simulation from stalling permanently
    if len(alive) == 0:
        count = 20 if kind == 'prey' else 6
        print(f"[!] {kind} extinct — restarting with {count} random agents")
        return [Agent(kind) for _ in range(count)]

    # ── Step 3: Sort by fitness (highest first) ───────────────────────────
    # fitness() = energy + age * 0.3
    # Best survivors rise to the top
    alive.sort(key=lambda a: a.fitness(), reverse=True)

    # ── Step 4: Select the top 33% as parents ────────────────────────────
    # We always keep at least 2 parents so crossover is possible
    n_parents = max(2, len(alive) // 3)
    parents   = alive[:n_parents]

    # ── Step 5: Decide population size for next generation ───────────────
    # Never shrink below a minimum — keeps the ecosystem alive
    # Never grow beyond a maximum — prevents overcrowding
    if kind == 'prey':
        target = max(12, min(len(alive), 50))
    else:
        target = max(4,  min(len(alive), 18))

    new_generation = []

    # ── Step 6: Elitism — copy the single best agent unchanged ───────────
    # This guarantees we never LOSE the best brain found so far.
    # We call mutate(0.0) which adds zero noise — just copies the weights.
    champion        = Agent(kind, brain=parents[0].brain.mutate(0.0))
    champion.energy = 80  # reset energy for fair start
    new_generation.append(champion)

    # ── Step 7: Breed the rest with crossover + mutation ─────────────────
    while len(new_generation) < target:
        # Pick two random parents from the elite pool
        # The same parent can be picked twice (self-crossover = pure mutation)
        parent_a = random.choice(parents)
        parent_b = random.choice(parents)

        # Crossover: mix weights from both parents 50/50
        child_brain = parent_a.brain.crossover(parent_b.brain)

        # Mutation: add small random noise — introduces new variation
        # Without mutation, the population converges and stops improving
        child_brain = child_brain.mutate(rate=0.12)

        child = Agent(kind, brain=child_brain)
        new_generation.append(child)

    return new_generation
