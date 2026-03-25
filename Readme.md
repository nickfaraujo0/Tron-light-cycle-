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



