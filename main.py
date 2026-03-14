"""
Ecosystem Evolution Simulator
==============================
Run with:  python main.py

Controls:
  SPACE     — force an evolution round right now
  +/-       — speed up / slow down simulation
  R         — reset everything from scratch
  ESC       — quit
"""

import pygame
import sys
from world     import World
from agent     import Agent
from evolution import evolve

# ── Simulation config ────────────────────────────────────────────────────
W, H          = 800, 600    # window / world size in pixels
FPS           = 60          # frames per second (ticks per second)
EVOLVE_EVERY  = 200         # ticks between each generation
N_PREY        = 30          # starting prey population
N_PRED        = 8           # starting predator population

# ── Colours (RGB) ───────────────────────────────────────────────────────
BG          = ( 13,  17,  23)   # dark background
C_FOOD      = ( 74, 222, 128)   # green dots for food
C_PREY      = ( 56, 189, 248)   # blue circles for prey
C_PREY_LOW  = (248, 196,  56)   # yellow when prey energy < 30
C_PRED      = (248, 113, 113)   # red circles for predators
C_PRED_HIGH = (240,  80,  40)   # brighter red when predator has high energy
C_TEXT      = (180, 190, 200)   # HUD text
C_BAR_BG    = ( 30,  36,  46)   # background of generation progress bar
C_BAR_FG    = ( 99, 179, 237)   # fill of generation progress bar


def draw_hud(screen, font, font_sm, generation, tick, prey_pop, pred_pop,
             world, evolve_every, speed_mult):
    """
    Render the heads-up display in the top-left corner.

    Shows: generation, tick, alive counts, food count,
           generation progress bar, and keyboard shortcuts.
    """

    n_prey = sum(1 for p in prey_pop if p.alive)
    n_pred = sum(1 for p in pred_pop if p.alive)

    lines = [
        f"Generation : {generation}",
        f"Tick       : {tick % evolve_every} / {evolve_every}",
        f"Prey alive : {n_prey}",
        f"Predators  : {n_pred}",
        f"Food       : {len(world.foods)}",
        f"Speed      : {speed_mult}x",
    ]

    for i, line in enumerate(lines):
        surf = font.render(line, True, C_TEXT)
        screen.blit(surf, (10, 10 + i * 18))

    # Generation progress bar
    bar_y    = 10 + len(lines) * 18 + 6
    bar_w    = 160
    bar_h    = 6
    progress = (tick % evolve_every) / evolve_every

    pygame.draw.rect(screen, C_BAR_BG, (10, bar_y, bar_w, bar_h), border_radius=3)
    pygame.draw.rect(screen, C_BAR_FG,
                     (10, bar_y, int(bar_w * progress), bar_h), border_radius=3)

    # Controls reminder at bottom-left
    tips = ["SPACE=evolve  R=reset  +/-=speed  ESC=quit"]
    for i, t in enumerate(tips):
        surf = font_sm.render(t, True, (80, 90, 100))
        screen.blit(surf, (10, H - 20 - i * 15))


def draw_agents(screen, prey_pop, pred_pop):
    """
    Draw all alive agents as coloured circles.

    Prey:
      - Normal:    blue circle, radius 5
      - Low energy (< 30): yellow — creature is struggling
    Predators:
      - Normal:    red circle, radius 7
      - High energy (> 100): bright orange-red — well-fed hunter
    """
    for p in prey_pop:
        if not p.alive:
            continue
        colour = C_PREY_LOW if p.energy < 30 else C_PREY
        pygame.draw.circle(screen, colour, (int(p.x), int(p.y)), 5)
        # Draw a tiny velocity line so you can see movement direction
        ex = int(p.x + p.vx * 4)
        ey = int(p.y + p.vy * 4)
        pygame.draw.line(screen, (30, 120, 180), (int(p.x), int(p.y)), (ex, ey), 1)

    for p in pred_pop:
        if not p.alive:
            continue
        colour = C_PRED_HIGH if p.energy > 100 else C_PRED
        pygame.draw.circle(screen, colour, (int(p.x), int(p.y)), 7)
        ex = int(p.x + p.vx * 4)
        ey = int(p.y + p.vy * 4)
        pygame.draw.line(screen, (180, 60, 60), (int(p.x), int(p.y)), (ex, ey), 1)


