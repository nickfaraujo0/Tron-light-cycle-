from dataclasses import dataclass
from utils import add, neg

@dataclass
class Bike:
    name: str
    pos: tuple[int, int]
    direction: tuple[int, int]
    color: tuple[int, int, int]
    glow_color: tuple[int, int, int]
    head_color: tuple[int, int, int]
    trail: list[tuple[int, int]]

    def __init__(self, name, pos, direction, color, glow_color, head_color):
        self.name = name
        self.pos = pos
        self.direction = direction
        self.color = color
        self.glow_color = glow_color
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
