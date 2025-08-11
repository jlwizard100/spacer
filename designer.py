import pygame
import sys
import json
import numpy as np
from renderer import Camera, draw_wireframe_object
from game_objects import Gate, Asteroid, ASTEROID_MODELS, load_course_from_file
from utils import q_from_axis_angle, q_multiply

# --- Constants ---
WIDTH, HEIGHT = 1600, 900
SIDEBAR_WIDTH = 300
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH

COLOR_BACKGROUND = (20, 20, 30); COLOR_SIDEBAR = (40, 40, 50)
COLOR_MAIN_VIEW = (10, 10, 15); COLOR_GRID = (50, 50, 60)
COLOR_GATE = (0, 255, 0); COLOR_ASTEROID = (160, 82, 45)
COLOR_SELECTED = (255, 255, 0); COLOR_TEXT = (220, 220, 220)

ASTEROID_MODEL_IDS = list(ASTEROID_MODELS.keys())

# --- Camera for the Designer ---
class DesignerCamera(Camera):
    def __init__(self, fov=75):
        super().__init__(MAIN_VIEW_WIDTH, HEIGHT, fov)
        self.position = np.array([0.0, 1000.0, -2000.0]); self.target = np.array([0.0, 0.0, 0.0])

def rotate_vector(vec, axis, angle):
    q = q_from_axis_angle(axis, angle)
    q_vec = np.concatenate(([0.0], vec))
    rotated_q = q_multiply(q, q_multiply(q_vec, np.array([q[0], -q[1], -q[2], -q[3]])))
    return rotated_q[1:]

def save_course_to_file(filepath, gates, asteroids):
    """Saves the current scene to a JSON file."""
    course_data = {
        "version": 1, "course_name": "Designer Course", "boundaries": {"width": 20000, "height": 20000, "depth": 20000},
        "race_gates": [
            {"gate_number": i + 1, "position": g.position.tolist(), "orientation": g.orientation.tolist(), "size": g.size}
            for i, g in enumerate(gates)
        ],
        "asteroids": [
            {"model_id": a.model_id, "position": a.position.tolist(), "orientation": a.orientation.tolist(), "size": a.size, "angular_velocity": a.angular_velocity.tolist()}
            for a in asteroids
        ]
    }
    with open(filepath, 'w') as f:
        json.dump(course_data, f, indent=2)
    print(f"INFO: Course saved to {filepath}")

