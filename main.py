import pygame
import numpy as np
import config
from spaceship import Spaceship, qv_rotate
from renderer import Camera, draw_ship, draw_asteroid, draw_gate
from game_objects import create_asteroid_field, create_gate_course
from hud import HUD

# --- Game Setup ---
WIDTH, HEIGHT = 1280, 800
FONT_BIG = None
FONT_SMALL = None

def reset_game():
    """Resets the game to its initial state."""
    ship = Spaceship()
    gates = create_gate_course()
    asteroids = create_asteroid_field(200, 5000)

    game_state = {
        "ship": ship,
        "gates": gates,
        "asteroids": asteroids,
        "camera": Camera(WIDTH, HEIGHT),
        "hud": HUD(WIDTH, HEIGHT),
        "status": "playing",  # "playing", "game_over", "course_complete"
        "active_gate_index": 0,
        "last_dist_to_gate": None
    }
    return game_state

def main():
    """Main game function."""
    global FONT_BIG, FONT_SMALL
    pygame.init()
    pygame.joystick.init() # Initialize the joystick module
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Spaceship Simulator")
    clock = pygame.time.Clock()
    FONT_BIG = pygame.font.Font(None, 72)
    FONT_SMALL = pygame.font.Font(None, 36)

    # --- Joystick Setup ---
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"INFO: Joystick detected: {joystick.get_name()}")
    else:
        print("INFO: No joystick detected. Using keyboard controls.")

    gs = reset_game()

    # Control state
    thrust_input = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and gs["status"] != "playing":
                    gs = reset_game()
                    thrust_input = 0.0 # Also reset input state

        # --- Input Handling ---
        # Get keyboard state
        keys = pygame.key.get_pressed()
        k_pitch = 1.0 if keys[pygame.K_DOWN] else -1.0 if keys[pygame.K_UP] else 0.0
        k_yaw = -1.0 if keys[pygame.K_LEFT] else 1.0 if keys[pygame.K_RIGHT] else 0.0
        k_roll = -1.0 if keys[pygame.K_a] else 1.0 if keys[pygame.K_d] else 0.0

        # Get joystick state
        j_pitch, j_yaw, j_roll, j_thrust_active = 0.0, 0.0, 0.0, False
        if joystick:
            def deadzone(val, dz=0.15): return val if abs(val) > dz else 0.0

            # Axis mappings from config file
            if joystick.get_numaxes() > config.JOYSTICK_AXIS_YAW:
                j_yaw = deadzone(joystick.get_axis(config.JOYSTICK_AXIS_YAW))
            if joystick.get_numaxes() > config.JOYSTICK_AXIS_PITCH:
                j_pitch = -deadzone(joystick.get_axis(config.JOYSTICK_AXIS_PITCH)) # Inverted
            if joystick.get_numaxes() > config.JOYSTICK_AXIS_ROLL:
                j_roll = deadzone(joystick.get_axis(config.JOYSTICK_AXIS_ROLL))

            # Thrust from a trigger axis
            if joystick.get_numaxes() > config.JOYSTICK_AXIS_THRUST:
                trigger_val = joystick.get_axis(config.JOYSTICK_AXIS_THRUST)
                if trigger_val > -0.99: # If trigger is being used
                    thrust_input = (trigger_val + 1.0) / 2.0
                    j_thrust_active = True

        # Combine keyboard and joystick inputs
        pitch_input = np.clip(k_pitch + j_pitch, -1.0, 1.0)
        yaw_input = np.clip(k_yaw + j_yaw, -1.0, 1.0)
        roll_input = np.clip(k_roll + j_roll, -1.0, 1.0)

        # Handle thrust (joystick overrides keyboard's gradual control)
        if not j_thrust_active:
            k_thrust_change = 1.0 if keys[pygame.K_w] else -1.0 if keys[pygame.K_s] else 0.0
            thrust_input = np.clip(thrust_input + k_thrust_change * dt * 0.5, 0.0, 1.0)

        # Zero out all inputs if game is not in "playing" state
        if gs["status"] != "playing":
            thrust_input, pitch_input, yaw_input, roll_input = 0,0,0,0

        # --- Updates (only if playing) ---
        if gs["status"] == "playing":
            gs["ship"].update(dt, thrust_input, pitch_input, yaw_input, roll_input)

            # --- Collision and Gate Logic ---
            # 1. Check for collision with asteroids
            for asteroid in gs["asteroids"]:
                dist = np.linalg.norm(gs["ship"].position - asteroid.position)
                if dist < gs["ship"].bounding_radius + asteroid.size:
                    gs["status"] = "game_over"
                    break

            # 2. Check for passing through the active gate
            if gs["status"] == "playing" and gs["active_gate_index"] < len(gs["gates"]):
                active_gate = gs["gates"][gs["active_gate_index"]]
                gate_normal = qv_rotate(active_gate.orientation, np.array([0,0,1]))
                gate_to_ship = gs["ship"].position - active_gate.position
                dist_from_plane = np.dot(gate_to_ship, gate_normal)

                # Check for crossing the plane
                if gs["last_dist_to_gate"] is not None and np.sign(dist_from_plane) != np.sign(gs["last_dist_to_gate"]):
                    # Check if within the gate's radius when crossing
                    dist_from_center = np.linalg.norm(gate_to_ship - dist_from_plane * gate_normal)
                    if dist_from_center < active_gate.size:
                        active_gate.is_passed = True
                        gs["active_gate_index"] += 1
                        gs["last_dist_to_gate"] = None # Reset for next gate
                        if gs["active_gate_index"] >= len(gs["gates"]):
                            gs["status"] = "course_complete"
                else:
                    gs["last_dist_to_gate"] = dist_from_plane

        # --- Drawing ---
        screen.fill((0, 0, 0))
        gs["camera"].update(gs["ship"])

        for a in gs["asteroids"]: draw_asteroid(screen, a, gs["camera"])
        for g in gs["gates"]: draw_gate(screen, g, gs["camera"])
        draw_ship(screen, gs["ship"], gs["camera"])

        gs["hud"].update(gs["ship"], thrust_input)
        gs["hud"].draw(screen)

        # --- Game State Overlay ---
        if gs["status"] != "playing":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))

            msg = "GAME OVER" if gs["status"] == "game_over" else "COURSE COMPLETE!"
            text_surf = FONT_BIG.render(msg, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
            overlay.blit(text_surf, text_rect)

            restart_surf = FONT_SMALL.render("Press 'R' to Restart", True, (255, 255, 255))
            restart_rect = restart_surf.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
            overlay.blit(restart_surf, restart_rect)

            screen.blit(overlay, (0,0))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
