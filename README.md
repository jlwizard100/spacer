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

### Camera Controls

*   **Orbit:** Right-click + Drag
*   **Pan:** Middle-click + Drag
*   **Zoom:** Mouse Wheel

### Object Creation

*   **Create Gate:** Press the `G` key. A new gate will appear at the world origin.
*   **Create Asteroid:** Press the `A` key. A new asteroid will appear at the world origin.

### Selection & Deletion

*   **Select Object:** Left-click on a gate or asteroid. The selected object will be highlighted in yellow.
*   **Delete Selected Object:** Press the `DELETE` key.

### Editing a Selected Object

The following controls apply to any selected object (gate or asteroid):

*   **Move (X/Z Plane):** Arrow Keys
*   **Move (Up/Down Y-axis):** `Page Up` / `Page Down`
*   **Rotate (Yaw):** `Q` / `E` keys
*   **Rotate (Pitch):** `R` / `F` keys
*   **Rotate (Roll):** `T` / `G` keys

### Asteroid-Specific Editing

The following controls only apply when an asteroid is selected:

*   **Change Size:** `+` and `-` keys.
*   **Change Model:** `1`, `2`, and `3` keys to cycle through the available wireframe models.

### File Operations

*   **Save Course:** `CTRL + S`. This will save the current layout to `course.json`, overwriting it if it exists.
*   **Load Course:** `CTRL + L`. This will clear the current scene and load the data from `course.json`.