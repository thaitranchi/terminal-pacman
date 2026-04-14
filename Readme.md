# ᗧ Terminal Pac-Man (MVC Edition)

A professional-grade implementation of the classic Pac-Man arcade game running entirely in the terminal. This project demonstrates clean **Model-View-Controller (MVC)** architecture, custom map decompression (**RLE**), and terminal rendering using the `curses` library.

## 🚀 Features
* **MVC Architecture:** Clean separation between game logic, rendering, and input handling.
* **Custom Map Engine:** Supports `.rle` compressed map files and `.json` metadata for level loading.
* **Retro Visuals:** Uses Unicode characters and `curses` color palettes to recreate the 1980s arcade feel.
* **Ghost AI:** Independent movement logic for Blinky, Pinky, Inky, and Clyde.

## 📂 File Structure
```text
pacman
├── main.py           # Entry point: Initializes and starts the Game Engine.
├── controller.py     # The "Brain": Handles the game loop, input, and physics updates.
├── model.py          # The "Data": Defines Entities (Pacman, Ghosts) and Map logic.
├── view.py           # The "Visuals": Manages curses rendering, colors, and UI.
├── map_utils.py      # The "Helpers": Handles RLE decompression and map prettifying.
└── map/              # Assets: Level layouts and spawn coordinates.
```

## 🛠️ Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/thaitranchi/terminal-pacman.git
   cd pacman
   ```
2. **Ensure Python 3.x is installed.**
3. **Run the game:**
   ```bash
   python3 main.py
   ```
   *(Note: For Windows users, it is recommended to use `windows-curses` via `pip install windows-curses`.)*

## 🎮 Controls
* **WASD / Arrow Keys:** Move Pac-Man
* **Q:** Quit the game

## 🧠 Devlog & Architecture
This project was built to showcase how to transition from "scripting" to "software engineering." By separating the **Model** (data) from the **View** (graphics), the game becomes modular. For example, the `view.py` could be swapped from `curses` to `Pygame` without changing any of the core game logic in `model.py`.
