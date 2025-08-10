import pygame
import numpy as np
from utils import qv_rotate

# A simple 3D wireframe model for the spaceship (vertices in local/model space)
# The shape is a wedge/pointer, with the nose pointing along the +Z axis.
SHIP_VERTICES = np.array([
    [0, 0, 20],      # 0: Nose tip
    [-7.5, 5, -20],  # 1: Back Top Left
    [7.5, 5, -20],   # 2: Back Top Right
    [7.5, -5, -20],  # 3: Back Bottom Right
    [-7.5, -5, -20], # 4: Back Bottom Left
])

# Edges define which vertices to connect to form the wireframe structure
SHIP_EDGES = [
    (0, 1), (0, 2), (0, 3), (0, 4), # Lines from nose to the back corners
    (1, 2), (2, 3), (3, 4), (4, 1), # The rectangular back face
]


class Camera:
    """
    Manages the viewpoint and 3D-to-2D projection.
    """
    def __init__(self, screen_width, screen_height, fov=90):
        self.width = screen_width
        self.height = screen_height
        self.fov = fov
        self.near_plane = 0.5  # Objects closer than this won't be rendered

        self.position = np.array([0.0, 0.0, -50.0])
        self.target = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

    def update(self, ship):
        """Updates the camera to follow the ship (chase camera)."""
        self.target = ship.position
        # Position the camera behind and slightly above the ship, relative to ship's orientation
        pos_offset = ship.get_forward_vector() * -60 # 60 meters behind
        pos_offset += ship.get_up_vector() * 20      # 20 meters above
        self.position = ship.position + pos_offset
        # Align camera's 'up' with the ship's 'up' to follow rolls
        self.up = ship.get_up_vector()

    def project_point(self, point_3d):
        """Projects a single 3D point from world space to 2D screen space."""
        # 1. Compute camera basis vectors (view matrix components)
        forward = self.target - self.position
        if np.linalg.norm(forward) > 0:
            forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, self.up)
        if np.linalg.norm(right) > 0:
            right = right / np.linalg.norm(right)

        camera_up = np.cross(right, forward)

        # 2. Transform point from world space to camera space
        p_camera = point_3d - self.position
        p_camera_x = np.dot(p_camera, right)
        p_camera_y = np.dot(p_camera, camera_up)
        p_camera_z = np.dot(p_camera, forward)

        # 3. Basic clipping: if the point is behind the camera, don't draw it.
        if p_camera_z < self.near_plane:
            return None

        # 4. Perspective Projection
        # The projected coordinates are scaled by their distance (z).
        fov_rad = np.deg2rad(self.fov)
        scale = 1 / (np.tan(fov_rad / 2) * p_camera_z)
        x_proj = p_camera_x * scale
        y_proj = p_camera_y * scale

        # 5. Convert from normalized coordinates (-1 to 1) to screen coordinates
        x_screen = (x_proj + 1) * 0.5 * self.width
        y_screen = (1 - (y_proj + 1) * 0.5) * self.height # Y is inverted on screens

        return (int(x_screen), int(y_screen))


def draw_wireframe_object(screen, camera, position, orientation, vertices, edges, color):
    """A generic function to draw any wireframe object."""
    # Transform local model vertices to their position in the 3D world
    world_vertices = [qv_rotate(orientation, v) + position for v in vertices]

    # Project the 3D world vertices to 2D screen points
    screen_points = [camera.project_point(v) for v in world_vertices]

    # Draw the lines (edges) of the wireframe
    for edge in edges:
        p1 = screen_points[edge[0]]
        p2 = screen_points[edge[1]]

        # Only draw the line if both points are in front of the camera
        if p1 is not None and p2 is not None:
            pygame.draw.line(screen, color, p1, p2, 1)

def draw_ship(screen, ship, camera):
    """Draws the spaceship's wireframe model on the screen."""
    draw_wireframe_object(screen, camera, ship.position, ship.orientation, SHIP_VERTICES, SHIP_EDGES, (255, 255, 255))

def draw_asteroid(screen, asteroid, camera):
    """Draws an asteroid's wireframe model."""
    color = (160, 82, 45) # Sienna brown
    draw_wireframe_object(screen, camera, asteroid.position, asteroid.orientation, asteroid.vertices, asteroid.edges, color)

def draw_gate(screen, gate, camera):
    """Draws a gate's wireframe model."""
    # Green for active, red for passed
    color = (0, 255, 0) if not gate.is_passed else (255, 0, 0)
    draw_wireframe_object(screen, camera, gate.position, gate.orientation, gate.vertices, gate.edges, color)
