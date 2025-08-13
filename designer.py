import pygame as pg
import moderngl as mgl
import sys
import numpy as np
from camera import Camera
from shaders import vertex_shader, fragment_shader
from model_loader import Cube

class App:
    def __init__(self, win_size=(1600, 900)):
        pg.init()
        self.win_size = win_size

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        self.screen = pg.display.set_mode(self.win_size, flags=pg.OPENGL | pg.DOUBLEBUF)

        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.clock = pg.time.Clock()
        self.dt = 0
        self.camera = Camera(self)

        # Compile shaders and create a program
        self.program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # Create a placeholder model
        self.model = Cube(self)

        # Create a model matrix for the object
        self.m_model = self.get_model_matrix()

    def get_model_matrix(self, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
        # For now, a simple identity matrix, placing the object at the origin
        return np.identity(4, dtype=np.float32)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                sys.exit()

    def update(self):
        self.camera.update()

    def render(self):
        self.ctx.clear(0.08, 0.16, 0.18)

        # Pass matrices to the shader
        self.program['m_proj'].write(self.camera.m_proj.tobytes())
        self.program['m_view'].write(self.camera.m_view.tobytes())
        self.program['m_model'].write(self.m_model.tobytes())

        # Render the model
        self.model.render()

        pg.display.flip()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.render()
            self.dt = self.clock.tick(60) / 1000.0

if __name__ == '__main__':
    app = App()
    app.run()
