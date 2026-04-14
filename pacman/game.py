#!/usr/bin/env python3

import pathlib
import curses
from model import *

# Refined border definitions for collision detection
BORDERS = ['═', '║', '╔', '╗', '╚', '╝', 'x', '-']

class PacmanGameEngine:
    """The class handles game flow and state transitions."""
    
    def __init__(self):
        pass

    @staticmethod
    def __set_up(level_number):
        # Validate input
        if not isinstance(level_number, int):
            raise TypeError("'level_number' must be an integer")
        if level_number < 0:
            raise ValueError("'level_number' must be a positive integer")
        
        # Initialize curses
        window = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        
        window.nodelay(1)
        window.keypad(1)
        
        # Load game data
        level = Level.load(level_number)
        scene = Scene(window, level)
        
        return window, level, scene

    @staticmethod
    def _tear_down(window):
        # Restore terminal settings safely
        window.clear()
        window.refresh()
        curses.nocbreak()
        window.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def __handle_input(self, window, pacman, pmap):
        """Captures input and validates potential direction changes."""
        button = window.getch()
        
        if button == ord('q'):
            return "QUIT"
            
        # Check for potential moves (Input Validation)
        new_dir = None
        if button in [ord('w'), curses.KEY_UP]:
            new_dir = (-1, 0)
        elif button in [ord('s'), curses.KEY_DOWN]:
            new_dir = (1, 0)
        elif button in [ord('a'), curses.KEY_LEFT]:
            new_dir = (0, -1)
        elif button in [ord('d'), curses.KEY_RIGHT]:
            new_dir = (0, 1)

        # Only update direction if there's no wall in that direction
        if new_dir:
            target_y, target_x = pacman.y + new_dir[0], pacman.x + new_dir[1]
            if 0 <= target_y < pmap.height and 0 <= target_x < pmap.width:
                if pmap.grid[target_y][target_x] not in BORDERS:
                    pacman.set_direction(new_dir[0], new_dir[1])
        
        return "CONTINUE"

    def __run(self, window, level, scene):
        pacman = level.pacman
        pmap = level.pmap
        ghosts = level.ghosts
        bonuses = level.bonuses
        
        main_loop = 0
        power_timer = 0
        eaten_ghost_multiplier = 0

        # Standing Start Announcement (Ready!)
        for _ in range(15):
            scene.standing_start_announcement = True
            scene.render()
            curses.napms(100)
        scene.standing_start_announcement = False

        while True:
            main_loop += 1
            
            # 1. Input Handling
            if self.__handle_input(window, pacman, pmap) == "QUIT":
                break

            # 2. Movement & Physics
            # Check if current direction hits a wall
            next_y, next_x = pacman.y + pacman.dir_y, pacman.x + pacman.dir_x
            if pmap.grid[next_y][next_x] in BORDERS:
                pacman.set_direction(0, 0) # Stop at wall
            
            pacman.play(scene) # Move Pac-Man

            # 3. Collision Logic (Items)
            current_tile = pmap.grid[pacman.y][pacman.x]
            if current_tile == '·':
                pmap.grid[pacman.y][pacman.x] = ' '
                scene.points += 10
            elif current_tile == '•':
                pmap.grid[pacman.y][pacman.x] = ' '
                scene.points += 50
                scene.power_capsule = True
                power_timer = 40 # Power mode duration
                eaten_ghost_multiplier = 0

            # 4. Ghost AI & Interaction
            for ghost in ghosts:
                # Handle movement (Exit cage first, then chase)
                if main_loop > 10:
                    ghost.play(scene, level)
                
                # Check collision with Pac-Man
                if pacman.x == ghost.x and pacman.y == ghost.y:
                    if scene.power_capsule and not ghost.is_eaten:
                        # Pac-man eats ghost
                        ghost.is_eaten = True
                        eaten_ghost_multiplier += 1
                        scene.points += (200 * eaten_ghost_multiplier)
                    elif not scene.power_capsule:
                        # Ghost eats Pac-man
                        scene.death = True

            # 5. Handle Power Capsule Expiration
            if scene.power_capsule:
                power_timer -= 1
                if power_timer < 10:
                    scene.flash = True # Start flashing before ending
                if power_timer <= 0:
                    scene.power_capsule = False
                    scene.flash = False
                    for g in ghosts: g.is_eaten = False

            # 6. Death Logic
            if scene.death:
                scene.render()
                curses.napms(1500)
                scene.life -= 1
                if scene.life <= 0:
                    break
                # Reset positions
                pacman.reset()
                for g in ghosts: g.reset()
                scene.death = False

            # 7. Win Condition
            if not any('·' in row or '•' in row for row in pmap.grid):
                scene.render()
                curses.napms(2000
