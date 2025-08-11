import json
import numpy as np
from utils import q_multiply

# --- Quaternion helper for gate setup ---
def q_from_axis_angle(axis, angle):
    """Creates a quaternion from an axis and an angle."""
    axis = axis / np.linalg.norm(axis)
    half_angle = angle / 2.0
    w = np.cos(half_angle)
    x, y, z = axis * np.sin(half_angle)
    return np.array([w, x, y, z])

# --- Asteroid Model Library ---
# A library of predefined wireframe models for asteroids.
# The vertices are defined in a normalized space (e.g., a 1x1x1 cube)
# and will be scaled by the asteroid's size.

_CUBE_VERTICES = np.array([
    [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
    [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
])
_CUBE_EDGES = [
    (0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

_TETRA_VERTICES = np.array([
    [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, -0.5], [0.5, -0.5, -0.5]
])
_TETRA_EDGES = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]

# A pre-randomized "jagged" asteroid model for variety.
# This uses a fixed seed to ensure it's the same every time.
np.random.seed(42)
_JAGGED_VERTICES = _CUBE_VERTICES * 1.2 + np.random.uniform(-0.3, 0.3, _CUBE_VERTICES.shape)
np.random.seed(None) # Reset seed

ASTEROID_MODELS = {
    "asteroid_cube_simple": (_CUBE_VERTICES, _CUBE_EDGES),
    "asteroid_tetrahedron": (_TETRA_VERTICES, _TETRA_EDGES),
    "asteroid_jagged_1": (_JAGGED_VERTICES, _CUBE_EDGES), # Use cube edges for jagged
}

class Asteroid:
    """
    Represents a single asteroid in the game world.
    """
    def __init__(self, position, size, orientation, angular_velocity, model_id):
        self.position = np.array(position, dtype=float)
        self.orientation = np.array(orientation, dtype=float)
        self.angular_velocity = np.array(angular_velocity, dtype=float)

        self.base_vertices = None
        self.edges = None
        self.model_id = None
        self.size = None

        self.set_model(model_id)
        self.set_size(size)

    def set_size(self, new_size):
        """Updates the asteroid's size and rescales its vertices."""
        self.size = new_size
        self.vertices = self.base_vertices * self.size

    def set_model(self, new_model_id):
        """Changes the asteroid's model and rescales the new vertices."""
        if new_model_id == self.model_id:
            return

        self.model_id = new_model_id
        self.base_vertices, self.edges = ASTEROID_MODELS.get(
            self.model_id, ASTEROID_MODELS["asteroid_cube_simple"]
        )
        # Ensure vertices are rescaled if size is already set
        if self.size is not None:
            self.set_size(self.size)

    def update(self, dt):
        """Updates the asteroid's orientation over time."""
        w_quat = np.concatenate(([0.0], self.angular_velocity))
        q_derivative = 0.5 * q_multiply(self.orientation, w_quat)
        self.orientation += q_derivative * dt

        # Normalize the quaternion
        norm = np.linalg.norm(self.orientation)
        if norm > 0:
            self.orientation /= norm

class Gate:
    """
    Represents a single race gate in the obstacle course.
    """
    def __init__(self, position, orientation, size=30):
        self.position = np.array(position)
        self.orientation = np.array(orientation)
        self.size = size # The radius of the gate opening
        self.is_passed = False

        # A simple square wireframe model for the gate
        s = self.size
        self.vertices = np.array([
            [-s, -s, 0], [s, -s, 0], [s, s, 0], [-s, s, 0]
        ])
        self.edges = [(0,1), (1,2), (2,3), (3,0)]


def load_course_from_file(filepath):
    """
    Loads a course definition from a JSON file.
    Returns a tuple of (gates, asteroids).
    """
    with open(filepath, 'r') as f:
        data = json.load(f)

    gates = []
    for g_data in sorted(data['race_gates'], key=lambda x: x['gate_number']):
        gate = Gate(
            position=g_data['position'],
            orientation=g_data['orientation'],
            size=g_data['size']
        )
        gates.append(gate)

    asteroids = []
    for a_data in data['asteroids']:
        asteroid = Asteroid(
            position=a_data['position'],
            size=a_data['size'],
            orientation=a_data['orientation'],
            angular_velocity=a_data['angular_velocity'],
            model_id=a_data['model_id']
        )
        asteroids.append(asteroid)

    print(f"INFO: Loaded course '{data['course_name']}' with {len(gates)} gates and {len(asteroids)} asteroids.")
    return gates, asteroids
