import pygame
from settings import GRID_W, GRID_H, CELL_SIZE, PANEL_H

def add(p, d):
    return (p[0] + d[0], p[1] + d[1])

def neg(d):
    return (-d[0], -d[1])

def in_bounds(p):
    return 0 <= p[0] < GRID_W and 0 <= p[1] < GRID_H

def cell_rect(cell):
    x, y = cell
    return pygame.Rect(x * CELL_SIZE, PANEL_H + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
