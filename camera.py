import pygame as pg
import numpy as np
import math

class Camera:
    def __init__(self, app, position=(0, 5, -10), yaw=-90, pitch=0):
        self.app = app
        self.aspect_ratio = app.win_size[0] / app.win_size[1]
        self.position = np.array(position, dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.forward = np.array([0, 0, -1], dtype=np.float32)
        self.yaw = yaw
        self.pitch = pitch

        # View matrix
        self.m_view = self.get_view_matrix()
        # Projection matrix
        self.m_proj = self.get_projection_matrix()

        self.update_vectors()

    def get_projection_matrix(self, fov=50, near=0.1, far=10000):
        t = math.tan(math.radians(fov) / 2) * near
        b = -t
        r = t * self.aspect_ratio
        l = -r

        m00 = 2 * near / (r - l)
        m11 = 2 * near / (t - b)
        m22 = -(far + near) / (far - near)
        m23 = -2 * far * near / (far - near)

        return np.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, m22, -1],
            [0, 0, m23, 0]
        ], dtype=np.float32)

    def get_view_matrix(self):
        return np.look_at(self.position, self.position + self.forward, self.up)

    def update_vectors(self):
        self.forward[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.forward[1] = math.sin(math.radians(self.pitch))
        self.forward[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))

        self.forward = self.forward / np.linalg.norm(self.forward)
        self.right = np.cross(self.forward, np.array([0, 1, 0], dtype=np.float32))
        self.up = np.cross(self.right, self.forward)

    def update(self):
        self.move()
        self.rotate()
        self.m_view = self.get_view_matrix()

    def move(self):
        velocity = 10 * self.app.dt
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position += self.up * velocity
        if keys[pg.K_e]:
            self.position -= self.up * velocity

    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        if pg.mouse.get_pressed()[2]: # Right mouse button
            self.yaw += rel_x * 0.1
            self.pitch -= rel_y * 0.1
            self.pitch = max(-89, min(89, self.pitch))
            self.update_vectors()

# Monkey patch numpy to add a look_at function if it doesn't exist
# This is a common pattern for small projects to avoid a full dependency like pyrr
def look_at(eye, target, up):
    z_axis = eye - target
    z_axis /= np.linalg.norm(z_axis)
    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)
    y_axis = np.cross(z_axis, x_axis)

    view_matrix = np.array([
        [x_axis[0], y_axis[0], z_axis[0], 0],
        [x_axis[1], y_axis[1], z_axis[1], 0],
        [x_axis[2], y_axis[2], z_axis[2], 0],
        [-np.dot(x_axis, eye), -np.dot(y_axis, eye), -np.dot(z_axis, eye), 1]
    ], dtype=np.float32).T

    return view_matrix

np.look_at = look_at
