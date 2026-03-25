import random
import sys
from collections import deque
from dataclasses import dataclass

import pygame


GRID_W = 20
GRID_H = 20
CELL_SIZE = 28
PANEL_H = 70
WIN_W = GRID_W * CELL_SIZE
WIN_H = GRID_H * CELL_SIZE + PANEL_H

FPS = 10

BG = (10, 10, 14)
GRID_LINE = (25, 25, 34)
TEXT = (230, 230, 245)
MUTED = (160, 160, 180)

PLAYER_COLOR = (0, 200, 255)
AI_COLOR = (255, 160, 0)
PLAYER_HEAD = (150, 245, 255)
AI_HEAD = (255, 215, 120)


DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
DIR_LIST = [DIRS["UP"], DIRS["DOWN"], DIRS["LEFT"], DIRS["RIGHT"]]


def add(p, d):
    return (p[0] + d[0], p[1] + d[1])


def neg(d):
    return (-d[0], -d[1])


def in_bounds(p):
    return 0 <= p[0] < GRID_W and 0 <= p[1] < GRID_H


def cell_rect(cell):
    x, y = cell
    return pygame.Rect(x * CELL_SIZE, PANEL_H + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def flood_fill_free_space(start, occupied):
    if start in occupied or not in_bounds(start):
        return 0
    q = deque([start])
    seen = {start}
    while q:
        cur = q.popleft()
        for d in DIR_LIST:
            nxt = add(cur, d)
            if nxt in seen or nxt in occupied or not in_bounds(nxt):
                continue
            seen.add(nxt)
            q.append(nxt)
    return len(seen)


def count_safe_neighbors(cell, occupied):
    n = 0
    for d in DIR_LIST:
        nxt = add(cell, d)
        if in_bounds(nxt) and nxt not in occupied:
            n += 1
    return n


@dataclass
class Bike:
    name: str
    pos: tuple[int, int]
    direction: tuple[int, int]
    color: tuple[int, int, int]
    head_color: tuple[int, int, int]
    trail: list[tuple[int, int]]

    def __init__(self, name, pos, direction, color, head_color):
        self.name = name
        self.pos = pos
        self.direction = direction
        self.color = color
        self.head_color = head_color
        self.trail = [pos]

    def set_direction(self, new_dir):
        if new_dir == neg(self.direction):
            return
        self.direction = new_dir

    def next_cell(self):
        return add(self.pos, self.direction)

    def commit_move(self, nxt):
        self.pos = nxt
        self.trail.append(nxt)


class TronGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tron Light Cycle — AI Lab")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 22)
        self.font_big = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_mid = pygame.font.SysFont("consolas", 28, bold=True)

        self.round_wins = {"Player": 0, "AI": 0, "Tie": 0}
        self.reset_round()

    def reset_round(self):
        self.state = "RUNNING"
        self.winner = None
        self.round_start_ms = pygame.time.get_ticks()
        self.round_end_ms = None

        self.player = Bike(
            name="Player",
            pos=(5, GRID_H // 2),
            direction=DIRS["RIGHT"],
            color=PLAYER_COLOR,
            head_color=PLAYER_HEAD,
        )
        self.ai = Bike(
            name="AI",
            pos=(GRID_W - 6, GRID_H // 2),
            direction=DIRS["LEFT"],
            color=AI_COLOR,
            head_color=AI_HEAD,
        )

    def occupied_cells(self):
        return set(self.player.trail) | set(self.ai.trail)

    def ai_choose_direction(self):
        occupied = self.occupied_cells()

        candidates = []
        for d in DIR_LIST:
            if d == neg(self.ai.direction):
                continue
            nxt = add(self.ai.pos, d)
            if not in_bounds(nxt):
                continue
            if nxt in occupied:
                continue
            candidates.append(d)

        if not candidates:
            return self.ai.direction

        best_score = None
        best_dirs = []
        for d in candidates:
            nxt = add(self.ai.pos, d)

            space = flood_fill_free_space(nxt, occupied)
            degree = count_safe_neighbors(nxt, occupied)

            # Basic dead-end avoidance: strongly avoid moves that immediately trap us.
            dead_end_penalty = 0
            if degree == 0:
                dead_end_penalty = 10_000
            elif degree == 1:
                dead_end_penalty = 250

            # Greedy heuristic: maximize reachable free space, then prefer more exits.
            score = (space * 10) + (degree * 15) - dead_end_penalty

            # Tiny randomness to avoid repetitive ties.
            score += random.randint(0, 7)

            if best_score is None or score > best_score:
                best_score = score
                best_dirs = [d]
            elif score == best_score:
                best_dirs.append(d)

        return random.choice(best_dirs)

    def end_round(self, winner):
        self.state = "GAME_OVER"
        self.winner = winner
        self.round_end_ms = pygame.time.get_ticks()
        self.round_wins[winner] += 1

    def survival_time_s(self):
        end_ms = self.round_end_ms if self.round_end_ms is not None else pygame.time.get_ticks()
        return max(0.0, (end_ms - self.round_start_ms) / 1000.0)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                if self.state == "RUNNING":
                    if event.key == pygame.K_UP:
                        self.player.set_direction(DIRS["UP"])
                    elif event.key == pygame.K_DOWN:
                        self.player.set_direction(DIRS["DOWN"])
                    elif event.key == pygame.K_LEFT:
                        self.player.set_direction(DIRS["LEFT"])
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_direction(DIRS["RIGHT"])
                else:
                    if event.key in (pygame.K_r, pygame.K_SPACE):
                        self.reset_round()

    def step(self):
        if self.state != "RUNNING":
            return

        self.ai.set_direction(self.ai_choose_direction())

        occupied = self.occupied_cells()

        p_next = self.player.next_cell()
        a_next = self.ai.next_cell()

        # Collisions are evaluated using the current occupied trails.
        p_crash = (not in_bounds(p_next)) or (p_next in occupied)
        a_crash = (not in_bounds(a_next)) or (a_next in occupied)

        # Head-on collisions (same next cell) or swapping positions both crash.
        if p_next == a_next:
            p_crash = True
            a_crash = True
        if p_next == self.ai.pos and a_next == self.player.pos:
            p_crash = True
            a_crash = True

        if p_crash and a_crash:
            self.end_round("Tie")
            return
        if p_crash:
            self.end_round("AI")
            return
        if a_crash:
            self.end_round("Player")
            return

        self.player.commit_move(p_next)
        self.ai.commit_move(a_next)

    def draw_grid(self):
        for x in range(GRID_W + 1):
            px = x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (px, PANEL_H), (px, WIN_H))
        for y in range(GRID_H + 1):
            py = PANEL_H + y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (0, py), (WIN_W, py))

    def draw_trails(self, bike):
        for cell in bike.trail[:-1]:
            pygame.draw.rect(self.screen, bike.color, cell_rect(cell))
        pygame.draw.rect(self.screen, bike.head_color, cell_rect(bike.trail[-1]))

    def draw_panel(self):
        pygame.draw.rect(self.screen, (14, 14, 20), pygame.Rect(0, 0, WIN_W, PANEL_H))
        pygame.draw.line(self.screen, GRID_LINE, (0, PANEL_H - 1), (WIN_W, PANEL_H - 1))

        time_s = self.survival_time_s()
        status = f"Time: {time_s:0.1f}s"
        score = f"Wins  Player: {self.round_wins['Player']}   AI: {self.round_wins['AI']}   Tie: {self.round_wins['Tie']}"

        self.screen.blit(self.font.render(status, True, TEXT), (12, 10))
        self.screen.blit(self.font.render(score, True, MUTED), (12, 38))

    def draw_game_over(self):
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "Tie":
            title = "TIE!"
            subtitle = "Head-on crash."
            title_color = (220, 220, 235)
        elif self.winner == "Player":
            title = "YOU WIN"
            subtitle = "AI crashed."
            title_color = PLAYER_HEAD
        else:
            title = "AI WINS"
            subtitle = "You crashed."
            title_color = AI_HEAD

        t = self.font_big.render(title, True, title_color)
        s = self.font_mid.render(subtitle, True, TEXT)
        time_s = self.font.render(f"Survived: {self.survival_time_s():0.1f}s", True, MUTED)
        hint = self.font.render("Press R / Space to restart  •  Esc to quit", True, TEXT)

        cx = WIN_W // 2
        cy = WIN_H // 2

        self.screen.blit(t, t.get_rect(center=(cx, cy - 60)))
        self.screen.blit(s, s.get_rect(center=(cx, cy - 15)))
        self.screen.blit(time_s, time_s.get_rect(center=(cx, cy + 25)))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 70)))

    def draw(self):
        self.screen.fill(BG)
        self.draw_panel()
        self.draw_grid()
        self.draw_trails(self.player)
        self.draw_trails(self.ai)

        if self.state == "GAME_OVER":
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.step()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    TronGame().run()

