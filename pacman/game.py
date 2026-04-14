#!/usr/bin/env python3

import json
import pathlib
import curses
import math
import random
from map_utils import *

# Constants
PACMAN, BLINKY, PINKY, INKY, CLYDE = "pacman", "blinky", "pinky", "inky", "clyde"
SYMBOL, CHERRY, POINTS, EYES = "symbol", "cherry", "points", '👀'
STANDING_START_ANNOUNCEMENT = "standing_start_announcement"
PACMAN_SYMBOL, READY, EXPLODING, SKULL = "ᗧ", "READY!", '💥', '💀'
X, Y = "x", "y"

# Colors (RGB 0-255)
COLOR_RGB_PACMAN = (255, 255, 0)
COLOR_RGB_BLINKY = (255, 0, 0)
COLOR_RGB_PINKY = (255, 184, 255)
COLOR_RGB_INKY = (0, 255, 255)
COLOR_RGB_CLYDE = (255, 184, 82)

NOT_WALKABLE = ['═', '║', '╔', '╗', '╚', '╝', '-', 'x']

class Object:
    def __init__(self, x, y, symbol, color):
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("Coordinates must be integers.")
        self._x, self._y = x, y
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
    def set_direction(self, dy, dx, pmap):
        new_x, new_y = self._x + dx, self._y + dy
        
        # Tunneling logic
        if dx == -1 and self._x == 0:
            new_x = pmap.width - 1
        elif dx == 1 and self._x == pmap.width - 1:
            new_x = 0
            
        if pmap.grid[new_y][new_x] not in NOT_WALKABLE:
            self._x, self._y = new_x, new_y

class Ghost(AnimatedCharacter):
    def __init__(self, x, y, color):
        super().__init__(x, y, 'ᗣ', color)
        self.last_pos = (x, y)

    def play(self, scene, level):
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for dy, dx in moves:
            nx, ny = self._x + dx, self._y + dy
            if 0 <= ny < level.pmap.height and 0 <= nx < level.pmap.width:
                if level.pmap.grid[ny][nx] not in NOT_WALKABLE:
                    if (nx, ny) != self.last_pos:
                        self.last_pos = (self._x, self._y)
                        self._x, self._y = nx, ny
                        break

class Pacman(AnimatedCharacter):
    def __init__(self, x, y, symbol, color):
        super().__init__(x, y, symbol, color)

class Map:
    def __init__(self, data):
        self.grid = [list(line) for line in data]
        self.height = len(data)
        self.width = max(len(line) for line in data) if data else 0

    @staticmethod
    def load_map(path):
        return Map(prettify_map(uncompress_map_with_rle(load_map(path))))

class Level:
    def __init__(self, number, pmap, objects):
        self.number = number
        self.pmap = pmap
        self.pacman = objects[0]
        self.ghosts = objects[1:5]
        self.bonus = objects[5]
        self.start_info = objects[6]

    @classmethod
    def load(cls, number, root="./"):
        path = pathlib.Path(root) / "map" / f"level{number}"
        with open(f"{path}.json", "r") as f:
            data = json.load(f)
        
        objs = [
            Pacman(data[PACMAN][X], data[PACMAN][Y], PACMAN_SYMBOL, COLOR_RGB_PACMAN),
            Ghost(data[PINKY][X], data[PINKY][Y], COLOR_RGB_PINKY),
            Ghost(data[INKY][X], data[INKY][Y], COLOR_RGB_INKY),
            Ghost(data[BLINKY][X], data[BLINKY][Y], COLOR_RGB_BLINKY),
            Ghost(data[CLYDE][X], data[CLYDE][Y], COLOR_RGB_CLYDE),
            Object(data[CHERRY][0][X], data[CHERRY][0][Y], data[CHERRY][0][SYMBOL], (255, 0, 0)),
            Object(data[STANDING_START_ANNOUNCEMENT][X], data[STANDING_START_ANNOUNCEMENT][Y], "", (0,0,0))
        ]
        return cls(number, Map.load_map(f"{path}.rle"), objs)

class Scene:
    def __init__(self, window, level, palette):
        self.window = window
        self.level = level
        self.palette = palette
        self.points = 0
        self.life = 3

    def render(self):
        self.window.erase()
        h, w = self.window.getmaxyx()
        ry, rx = (h // 2) - (self.level.pmap.height // 2), (w // 2) - (self.level.pmap.width // 2)

        # Draw Map
        for y, line in enumerate(self.level.pmap.grid):
            for x, char in enumerate(line):
                color = self.palette.get_composite_color((25, 25, 255)) if char in BORDERS else self.palette.get_composite_color((255, 255, 255))
                self.window.addch(y + ry, x + rx, char, color)

        # Draw Entities
        p = self.level.pacman
        self.window.addch(p.y + ry, p.x + rx, p.symbol, self.palette.get_composite_color(p.color))
        
        for g in self.level.ghosts:
            self.window.addch(g.y + ry, g.x + rx, g.symbol, self.palette.get_composite_color(g.color))

        self.window.addstr(0, 0, f" SCORE: {self.points} | LIVES: {self.life}", curses.A_BOLD)
        self.window.refresh()
