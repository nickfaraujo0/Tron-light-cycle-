# 🏍️ Tron Light Cycle — Neon Arena

A premium, highly-polished **Tron Light Cycle** arcade game built with Python and Pygame. Face off against an intelligent heuristic AI in a high-speed, high-stakes battle for survival within a cinematic cyberpunk arena!

## ✨ Features

- **Cinematic Cyberpunk Aesthetics**: High-end visual overhaul featuring aerodynamic light cycles, glowing 3-layer plasma trails, glassmorphism UI panels, and a pulsing neon main menu.
- **Intelligent Heuristic AI**: The enemy AI utilizes flood-fill algorithms to evaluate free space and counts safe neighbors to actively avoid dead ends and trap the player.
- **Dynamic Difficulty**: Choose between **Easy, Medium, and Hard**. Difficulty scales both the AI's intelligence evaluation and the base speed of the game.
- **Customizable Trail Modes**:
  - **Finite Mode**: Trails smoothly fade and disappear over time, opening up the arena.
  - **Infinite Mode**: Classic Tron rules—trails are permanent glowing walls that create an increasingly deadly maze.
- **Competitive Match System**: First to 3 points wins the match! Enjoy smooth round transitions and explosive particle effects upon crashing.

## 🚀 Installation & Running

1. Ensure you have Python 3.10+ installed.
2. Install the required dependency (`pygame-ce`):
```bash
pip install -r requirements.txt
```
3. Boot up the game:
```bash
python main.py
```

## 🎮 Controls

- **Arrow Keys**: Steer your Light Cycle (Up, Down, Left, Right).
- **Enter / Space**: Select menu items.
- **R / Space**: Play again after a match ends.
- **M**: Return to the main menu from the game over screen.
- **Esc**: Quit the game instantly.

## 🏗️ Architecture

The codebase has been designed with a clean, modular architecture:

- **`main.py`**: The entry point that boots the game.
- **`game.py`**: Contains the core `TronGame` loop, state machine (Menu, Running, Round Over), input handling, and premium UI rendering.
- **`ai.py`**: Houses the standalone pathfinding algorithms (`flood_fill_free_space`, `count_safe_neighbors`).
- **`bike.py`**: The `Bike` dataclass that manages position, direction, and trail history.
- **`particles.py`**: Independent rendering classes for crash sparks and expanding shockwaves.
- **`settings.py`**: The central configuration file for all grid dimensions, timings, and the cyberpunk color palette.
- **`utils.py`**: Mathematical and grid helper functions.

---
*Built as an AI Lab Mini-Project, transformed into a premium arcade experience.*