def reset(n_prey=N_PREY, n_pred=N_PRED):
    """Create a fresh world, prey population, and predator population."""
    world    = World()
    prey_pop = [Agent('prey')      for _ in range(n_prey)]
    pred_pop = [Agent('predator')  for _ in range(n_pred)]
    return world, prey_pop, pred_pop


def main():
    pygame.init()
    screen  = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Ecosystem Evolution Simulator')
    clock   = pygame.time.Clock()
    font    = pygame.font.SysFont('monospace', 13)
    font_sm = pygame.font.SysFont('monospace', 11)

    # Create initial simulation state
    world, prey_pop, pred_pop = reset()
    generation  = 0
    tick        = 0
    speed_mult  = 1    # how many simulation ticks per rendered frame

    # ── Main loop ────────────────────────────────────────────────────────
    while True:

        # ── 1. Handle input events ──────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r:
                    # Full reset — new random brains, fresh world
                    world, prey_pop, pred_pop = reset()
                    generation = 0
                    tick       = 0
                    print("[R] Simulation reset")

                if event.key == pygame.K_SPACE:
                    # Force evolution immediately — useful for fast-forwarding
                    prey_pop   = evolve(prey_pop, 'prey')
                    pred_pop   = evolve(pred_pop, 'predator')
                    generation += 1
                    print(f"[SPACE] Forced generation {generation}")

                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    # Speed up: run more ticks per frame
                    speed_mult = min(speed_mult + 1, 10)

                if event.key == pygame.K_MINUS:
                    # Slow down
                    speed_mult = max(speed_mult - 1, 1)

        # ── 2. Simulation update (run speed_mult ticks per frame) ───────
        # At speed_mult=1 the simulation runs in real time.
        # At speed_mult=5 it runs 5× faster — useful for early generations.
        for _ in range(speed_mult):

            # Update world (spawn food on schedule)
            world.update()

            # Update every prey agent
            # Prey see: food (approach), predators (avoid), no targets
            for p in prey_pop:
                p.update(
                    foods   = world.foods,
                    threats = pred_pop,    # avoid predators
                    targets = []           # prey don't hunt anything
                )

            # Update every predator agent
            # Predators see: prey as targets (approach), no threats
            for p in pred_pop:
                p.update(
                    foods   = world.foods,
                    threats = [],          # predators have nothing to fear
                    targets = prey_pop     # hunt prey
                )

            # Check all eating interactions this tick
            world.check_eating(prey_pop, pred_pop)

            tick += 1

            # ── 3. Evolution round ──────────────────────────────────────
            # Every EVOLVE_EVERY ticks, run the genetic algorithm.
            # The entire population is replaced by evolved offspring.
            if tick % EVOLVE_EVERY == 0:
                prey_pop   = evolve(prey_pop, 'prey')
                pred_pop   = evolve(pred_pop, 'predator')
                generation += 1
                print(f"[Gen {generation}] "
                      f"prey={sum(1 for p in prey_pop if p.alive)} "
                      f"pred={sum(1 for p in pred_pop if p.alive)}")

        # ── 4. Render ───────────────────────────────────────────────────
        # Only draw once per frame regardless of speed_mult
        screen.fill(BG)

        # Draw food as small green dots
        for fx, fy in world.foods:
            pygame.draw.circle(screen, C_FOOD, (int(fx), int(fy)), 3)

        # Draw all agents
        draw_agents(screen, prey_pop, pred_pop)

        # Draw the HUD overlay
        draw_hud(screen, font, font_sm,
                 generation, tick, prey_pop, pred_pop,
                 world, EVOLVE_EVERY, speed_mult)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()