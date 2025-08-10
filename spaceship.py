import numpy as np

# --- Quaternion Helper Functions ---
def q_conjugate(q):
    """Calculates the conjugate of a quaternion."""
    w, x, y, z = q
    return np.array([w, -x, -y, -z])

def q_multiply(q1, q2):
    """Multiplies two quaternions."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    return np.array([w, x, y, z])

def qv_rotate(q, v):
    """Rotates a vector v by a quaternion q."""
    v_quat = np.concatenate(([0.0], v))
    q_conj = q_conjugate(q)
    rotated_v_quat = q_multiply(q_multiply(q, v_quat), q_conj)
    return rotated_v_quat[1:]

class Spaceship:
    """
    Represents the player's spaceship, handling its physics and state.
    """
    def __init__(self):
        # Physical properties from the prompt
        self.mass = 20000.0  # kg

        # Ship dimensions (length: 40m, width: 15m)
        # Body frame: +x is right, +y is up, +z is forward
        dx = 15.0 # width
        dy = 15.0 # height (assuming same as width)
        dz = 40.0 # length

        # Inertia tensor for a solid cuboid.
        I_xx = (1/12) * self.mass * (dy**2 + dz**2)
        I_yy = (1/12) * self.mass * (dx**2 + dz**2)
        I_zz = (1/12) * self.mass * (dx**2 + dy**2)
        self.inertia_tensor = np.diag([I_xx, I_yy, I_zz])
        self.inverse_inertia_tensor = np.linalg.inv(self.inertia_tensor)

        # Moment arms for calculating torque from thrusters
        self.moment_arm_pitch = dz / 2.0 # Thrusters at nose/tail
        self.moment_arm_yaw = dx / 2.0   # Thrusters at wingtips
        self.moment_arm_roll = np.sqrt((dx/2)**2 + (dy/2)**2) # Assume roll thrusters are at corners

        # State Vectors
        self.position = np.array([0.0, 0.0, 0.0])      # World space position
        self.velocity = np.array([0.0, 0.0, 0.0])      # World space velocity
        self.bounding_radius = 20.0 # Approx. radius in meters for collision detection

        # Orientation represented by a quaternion (w, x, y, z)
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0]) # Identity quaternion
        self.angular_velocity = np.array([0.0, 0.0, 0.0]) # Body space angular velocity (rad/s)

        # Thruster Properties from the prompt
        self.main_thruster_min_force = 1000.0 # N
        self.main_thruster_max_force = 3000.0 # N
        self.steering_thruster_force = 200.0  # N

    def get_forward_vector(self):
        """Returns the current forward-facing vector in world space."""
        return qv_rotate(self.orientation, np.array([0.0, 0.0, 1.0]))

    def get_up_vector(self):
        """Returns the current up-facing vector in world space."""
        return qv_rotate(self.orientation, np.array([0.0, 1.0, 0.0]))

    def get_right_vector(self):
        """Returns the current right-facing vector in world space."""
        return qv_rotate(self.orientation, np.array([1.0, 0.0, 0.0]))

    def update(self, dt, thrust_input, pitch_input, yaw_input, roll_input):
        """
        Updates the ship's state over a time step dt based on control inputs.
        - thrust_input: float between 0.0 and 1.0
        - pitch_input, yaw_input, roll_input: float between -1.0 and 1.0
        """
        # --- Calculate Forces and Torques ---

        # 1. Main Thruster Force (acts along the ship's forward vector)
        thrust_magnitude = self.main_thruster_min_force + \
                           (self.main_thruster_max_force - self.main_thruster_min_force) * thrust_input
        force = self.get_forward_vector() * thrust_magnitude if thrust_input > 0 else np.array([0.0, 0.0, 0.0])

        # 2. Steering Thrusters Torque (acts in the ship's body frame)
        # Torque = Force * Moment Arm
        torque = np.array([
            pitch_input * self.steering_thruster_force * self.moment_arm_pitch,
            yaw_input * self.steering_thruster_force * self.moment_arm_yaw,
            roll_input * self.steering_thruster_force * self.moment_arm_roll
        ])

        # --- Update Linear Motion (World Frame) ---
        linear_acceleration = force / self.mass
        self.velocity += linear_acceleration * dt
        self.position += self.velocity * dt

        # --- Update Rotational Motion (Body Frame) ---
        # Using Euler's equation of motion for rigid bodies.
        # We ignore the gyroscopic precession term for simplicity, which is a common simplification in games.
        # alpha = I_inv * (torque)
        angular_acceleration = self.inverse_inertia_tensor @ torque
        self.angular_velocity += angular_acceleration * dt

        # Update orientation quaternion from angular velocity
        # dq/dt = 0.5 * q * w  (where w is a pure quaternion (0, omega_vector))
        w_quat = np.concatenate(([0.0], self.angular_velocity))
        q_derivative = 0.5 * q_multiply(self.orientation, w_quat)

        self.orientation += q_derivative * dt

        # Normalize the quaternion to prevent floating point drift, ensuring it remains a unit quaternion.
        norm = np.linalg.norm(self.orientation)
        if norm > 0:
            self.orientation /= norm

        # --- Flight Assist: Angular Damping ---
        # If there is no rotational input from the player, gradually slow down the ship's spin.
        # This makes the controls less frustrating and more "fly-by-wire".
        has_rot_input = (pitch_input != 0 or yaw_input != 0 or roll_input != 0)
        if not has_rot_input:
            damping_factor = 1.5 # How quickly to stop rotation
            self.angular_velocity *= (1.0 - damping_factor * dt)
