import pygame
import numpy as np
import math

class HUD:
    """
    Manages the Heads-Up Display, which shows ship telemetry at the bottom of the screen.
    """
    def __init__(self, width, height):
        self.width = width
        self.hud_height = 120
        self.surface = pygame.Surface((width, self.hud_height))

        try:
            self.font = pygame.font.Font(None, 24)
        except Exception:
            self.font = pygame.font.SysFont("monospace", 16)

        self.last_update_time = 0
        self.update_interval = 500
        self.telemetry_surfaces = []

    def update(self, ship, thrust_input):
        """
        Updates the telemetry data, but only if the update interval has passed.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.update_interval:
            self.last_update_time = current_time

            # --- Fetch and calculate new data ---
            pos = ship.position
            vel_kmh = np.linalg.norm(ship.velocity) * 3.6

            # Calculate current thrust in Newtons
            thrust_n = ship.main_thruster_min_force + \
                       (ship.main_thruster_max_force - ship.main_thruster_min_force) * thrust_input

            # Format the data into strings
            fwd, up, right = ship.get_forward_vector(), ship.get_up_vector(), ship.get_right_vector()
            telemetry_data = [
                f"Speed        : {vel_kmh:>8.1f} km/h   |   Thrust: {thrust_n:>8.0f} N",
                f"Position(XYZ): {pos[0]:>8.1f}, {pos[1]:>8.1f}, {pos[2]:>8.1f}",
                f"Forward (Vec): <{fwd[0]:>6.2f}, {fwd[1]:>6.2f}, {fwd[2]:>6.2f}>",
                f"Up      (Vec): <{up[0]:>6.2f}, {up[1]:>6.2f}, {up[2]:>6.2f}>",
                f"Right   (Vec): <{right[0]:>6.2f}, {right[1]:>6.2f}, {right[2]:>6.2f}>"
            ]

            # Re-render the text surfaces and store them in the cache
            self.telemetry_surfaces = []
            for text in telemetry_data:
                surface = self.font.render(text, True, (0, 255, 100))
                self.telemetry_surfaces.append(surface)

    def draw(self, screen):
        """
        Draws the HUD panel onto the main screen.
        """
        self.surface.fill((0, 15, 0, 180))
        pygame.draw.rect(self.surface, (0, 80, 0), self.surface.get_rect(), 2)

        y_offset = 10
        for text_surface in self.telemetry_surfaces:
            self.surface.blit(text_surface, (10, y_offset))
            y_offset += self.font.get_height() + 4

        screen.blit(self.surface, (0, screen.get_height() - self.hud_height))
