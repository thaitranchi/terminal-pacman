#!/usr/bin/env python3

import json
import pathlib
from map_utils import *

class Map:
    def __init__(self, grid):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])

class Entity:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.dir_x = 0
        self.dir_y = 0

    def move(self, dx, dy, pmap, borders):
        nx, ny = self.x + dx, self.y + dy
        # Collision logic inside the model
        if 0 <= ny < pmap.height and 0 <= nx < pmap.width:
            if pmap.grid[ny][nx] not in borders:
                self.x, self.y = nx, ny

class Level:
    def __init__(self, pmap, pacman, ghosts):
        self.pmap = pmap
        self.pacman = pacman
        self.ghosts = ghosts

    @classmethod
    def load(cls, level_num):
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
