"""
A simple 3D car simulation using Pyglet.

This script demonstrates:
- A movable first-person camera (representing the driver's view).
- A 3D environment with a ground plane and simple objects (cubes).
- A real-time rear-view mirror effect, rendered at the top of the screen.
- Use of Framebuffer Objects (FBOs) for rendering to a texture.

Controls:
- W: Move forward
- S: Move backward
- A: Turn left
- D: Turn right
"""
import math
import pyglet
from pyglet.gl import *
from pyglet.window import key

# --- Constants ---
PLAYER_SPEED = 5.0
PLAYER_ROTATION_SPEED = 90.0

# --- Helper Functions and Classes ---

class Player:
    """Represents the player's position, rotation, and movement logic."""
    def __init__(self, position=(0, 0, 0), rotation=(0, 0)):
        """
        Initializes the player.
        :param position: A 3-tuple (x, y, z) for the starting position.
        :param rotation: A 2-tuple (pitch, yaw) for the starting rotation.
        """
        self.position = list(position)
        self.rotation = list(rotation)

    def update(self, dt, keys):
        """
        Updates the player's position and rotation based on key presses.
        :param dt: The time delta since the last frame.
        :param keys: A KeyStateHandler object.
        """
        dx = dt * PLAYER_SPEED * math.sin(math.radians(self.rotation[1]))
        dz = dt * PLAYER_SPEED * math.cos(math.radians(self.rotation[1]))

        if keys[key.W]:
            self.position[0] -= dx
            self.position[2] += dz
        if keys[key.S]:
            self.position[0] += dx
            self.position[2] -= dz
        if keys[key.A]:
            self.rotation[1] -= dt * PLAYER_ROTATION_SPEED
        if keys[key.D]:
            self.rotation[1] += dt * PLAYER_ROTATION_SPEED

def draw_cube(position, size, color):
    """
    Draws a single, multi-colored cube.
    :param position: The (x, y, z) center of the cube.
    :param size: The side length of the cube.
    :param color: The base (r, g, b) color tuple for the cube.
    """
    x, y, z = position
    s = size / 2
    vertices = [
        x-s, y-s, z+s, x+s, y-s, z+s, x+s, y+s, z+s, x-s, y+s, z+s,  # Front
        x-s, y-s, z-s, x-s, y+s, z-s, x+s, y+s, z-s, x+s, y-s, z-s,  # Back
        x-s, y+s, z+s, x+s, y+s, z+s, x+s, y+s, z-s, x-s, y+s, z-s,  # Top
        x-s, y-s, z+s, x-s, y-s, z-s, x+s, y-s, z-s, x+s, y-s, z+s,  # Bottom
        x-s, y-s, z-s, x-s, y-s, z+s, x-s, y+s, z+s, x-s, y+s, z-s,  # Left
        x+s, y-s, z-s, x+s, y+s, z-s, x+s, y+s, z+s, x+s, y-s, z+s,  # Right
    ]
    colors = [
        *color, *color, *color, *color,
        *[c*0.8 for c in color], *[c*0.8 for c in color], *[c*0.8 for c in color], *[c*0.8 for c in color],
        *[c*0.9 for c in color], *[c*0.9 for c in color], *[c*0.9 for c in color], *[c*0.9 for c in color],
        *[c*0.7 for c in color], *[c*0.7 for c in color], *[c*0.7 for c in color], *[c*0.7 for c in color],
        *[c*0.85 for c in color], *[c*0.85 for c in color], *[c*0.85 for c in color], *[c*0.85 for c in color],
        *[c*0.95 for c in color], *[c*0.95 for c in color], *[c*0.95 for c in color], *[c*0.95 for c in color],
    ]
    pyglet.graphics.draw(24, GL_QUADS, ('v3f', vertices), ('c3f', colors))