def main():
    pygame.init(); pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spaceship Course Designer")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 24)

    camera = DesignerCamera()

    grid_size = 10000; grid_step = 500; grid_verts = []
    for i in range(-grid_size, grid_size + 1, grid_step):
        grid_verts.append(np.array([-grid_size, 0, i])); grid_verts.append(np.array([grid_size, 0, i]))
        grid_verts.append(np.array([i, 0, -grid_size])); grid_verts.append(np.array([i, 0, grid_size]))

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                # --- File I/O ---
                if event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    save_course_to_file(current_filename, scene_gates, scene_asteroids)
                    status_message, status_message_timer = f"Saved to {current_filename}", 3
                if event.key == pygame.K_l and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    try:
                        scene_gates, scene_asteroids = load_course_from_file(current_filename)
                        selected_object = None
                        status_message, status_message_timer = f"Loaded from {current_filename}", 3
                    except FileNotFoundError:
                        status_message, status_message_timer = f"File not found: {current_filename}", 3
                # --- Object Creation / Deletion ---
                if not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    if event.key == pygame.K_g:
                        new_gate = Gate(position=[0,0,0], orientation=[1,0,0,0], size=800); scene_gates.append(new_gate)
                        selected_object = ("gate", len(scene_gates) - 1)
                    if event.key == pygame.K_a:
                        new_asteroid = Asteroid(position=[0,0,0], size=200, orientation=[1,0,0,0], angular_velocity=[0,0,0], model_id="asteroid_jagged_1"); scene_asteroids.append(new_asteroid)
                        selected_object = ("asteroid", len(scene_asteroids) - 1)
                    if event.key == pygame.K_DELETE:
                        if selected_object:
                            obj_type, obj_idx = selected_object
                            if obj_type == "gate": scene_gates.pop(obj_idx)
                            elif obj_type == "asteroid": scene_asteroids.pop(obj_idx)
                            selected_object = None
                    if selected_object and selected_object[0] == "asteroid":
                        asteroid = scene_asteroids[selected_object[1]]
                        if event.key in (pygame.K_PLUS, pygame.K_EQUALS): asteroid.set_size(asteroid.size + 20)
                        if event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE): asteroid.set_size(max(10, asteroid.size - 20))
                        if pygame.K_1 <= event.key <= pygame.K_3:
                            asteroid.set_model(ASTEROID_MODEL_IDS[event.key - pygame.K_1])

            if mx < MAIN_VIEW_WIDTH:
                # Mouse event handling for camera...
                if event.type == pygame.MOUSEWHEEL:
                    direction = camera.target - camera.position
                    if np.linalg.norm(direction) > 0:
                        direction /= np.linalg.norm(direction)
                        new_dist = max(10, np.linalg.norm(camera.target - camera.position) - event.y * 50)
                        camera.position = camera.target - direction * new_dist
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        closest_obj = None; min_dist_sq = 20**2
                        for i, gate in enumerate(scene_gates):
                            p = camera.project_point(gate.position)
                            if p and (p[0]-mx)**2 + (p[1]-my)**2 < min_dist_sq: min_dist_sq=(p[0]-mx)**2 + (p[1]-my)**2; closest_obj=("gate", i)
                        for i, asteroid in enumerate(scene_asteroids):
                            p = camera.project_point(asteroid.position)
                            if p and (p[0]-mx)**2 + (p[1]-my)**2 < min_dist_sq: min_dist_sq=(p[0]-mx)**2 + (p[1]-my)**2; closest_obj=("asteroid", i)
                        selected_object = closest_obj
                    elif event.button == 3: orbiting = True
                    elif event.button == 2: panning = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3: orbiting = False
                    if event.button == 2: panning = False
                elif event.type == pygame.MOUSEMOTION:
                    dx, dy = event.rel
                    if orbiting:
                        cam_vec = camera.position - camera.target
                        yaw, pitch = -dx*0.005, -dy*0.005
                        cam_vec = rotate_vector(cam_vec, [0,1,0], yaw)
                        right = np.cross([0,1,0], cam_vec); right /= np.linalg.norm(right)
                        cam_vec = rotate_vector(cam_vec, right, pitch)
                        camera.position = camera.target + cam_vec
                    if panning:
                        right = np.cross([0,1,0], camera.position - camera.target); right /= np.linalg.norm(right)
                        up = np.cross(camera.position - camera.target, right); up /= np.linalg.norm(up)
                        camera.position += -right * dx * 2.0 + up * dy * 2.0
                        camera.target += -right * dx * 2.0 + up * dy * 2.0

        if selected_object:
            # Keyboard handling for object transforms...
            obj = scene_gates[selected_object[1]] if selected_object[0] == "gate" else scene_asteroids[selected_object[1]]
            move_speed, rot_speed = 500*dt, 2*dt
            if keys[pygame.K_RIGHT]: obj.position[0] += move_speed
            if keys[pygame.K_LEFT]: obj.position[0] -= move_speed
            if keys[pygame.K_UP] and not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]): obj.position[2] += move_speed
            if keys[pygame.K_DOWN] and not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]): obj.position[2] -= move_speed
            if keys[pygame.K_PAGEUP]: obj.position[1] += move_speed
            if keys[pygame.K_PAGEDOWN]: obj.position[1] -= move_speed
            if keys[pygame.K_e]: obj.orientation = q_multiply(q_from_axis_angle([0,1,0], -rot_speed), obj.orientation)
            if keys[pygame.K_q]: obj.orientation = q_multiply(q_from_axis_angle([0,1,0], rot_speed), obj.orientation)
            if keys[pygame.K_r]: obj.orientation = q_multiply(q_from_axis_angle([1,0,0], rot_speed), obj.orientation)
            if keys[pygame.K_f]: obj.orientation = q_multiply(q_from_axis_angle([1,0,0], -rot_speed), obj.orientation)
            if keys[pygame.K_t]: obj.orientation = q_multiply(q_from_axis_angle([0,0,1], rot_speed), obj.orientation)
            if keys[pygame.K_g] and not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]): obj.orientation = q_multiply(q_from_axis_angle([0,0,1], -rot_speed), obj.orientation)

        # --- Drawing ---
        screen.fill(COLOR_MAIN_VIEW, pygame.Rect(0, 0, MAIN_VIEW_WIDTH, HEIGHT))
        projected_grid = [camera.project_point(v) for v in grid_verts]
        for i in range(0, len(projected_grid), 2):
            p1, p2 = projected_grid[i], projected_grid[i+1]
            if p1 and p2 and pygame.Rect(0,0,MAIN_VIEW_WIDTH,HEIGHT).collidepoint(p1) and pygame.Rect(0,0,MAIN_VIEW_WIDTH,HEIGHT).collidepoint(p2):
                pygame.draw.line(screen, COLOR_GRID, p1, p2, 1)

        for i, gate in enumerate(scene_gates):
            is_selected = selected_object == ("gate", i)
            draw_wireframe_object(screen, camera, gate.position, gate.orientation, gate.vertices, gate.edges, COLOR_SELECTED if is_selected else COLOR_GATE)
            p = camera.project_point(gate.position)
            if p and p[0] < MAIN_VIEW_WIDTH: screen.blit(font.render(f"G{i+1}", True, COLOR_SELECTED if is_selected else COLOR_GATE), (p[0]+10, p[1]-10))

        for i, asteroid in enumerate(scene_asteroids):
            is_selected = selected_object == ("asteroid", i)
            draw_wireframe_object(screen, camera, asteroid.position, asteroid.orientation, asteroid.vertices, asteroid.edges, COLOR_SELECTED if is_selected else COLOR_ASTEROID)

        screen.fill(COLOR_SIDEBAR, pygame.Rect(MAIN_VIEW_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        if status_message_timer > 0:
            msg_surf = font.render(status_message, True, COLOR_TEXT)
            screen.blit(msg_surf, (MAIN_VIEW_WIDTH + 20, HEIGHT - 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
