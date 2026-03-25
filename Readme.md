# Tron Light Cycle (AI Lab Project) — Pygame

A simple **Tron Light Cycle** game on a **20×20 grid**:

- **Player agent**: arrow-key control (no reverse), leaves a trail
- **AI agent**: heuristic + constraint-based move selection
- **State space**: each grid cell \((x, y)\) is a state; moves are transitions
- **Constraints**: stay inside grid, never enter occupied (trail) cells
- **Game loop**: simultaneous movement, collision detection, scoring, restart

## Run

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the game:

```bash
python main.py
```

## Controls

- **Arrow keys**: move (no reverse)
- **Esc**: quit
- **Game Over**: press **R** or **Space** to restart

## AI (explainable)

At each step the AI:

1. Generates possible actions: UP/DOWN/LEFT/RIGHT (except reverse)
2. Filters actions using **constraints** (inside grid, not occupied)
3. Scores remaining actions with a simple **heuristic**:
   - Prefer moves with **more reachable free space** (flood-fill count)
   - Avoid **dead ends** (few/no safe neighbors after the move)
4. Picks the best-scoring move (random tie-break)

## Note (Windows / Python 3.14)

If you’re using **Python 3.14**, `pygame` may not have wheels yet. This project uses **`pygame-ce`** (community edition), which installs a compatible `pygame` module and works the same for this lab.