class Framebuffer:
    """A class to encapsulate an OpenGL Framebuffer Object."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.texture = pyglet.image.Texture.create(width, height, GL_RGBA)
        fbo_id = GLuint()
        glGenFramebuffers(1, byref(fbo_id))
        self.id = fbo_id.value
        glBindFramebuffer(GL_FRAMEBUFFER, self.id)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.texture.target, self.texture.id, 0)

        depth_buffer = GLuint()
        glGenRenderbuffers(1, byref(depth_buffer))
        glBindRenderbuffer(GL_RENDERBUFFER, depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buffer)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer is not complete")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind(self):
        """Bind the FBO as the current rendering target."""
        glBindFramebuffer(GL_FRAMEBUFFER, self.id)

    def unbind(self):
        """Unbind the FBO, returning rendering to the default window."""
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

class CarWindow(pyglet.window.Window):
    """The main application window for the 3D simulation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 200)

        # --- OpenGL Setup ---
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # --- Player and Controls ---
        self.player = Player(position=(0, 1.0, 5))
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # --- World Objects ---
        self.objects = [
            {'pos': (0, 0.5, -10), 'size': 1, 'color': (1, 0, 0)},
            {'pos': (5, 0.5, -20), 'size': 1, 'color': (0, 0, 1)},
            {'pos': (-5, 0.5, -15), 'size': 1, 'color': (0, 1, 1)},
            {'pos': (3, 0.5, 15), 'size': 1, 'color': (1, 1, 0)},
            {'pos': (-4, 0.5, 25), 'size': 1, 'color': (1, 0, 1)},
        ]

        # --- Rear-View Mirror Setup ---
        self.mirror_width = self.width
        self.mirror_height = self.height // 5
        self.fbo = Framebuffer(self.mirror_width, self.mirror_height)

        # --- Scheduling ---
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def update(self, dt):
        """The main update loop, called every frame."""
        self.player.update(dt, self.keys)

    def draw_scene(self):
        """Draws all elements of the 3D scene."""
        self.draw_ground()
        self.draw_objects()

    def draw_ground(self):
        """Draws a green ground plane."""
        pyglet.graphics.draw(4, GL_QUADS,
            ('v3f', [-100, 0, -100, 100, 0, -100, 100, 0, 100, -100, 0, 100]),
            ('c3f', [0.1, 0.6, 0.1] * 4)
        )

    def draw_objects(self):
        """Draws all the objects in the world."""
        for obj in self.objects:
            draw_cube(obj['pos'], obj['size'], obj['color'])

    def set_3d_projection(self, width, height):
        """Sets up a 3D perspective projection."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height) if height > 0 else 1.0, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def on_draw(self):
        """The main drawing event, called every frame."""
        # --- Pass 1: Render rear-view scene to Framebuffer ---
        self.fbo.bind()
        glViewport(0, 0, self.mirror_width, self.mirror_height)
        self.set_3d_projection(self.mirror_width, self.mirror_height)
        glLoadIdentity()
        # Apply rear-facing camera transformation
        glRotatef(self.player.rotation[0], 1, 0, 0)
        glRotatef(self.player.rotation[1] + 180, 0, 1, 0)
        glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_scene()
        self.fbo.unbind()

        # --- Pass 2: Render main scene to the window ---
        glViewport(0, 0, self.width, self.height)
        self.set_3d_projection(self.width, self.height)
        glLoadIdentity()
        # Apply forward-facing camera transformation
        glRotatef(self.player.rotation[0], 1, 0, 0)
        glRotatef(self.player.rotation[1], 0, 1, 0)
        glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_scene()

        # --- Pass 3: Draw the rear-view mirror as a 2D HUD ---
        self.draw_rear_view_hud()

    def draw_rear_view_hud(self):
        """Draws the rear-view mirror texture as a 2D overlay."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3f(1, 1, 1)
        glEnable(self.fbo.texture.target)
        glBindTexture(self.fbo.texture.target, self.fbo.texture.id)

        mirror_y = self.height - self.mirror_height
        pyglet.graphics.draw(4, GL_QUADS,
            ('v2f', [0, mirror_y, self.width, mirror_y, self.width, self.height, 0, self.height]),
            ('t2f', [0, 0, 1, 0, 1, 1, 0, 1]) # Use flipped texture coordinates if needed
        )
        glDisable(self.fbo.texture.target)

    def on_resize(self, width, height):
        """Handles window resize events."""
        glViewport(0, 0, width, height)
        # Note: FBO and mirror size are fixed, but could be updated here if desired.
        return pyglet.event.EVENT_HANDLED

if __name__ == '__main__':
    window = CarWindow(width=1280, height=720, caption='3D Car Simulation', resizable=True)
    pyglet.app.run()
