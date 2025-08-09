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
from ctypes import byref
from pyglet.window import key

# --- Constants ---
PLAYER_SPEED = 5.0
PLAYER_ROTATION_SPEED = 90.0

# --- Helper Functions and Classes ---

class Player:
    """Represents the player's position, rotation, and movement logic."""
    def __init__(self, position=(0, 0, 0), rotation=(0, 0)):
        self.position = list(position)
        self.rotation = list(rotation)

    def update(self, dt, keys):
        dx = dt * PLAYER_SPEED * math.sin(math.radians(self.rotation[1]))
        dz = dt * PLAYER_SPEED * math.cos(math.radians(self.rotation[1]))
        if keys[key.W]:
            self.position[0] -= dx
            self.position[2] -= dz
        if keys[key.S]:
            self.position[0] += dx
            self.position[2] += dz
        if keys[key.A]:
            self.rotation[1] -= dt * PLAYER_ROTATION_SPEED
        if keys[key.D]:
            self.rotation[1] += dt * PLAYER_ROTATION_SPEED

def draw_cube(position, size, color):
    x, y, z = position
    s = size / 2
    vertices = [
        x-s, y-s, z+s, x+s, y-s, z+s, x+s, y+s, z+s, x-s, y+s, z+s,
        x-s, y-s, z-s, x-s, y+s, z-s, x+s, y+s, z-s, x+s, y-s, z-s,
        x-s, y+s, z+s, x+s, y+s, z+s, x+s, y+s, z-s, x-s, y+s, z-s,
        x-s, y-s, z+s, x-s, y-s, z-s, x+s, y-s, z-s, x+s, y-s, z+s,
        x-s, y-s, z-s, x-s, y-s, z+s, x-s, y+s, z+s, x-s, y+s, z-s,
        x+s, y-s, z-s, x+s, y+s, z-s, x+s, y+s, z+s, x+s, y-s, z+s,
    ]
    colors = [
        *color, *color, *color, *color,
        *[c*0.8 for c in color], *[c*0.8 for c in color], *[c*0.8 for c in color], *[c*0.8 for c in color],
        *[c*0.9 for c in color], *[c*0.9 for c in color], *[c*0.9 for c in color], *[c*0.9 for c in color],
        *[c*0.7 for c in color], *[c*0.7 for c in color], *[c*0.7 for c in color], *[c*0.7 for c in color],
        *[c*0.85 for c in color], *[c*0.85 for c in color], *[c*0.85 for c in color], *[c*0.85 for c in color],
        *[c*0.95 for c in color], *[c*0.95 for c in color], *[c*0.95 for c in color], *[c*0.95 for c in color],
    ]
    pyglet.graphics.draw(24, pyglet.gl.GL_QUADS, ('v3f', vertices), ('c3f', colors))

class Framebuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.texture = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA)
        fbo_id = pyglet.gl.GLuint()
        pyglet.gl.glGenFramebuffers(1, byref(fbo_id))
        self.id = fbo_id.value
        pyglet.gl.glBindFramebuffer(pyglet.gl.GL_FRAMEBUFFER, self.id)
        pyglet.gl.glFramebufferTexture2D(pyglet.gl.GL_FRAMEBUFFER, pyglet.gl.GL_COLOR_ATTACHMENT0, self.texture.target, self.texture.id, 0)

        depth_buffer = pyglet.gl.GLuint()
        pyglet.gl.glGenRenderbuffers(1, byref(depth_buffer))
        pyglet.gl.glBindRenderbuffer(pyglet.gl.GL_RENDERBUFFER, depth_buffer)
        pyglet.gl.glRenderbufferStorage(pyglet.gl.GL_RENDERBUFFER, pyglet.gl.GL_DEPTH_COMPONENT, width, height)
        pyglet.gl.glFramebufferRenderbuffer(pyglet.gl.GL_FRAMEBUFFER, pyglet.gl.GL_DEPTH_ATTACHMENT, pyglet.gl.GL_RENDERBUFFER, depth_buffer)

        if pyglet.gl.glCheckFramebufferStatus(pyglet.gl.GL_FRAMEBUFFER) != pyglet.gl.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer is not complete")
        pyglet.gl.glBindFramebuffer(pyglet.gl.GL_FRAMEBUFFER, 0)

    def bind(self):
        pyglet.gl.glBindFramebuffer(pyglet.gl.GL_FRAMEBUFFER, self.id)

    def unbind(self):
        pyglet.gl.glBindFramebuffer(pyglet.gl.GL_FRAMEBUFFER, 0)

class CarWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 200)

        pyglet.gl.glClearColor(0.5, 0.7, 1.0, 1.0)
        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)

        self.player = Player(position=(0, 1.0, 5))
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.objects = [
            {'pos': (0, 0.5, -10), 'size': 1, 'color': (1, 0, 0)},
            {'pos': (5, 0.5, -20), 'size': 1, 'color': (0, 0, 1)},
            {'pos': (-5, 0.5, -15), 'size': 1, 'color': (0, 1, 1)},
            {'pos': (3, 0.5, 15), 'size': 1, 'color': (1, 1, 0)},
            {'pos': (-4, 0.5, 25), 'size': 1, 'color': (1, 0, 1)},
        ]

        self.mirror_width = self.width
        self.mirror_height = self.height // 5
        self.fbo = Framebuffer(self.mirror_width, self.mirror_height)

        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def update(self, dt):
        self.player.update(dt, self.keys)

    def draw_scene(self):
        self.draw_ground()
        self.draw_objects()

    def draw_ground(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v3f', [-100, 0, -100, 100, 0, -100, 100, 0, 100, -100, 0, 100]),
            ('c3f', [0.1, 0.6, 0.1] * 4)
        )

    def draw_objects(self):
        for obj in self.objects:
            draw_cube(obj['pos'], obj['size'], obj['color'])

    def set_3d_projection(self, width, height):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.gluPerspective(65.0, width / float(height) if height > 0 else 1.0, 0.1, 1000.0)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)

    def on_draw(self):
        pyglet.gl.glViewport(0, 0, self.width, self.height)

        # Pass 1: Render rear-view scene to Framebuffer
        self.fbo.bind()
        pyglet.gl.glViewport(0, 0, self.mirror_width, self.mirror_height)
        self.set_3d_projection(self.mirror_width, self.mirror_height)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glRotatef(self.player.rotation[0], 1, 0, 0)
        pyglet.gl.glRotatef(self.player.rotation[1] + 180, 0, 1, 0)
        pyglet.gl.glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)
        self.draw_scene()
        self.fbo.unbind()

        # Pass 2: Render main scene to the window
        pyglet.gl.glViewport(0, 0, self.width, self.height)
        self.set_3d_projection(self.width, self.height)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glRotatef(self.player.rotation[0], 1, 0, 0)
        pyglet.gl.glRotatef(self.player.rotation[1], 0, 1, 0)
        pyglet.gl.glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)
        self.draw_scene()

        # Pass 3: Draw the rear-view mirror as a 2D HUD
        self.draw_rear_view_hud()

    def draw_rear_view_hud(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, self.width, 0, self.height, -1, 1)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()

        pyglet.gl.glColor3f(1, 1, 1)
        pyglet.gl.glEnable(self.fbo.texture.target)
        pyglet.gl.glBindTexture(self.fbo.texture.target, self.fbo.texture.id)

        mirror_y = self.height - self.mirror_height
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2f', [0, mirror_y, self.width, mirror_y, self.width, self.height, 0, self.height]),
            ('t2f', [0, 0, 1, 0, 1, 1, 0, 1])
        )
        pyglet.gl.glDisable(self.fbo.texture.target)

    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        return pyglet.event.EVENT_HANDLED

if __name__ == '__main__':
    window = CarWindow(width=1280, height=720, caption='3D Car Simulation', resizable=True)
    pyglet.app.run()
