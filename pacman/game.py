#!/usr/bin/env python3

import pathlib
import curses
from model import *

# Refined border definitions for collision detection
BORDERS = ['═', '║', '╔', '╗', '╚', '╝', 'x', '-']

class PacmanGameEngine:
    """The class handles game flow, input, and state transitions."""
    
    def __init__(self):
        pass

    @staticmethod
    def __set_up(level_number):
        """Initializes the terminal window and loads level data."""
        # Initialize curses
        window = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0) # Hide cursor
        
        window.nodelay(1)  # Non-blocking input
        window.keypad(1)   # Enable arrow keys
        
        # Load game data from model.py
        level = Level.load(level_number)
        
        # Initialize Palette (from model/previous code) and Scene
        palette = Palette()
        scene = Scene(window, level, palette)
        
        return window, level, scene

    @staticmethod
    def _tear_down(window):
        """Restores terminal settings safely to prevent terminal corruption."""
        window.clear()
        window.refresh()
        curses.nocbreak()
        window.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def __handle_input(self, window, pacman, pmap):
        """Captures input and checks if the new direction is valid (not a wall)."""
        button = window.getch()
        
        if button == ord('q'):
            return "QUIT"
            
        new_dir = None
        if button in [ord('w'), curses.KEY_UP]:
            new_dir = (-1, 0) # dy, dx
        elif button in [ord('s'), curses.KEY_DOWN]:
            new_dir = (1, 0)
        elif button in [ord('a'), curses.KEY_LEFT]:
            new_dir = (0, -1)
        elif button in [ord('d'), curses.KEY_RIGHT]:
            new_dir = (0, 1)

        # Only allow direction change if the path is clear
        if new_dir:
            target_y, target_x = pacman.y + new_dir[0], pacman.x + new_dir[1]
            if 0 <= target_y < pmap.height and 0 <= target_x < pmap.width:
                if pmap.grid[target_y][target_x] not in BORDERS:
                    # Assuming set_direction updates internal intended velocity
                    pacman.dir_y, pacman.dir_x = new_dir[0], new_dir[1]
        
        return "CONTINUE"

    def __run(self, window, level, scene):
        """Main game loop."""
        pacman = level.pacman
        pmap = level.pmap
        ghosts = level.ghosts
        
        main_loop = 0
        power_timer = 0
        eaten_ghost_multiplier = 0

        # Game Start Sequence
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
            
            # Boundary check
            if 0 <= next_y < pmap.height and 0 <= next_x < pmap.width:
                if pmap.grid[next_y][next_x] in BORDERS:
                    pacman.dir_y, pacman.dir_x = 0, 0 # Stop at wall
            
            # Move Pac-Man using the logic defined in AnimatedCharacter
            pacman.move(pacman.dir_x, pacman.dir_y, pmap)

            # 3. Collision Logic (Items)
            current_tile = pmap.grid[pacman.y][pacman.x]
            if current_tile == '·':
                pmap.grid[pacman.y][pacman.x] = ' '
                scene.points += 10
            elif current_tile == '•':
                pmap.grid[pacman.y][pacman.x] = ' '
                scene.points += 50
                scene.power_capsule = True
                power_timer = 60 # Duration
                eaten_ghost_multiplier = 0

            # 4. Ghost AI & Interaction
            for ghost in ghosts:
                # Basic AI update (random/avoiding backtrack)
                if main_loop > 10:
                    ghost.update_ai(pmap)
                
                # Check collision with Pac-Man
                if pacman.x == ghost.x and pacman.y == ghost.y:
                    if scene.power_capsule:
                        # Pac-man eats ghost - move ghost back to start (pseudo-reset)
                        scene.points += (200 * (2 ** eaten_ghost_multiplier))
                        eaten_ghost_multiplier += 1
                        # Note: In a full game, ghost would return to spawn
                    else:
                        scene.death = True

            # 5. Handle Power Capsule Expiration
            if scene.power_capsule:
                power_timer -= 1
                if power_timer < 15:
                    scene.flash = True 
                if power_timer <= 0:
                    scene.power_capsule = False
                    scene.flash = False

            # 6. Render & Loop Control
            scene.render()
            if scene.death:
                curses.napms(1000)
                scene.life -= 1
                if scene.life <= 0: break
                scene.death = False
                # Re-reset positions here if necessary

            curses.napms(100) # Frame rate control
            window.clear()

    def start(self, level_number):
        window, level, scene = self.__set_up(level_number)
        try:
            self.__run(window, level, scene)
        finally:
            self._tear_down(window)

def main():
    game = PacmanGameEngine()
    game.start(1)

if __name__ == '__main__':
    main()
