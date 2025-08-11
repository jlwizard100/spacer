import pygame
import sys
import json
import numpy as np
import random
from renderer import Camera, draw_wireframe_object
from game_objects import Gate, Asteroid, ASTEROID_MODELS, load_course_from_file
from utils import q_from_axis_angle, q_multiply, qv_rotate

# --- Constants ---
WIDTH, HEIGHT = 1600, 900
SIDEBAR_WIDTH = 300
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH

COLOR_BACKGROUND = (20, 20, 30); COLOR_SIDEBAR = (40, 40, 50)
COLOR_MAIN_VIEW = (10, 10, 15); COLOR_GRID = (50, 50, 60)
COLOR_BOUNDS = (40, 40, 40)
COLOR_GATE = (0, 255, 0); COLOR_ASTEROID = (160, 82, 45)
COLOR_SELECTED = (255, 255, 0); COLOR_TEXT = (220, 220, 220)

ASTEROID_MODEL_IDS = list(ASTEROID_MODELS.keys())

# --- Camera for the Designer ---
class DesignerCamera(Camera):
    def __init__(self, fov=75):
        super().__init__(MAIN_VIEW_WIDTH, HEIGHT, fov)
        self.position = np.array([0.0, 1000.0, -2000.0]); self.target = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

def save_course_to_file(filepath, gates, asteroids, bounds_size):
    course_data = {
        "version": 1, "course_name": "Designer Course",
        "boundaries": {"width": bounds_size, "height": bounds_size, "depth": bounds_size},
        "race_gates": [{"gate_number":i+1, "position":g.position.tolist(), "orientation":g.orientation.tolist(), "size":g.size} for i,g in enumerate(gates)],
        "asteroids": [{"model_id":a.model_id, "position":a.position.tolist(), "orientation":a.orientation.tolist(), "size":a.size, "angular_velocity":a.angular_velocity.tolist()} for a in asteroids]
    }
    with open(filepath, 'w') as f: json.dump(course_data, f, indent=2)
    print(f"INFO: Course saved to {filepath}")

def generate_random_asteroids(count, field_size):
    """Creates a list of randomly generated asteroids."""
    asteroids = []
    half_size = field_size / 2
    for _ in range(count):
        pos = np.random.uniform(-half_size, half_size, 3)
        size = np.random.uniform(100, 500)
        axis = np.random.rand(3) * 2 - 1; axis /= np.linalg.norm(axis)
        angle = np.random.rand() * 2 * np.pi
        orientation = q_from_axis_angle(axis, angle)
        model_id = random.choice(ASTEROID_MODEL_IDS)
        angular_velocity = np.random.rand(3) * 0.1
        asteroids.append(Asteroid(pos, size, orientation, angular_velocity, model_id))
    return asteroids

def draw_text(surface, text, pos, font, color=COLOR_TEXT):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def main():
    pygame.init(); pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spaceship Course Designer")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30); font_small = pygame.font.Font(None, 24); font_title = pygame.font.Font(None, 36)

    camera = DesignerCamera()

    boundary_size = 20000.0
    boundary_edges = [(0,1),(1,2),(2,3),(3,0), (4,5),(5,6),(6,7),(7,4), (0,4),(1,5),(2,6),(3,7)]

    scene_gates, scene_asteroids = [], []
    selected_object = None
    orbiting, panning = False, False
    current_filename = "course.json"
    status_message = ""; status_message_timer = 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if status_message_timer > 0: status_message_timer -= dt

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                # File I/O
                if event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    save_course_to_file(current_filename, scene_gates, scene_asteroids, boundary_size)
                    status_message, status_message_timer = f"Saved to {current_filename}", 3
                if event.key == pygame.K_l and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    try:
                        loaded_data = load_course_from_file(current_filename)
                        scene_gates, scene_asteroids = loaded_data['gates'], loaded_data['asteroids']
                        boundary_size = loaded_data.get('boundaries', {}).get('width', 20000.0)
                        selected_object = None; status_message, status_message_timer = f"Loaded from {current_filename}", 3
                    except (FileNotFoundError, json.JSONDecodeError) as e: status_message, status_message_timer = f"Error: {e}", 3

                # Object Creation / Deletion / Population
                if not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    if event.key == pygame.K_g:
                        new_gate = Gate(position=[0,0,0], orientation=[1,0,0,0], size=800); scene_gates.append(new_gate); selected_object = ("gate", len(scene_gates) - 1)
                    if event.key == pygame.K_a:
                        new_asteroid = Asteroid(position=[0,0,0], size=200, orientation=[1,0,0,0], angular_velocity=[0,0,0], model_id="asteroid_jagged_1"); scene_asteroids.append(new_asteroid); selected_object = ("asteroid", len(scene_asteroids) - 1)
                    if event.key == pygame.K_p:
                        new_asteroids = generate_random_asteroids(count=50, field_size=boundary_size); scene_asteroids.extend(new_asteroids)
                        status_message, status_message_timer = "Added 50 random asteroids", 3
                    if event.key == pygame.K_DELETE:
                        if selected_object:
                            obj_type, obj_idx = selected_object
                            if obj_type == "gate": scene_gates.pop(obj_idx)
                            elif obj_type == "asteroid": scene_asteroids.pop(obj_idx)
                            selected_object = None

                    # Selected Object Property Editing
                    if selected_object:
                        obj = scene_gates[selected_object[1]] if selected_object[0] == "gate" else scene_asteroids[selected_object[1]]
                        if selected_object[0] == "asteroid":
                            if event.key in (pygame.K_PLUS, pygame.K_EQUALS): obj.set_size(obj.size + 20)
                            if event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE): obj.set_size(max(10, obj.size - 20))
                            if pygame.K_1 <= event.key <= pygame.K_3: obj.set_model(ASTEROID_MODEL_IDS[event.key - pygame.K_1])
                        # Boundary size editing
                        if event.key == pygame.K_PAGEUP and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]): boundary_size += 1000
                        if event.key == pygame.K_PAGEDOWN and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]): boundary_size = max(1000, boundary_size - 1000)


        # --- Mouse & Camera Controls ---
        if mx < MAIN_VIEW_WIDTH:
            # (mouse handling code...)
            pass # Abridged for clarity

        # --- Object Transform Editing ---
        if selected_object:
            # (key press transform code...)
            pass # Abridged for clarity

        # --- Drawing ---
        screen.fill(COLOR_MAIN_VIEW, pygame.Rect(0, 0, MAIN_VIEW_WIDTH, HEIGHT))

        # Draw boundary box
        s = boundary_size / 2.0
        boundary_verts = np.array([[-s,-s,-s],[s,-s,-s],[s,s,-s],[-s,s,-s],[-s,-s,s],[s,-s,s],[s,s,s],[-s,s,s]])
        draw_wireframe_object(screen, camera, np.array([0,0,0]), np.array([1,0,0,0]), boundary_verts, boundary_edges, COLOR_BOUNDS)

        # (Rest of drawing code...)

        # --- Sidebar UI ---
        screen.fill(COLOR_SIDEBAR, pygame.Rect(MAIN_VIEW_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        sidebar_x = MAIN_VIEW_WIDTH + 20; y_pos = 20
        draw_text(screen, f"Boundary Size: {boundary_size:.0f}", (sidebar_x, y_pos), font); y_pos += 30
        if selected_object:
            # (selected object info drawing code...)
            pass # Abridged for clarity

        if status_message_timer > 0: draw_text(screen, status_message, (sidebar_x, HEIGHT - 50), font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
