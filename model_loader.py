import numpy as np

class Cube:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.program

        # Define the vertices of a cube
        vertices = [
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)
        ]
        vertices = np.array(vertices, dtype='f4')

        # Define the indices for the faces of the cube
        indices = [
            (0, 2, 3), (0, 1, 2),
            (1, 7, 2), (1, 6, 7),
            (6, 5, 4), (4, 7, 6),
            (4, 5, 0), (5, 1, 0),
            (3, 2, 7), (3, 7, 4),
            (5, 6, 1), (5, 1, 0)
        ]
        indices = np.array(indices, dtype='i4').flatten()

        # Create Vertex Buffer Object (VBO) and Index Buffer Object (IBO)
        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)

        # Create Vertex Array Object (VAO)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f', 'in_position')],
            index_buffer=self.ibo,
            index_element_size=4  # 4 bytes for 'i4'
        )

    def render(self):
        self.vao.render()
