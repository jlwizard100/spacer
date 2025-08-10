import numpy as np

# --- Quaternion helper for gate setup ---
def q_from_axis_angle(axis, angle):
    """Creates a quaternion from an axis and an angle."""
    axis = axis / np.linalg.norm(axis)
    half_angle = angle / 2.0
    w = np.cos(half_angle)
    x, y, z = axis * np.sin(half_angle)
    return np.array([w, x, y, z])

class Asteroid:
    """
    Represents a single asteroid in the game world.
    """
    def __init__(self, position, size):
        self.position = position
        self.size = size
        # Asteroids are static and don't rotate for now
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])
        self.vertices, self.edges = self._generate_model()

    def _generate_model(self):
        """Creates a randomized, rocky-looking 3D model."""
        # Start with a base cube shape
        base_verts = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ])
        # Scale it by the asteroid's size and add random perturbations
        verts = base_verts * self.size
        verts += np.random.uniform(-self.size/2, self.size/2, verts.shape)

        edges = [
            (0,1), (1,2), (2,3), (3,0), # Bottom face
            (4,5), (5,6), (6,7), (7,4), # Top face
            (0,4), (1,5), (2,6), (3,7)  # Connecting edges
        ]
        return verts, edges

class Gate:
    """
    Represents a single race gate in the obstacle course.
    """
    def __init__(self, position, orientation, size=30):
        self.position = position
        self.orientation = orientation
        self.size = size # The radius of the gate opening
        self.is_passed = False

        # A simple square wireframe model for the gate
        s = self.size
        self.vertices = np.array([
            [-s, -s, 0], [s, -s, 0], [s, s, 0], [-s, s, 0]
        ])
        self.edges = [(0,1), (1,2), (2,3), (3,0)]


def create_asteroid_field(num_asteroids, field_size):
    """Generates a list of randomly placed asteroids."""
    asteroids = []
    for _ in range(num_asteroids):
        # Position asteroids in a large cubic volume
        pos = np.random.uniform(-field_size/2, field_size/2, 3)
        size = np.random.uniform(10, 60) # Asteroids are 10m to 60m in size

        # Ensure asteroids don't spawn too close to the player's starting point
        if np.linalg.norm(pos) < 300:
            pos = pos / np.linalg.norm(pos) * 300 # Push them out to a 300m radius

        asteroids.append(Asteroid(pos, size))
    return asteroids

def create_gate_course():
    """Creates a predefined sequence of 8 gates for the race course."""
    gates = []
    gate_size = 40 # Gates have a 40m opening

    # A simple, winding course with 8 gates
    path = [
        {'pos': [0, 0, 500], 'axis': [1,0,0], 'angle': 0},
        {'pos': [400, 200, 1000], 'axis': [0,1,0], 'angle': np.pi/4},
        {'pos': [400, 200, 1500], 'axis': [0,1,0], 'angle': np.pi/2},
        {'pos': [0, 400, 2000], 'axis': [1,0,0], 'angle': -np.pi/4},
        {'pos': [-400, 0, 2500], 'axis': [0,1,0], 'angle': -np.pi/2},
        {'pos': [-400, -200, 3000], 'axis': [0,1,0], 'angle': -np.pi/4},
        {'pos': [0, -400, 3500], 'axis': [1,0,0], 'angle': np.pi/4},
        {'pos': [0, 0, 4000], 'axis': [1,0,0], 'angle': 0},
    ]

    for node in path:
        pos = np.array(node['pos'])
        orient = q_from_axis_angle(np.array(node['axis']), node['angle'])
        gates.append(Gate(pos, orient, gate_size))

    return gates
