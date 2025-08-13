vertex_shader = """
#version 330 core

// Input vertex position
in vec3 in_position;

// Transformation matrices
uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    // Transform vertex position to clip space
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
"""

fragment_shader = """
#version 330 core

// Output color
out vec4 f_color;

void main() {
    // For now, output a solid white color
    f_color = vec4(1.0, 1.0, 1.0, 1.0);
}
"""
