#!/usr/bin/env python3

import json
import pathlib
import math
import random
from map_utils import *

# --- Constants ---
PACMAN, BLINKY, PINKY, INKY, CLYDE = "pacman", "blinky", "pinky", "inky", "clyde"
SYMBOL, CHERRY, POINTS, EYES = "symbol", "cherry", "points", '👀'
STANDING_START_ANNOUNCEMENT = "standing_start_announcement"
PACMAN_SYMBOL, READY, EXPLODING, SKULL = "ᗧ", "READY!", '💥', '💀'
X, Y = "x", "y"

BORDER_SYMBOL = ['═', '║', '╔', '╗', '╚', '╝']
NOT_WALKABLE = BORDER_SYMBOL + ['-', 'x']

# --- Graph Logic for AI Pathfinding ---

class Cell:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.neighbor_cells = []

    def add_neighbor_cell(self, cell):
        if cell not in self.neighbor_cells:
            self.neighbor_cells.append(cell)

    def is_intersection(self):
        # Intersections have more than 2 neighbors (excluding dead ends)
        return len(self.neighbor_cells) > 2

class Node:
    def __init__(self, cell):
        self.cell = cell
        self.x = cell.x
        self.y = cell.y
        self.neighbor_nodes = [] # List of (distance, Node)

    def add_neighbor_node(self, node, distance):
        self.neighbor_nodes.append((distance, node))

# --- Core Game Objects ---

class Object:
    def __init__(self, x, y, symbol, color):
        # Input Validation
        if not all(isinstance(i, int) for i in [x, y]):
            raise TypeError("Coordinates must be integers.")
        if not isinstance(color, tuple) or len(color) != 3:
            raise ValueError("Color must be an RGB tuple (R, G, B).")
            
        self._x = x
        self._y = y
        self.__symbol = symbol
        self.__color = color

    @property
    def x(self): return self._x
    @property
    def y(self): return self._y
    @property
    def symbol(self): return self.__symbol
    @property
    def color(self): return self.__color

class AnimatedCharacter(Object):
    def move(self, dx, dy, pmap):
        new_x, new_y = self._x + dx, self._y + dy
        
        # Tunneling Logic
        if dx == -1 and self._x == 0:
            new_x = pmap.width - 1
        elif dx == 1 and self._x == pmap.width - 1:
            new_x = 0

        # Collision Check
        if 0 <= new_y < pmap.height and 0 <= new_x < pmap.width:
            if pmap.grid[new_y][new_x] not in NOT_WALKABLE:
                self._x, self._y = new_x, new_y

class Pacman(AnimatedCharacter):
    def __init__(self, x, y, symbol, color):
        super().__init__(x, y, symbol, color)

class Ghost(AnimatedCharacter):
    def __init__(self, x, y, color):
        super().__init__(x, y, 'ᗣ', color)
        self.last_pos = (x, y)

    def update_ai(self, pmap):
        """Random movement that avoids immediate backtracking."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        valid_moves = []
        
        for dx, dy in directions:
            nx, ny = self._x + dx, self._y + dy
            if 0 <= ny < pmap.height and 0 <= nx < pmap.width:
                if pmap.grid[ny][nx] not in NOT_WALKABLE:
                    if (nx, ny) != self.last_pos:
                        valid_moves.append((dx, dy))

        if not valid_moves: # Dead end or only backtracking possible
            valid_moves = [(- (self._x - self.last_pos[0]), - (self._y - self.last_pos[1]))]

        dx, dy = random.choice(valid_moves)
        self.last_pos = (self._x, self._y)
        self.move(dx, dy, pmap)

# --- Map and Level Management ---

class Map:
    def __init__(self, data):
        self.grid = [list(line) for line in data]
        self.height = len(data)
        self.width = max(len(line) for line in data) if data else 0

    @staticmethod
    def load_map(path):
        # Uses your existing map_utils logic
        raw_data = load_map(path)
        decompressed = uncompress_map_with_rle(raw_data)
        pretty = prettify_map(decompressed)
        return Map(pretty)

class Level:
    def __init__(self, number, pmap, objects):
        self.number = number
        self.pmap = pmap
        self.pacman = objects[0]
        self.ghosts = objects[1:5]
        self.bonus = objects[5]

    @classmethod
    def load(cls, number, root_path="./"):
        base_path = pathlib.Path(root_path) / "map" / f"level{number}"
        
        # Load JSON Metadata
        with open(f"{base_path}.json", "r") as f:
            data = json.load(f)

        objs = [
            Pacman(data[PACMAN][X], data[PACMAN][Y], PACMAN_SYMBOL, (255, 255, 0)),
            Ghost(data[PINKY][X], data[PINKY][Y], (255, 184, 255)),
            Ghost(data[INKY][X], data[INKY][Y], (0, 255, 255)),
            Ghost(data[BLINKY][X], data[BLINKY][Y], (255, 0, 0)),
            Ghost(data[CLYDE][X], data[CLYDE][Y], (255, 184, 82)),
            Object(data[CHERRY][0][X], data[CHERRY][0][Y], data[CHERRY][0][SYMBOL], (255, 0, 0))
        ]
        
        return cls(number, Map.load_map(str(base_path) + ".rle"), objs)
