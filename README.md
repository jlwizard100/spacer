# 3D Spaceship Simulator

This project is a 3D spaceship simulator with a Newtonian physics model, where the objective is to fly through a series of race gates while avoiding asteroids.

The game loads a course from `course.json`. You can create and edit your own courses using the included designer tool.

## Running the Game

```bash
# Make sure you have the dependencies installed
pip install -r requirements.txt

# Run the main game
python main.py
```

## Course Designer (`designer.py`)

A standalone tool is included to create and edit race courses.

### Running the Designer

```bash
python designer.py
```

### General Controls

*   **Adjust Boundary Size:** `CTRL` + `Page Up` / `Page Down`

### Camera Controls

*   **Orbit:** Right-click + Drag
*   **Pan:** Middle-click + Drag
*   **Zoom:** Mouse Wheel

### Object Creation & Population

*   **Create Gate:** `G` key
*   **Create Asteroid:** `A` key
*   **Populate with Random Asteroids:** `P` key (adds 50 random asteroids)

### Selection & Deletion

*   **Select Object:** Left-click on a gate or asteroid.
*   **Delete Selected Object:** `DELETE` key.

### Editing a Selected Object

*   **Move (X/Z Plane):** Arrow Keys
*   **Move (Up/Down Y-axis):** `Page Up` / `Page Down` (without CTRL)
*   **Rotate (Yaw):** `Q` / `E` keys
*   **Rotate (Pitch):** `R` / `F` keys
*   **Rotate (Roll):** `T` / `G` keys

### Asteroid-Specific Editing

*   **Change Size:** `+` and `-` keys.
*   **Change Model:** `1`, `2`, and `3` keys.

### File Operations

*   **Load From...:** `CTRL + L`. Opens a dialog to select a course file.
*   **Save (Quick Save):** `CTRL + S`. Saves changes to the current file.
*   **Save As...:** `CTRL + SHIFT + S`. Opens a dialog to save the course to a new file.

### UI Display

*   The sidebar on the right displays information about the current file, boundary size, and the properties of any selected object.