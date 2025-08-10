import pygame
import numpy as np
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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Spaceship Simulator")
    clock = pygame.time.Clock()
    FONT_BIG = pygame.font.Font(None, 72)
    FONT_SMALL = pygame.font.Font(None, 36)

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
        keys = pygame.key.get_pressed()
        if gs["status"] == "playing":
            if keys[pygame.K_w]: thrust_input = min(1.0, thrust_input + dt * 0.5)
            elif keys[pygame.K_s]: thrust_input = max(0.0, thrust_input - dt * 0.5)
            pitch_input = 1.0 if keys[pygame.K_DOWN] else -1.0 if keys[pygame.K_UP] else 0.0
            yaw_input = -1.0 if keys[pygame.K_LEFT] else 1.0 if keys[pygame.K_RIGHT] else 0.0
            roll_input = -1.0 if keys[pygame.K_a] else 1.0 if keys[pygame.K_d] else 0.0
        else:
            # No input if game is over
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

        gs["hud"].update(gs["ship"])
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
