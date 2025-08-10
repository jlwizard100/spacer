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
