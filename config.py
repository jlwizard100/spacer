# -- config.py --
# This file contains all the core parameters for the spaceship simulator
# for easy tuning and adjustment.

# --- Ship Properties ---
SHIP_MASS = 20000.0  # kg

# --- Thruster Properties ---
# Main thruster provides forward force
MAIN_THRUSTER_MIN_FORCE = 0.0  # Newtons
MAIN_THRUSTER_MAX_FORCE = 10000.0 # Newtons

# Steering thrusters provide rotational force (torque)
STEERING_THRUSTER_FORCE = 500.0  # Newtons

# --- Joystick Axis Configuration ---
# Note: Axis mappings can vary between controllers.
# These are common defaults (e.g., for an Xbox controller).
JOYSTICK_AXIS_YAW   = 0  # Left Stick X
JOYSTICK_AXIS_PITCH = 1  # Left Stick Y (will be inverted in code)
JOYSTICK_AXIS_ROLL  = 2  # Right Stick X (as per last user request)
JOYSTICK_AXIS_THRUST = 4 # Right Trigger (as per last user request)
