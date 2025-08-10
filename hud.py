import pygame
import numpy as np

class HUD:
    """
    Manages the Heads-Up Display, which shows ship telemetry at the bottom of the screen.
    """
    def __init__(self, width, height):
        self.width = width
        # The prompt asks for a constant display panel at the bottom of the screen.
        self.hud_height = 120  # Height of the HUD panel in pixels
        self.surface = pygame.Surface((width, self.hud_height))

        try:
            self.font = pygame.font.Font(None, 24) # Use default pygame font
        except Exception:
            self.font = pygame.font.SysFont("monospace", 16) # Fallback font

        self.last_update_time = 0
        self.update_interval = 500  # milliseconds (0.5 seconds), as per the prompt

        # Cache the rendered text surfaces for performance. They only update every 0.5s.
        self.telemetry_surfaces = []

    def update(self, ship):
        """
        Updates the telemetry data, but only if the update interval has passed.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.update_interval:
            self.last_update_time = current_time

            # Fetch new data from the ship
            pos = ship.position
            # Convert speed from m/s to km/h
            vel_kmh = np.linalg.norm(ship.velocity) * 3.6
            fwd = ship.get_forward_vector()
            up = ship.get_up_vector()
            rot = ship.orientation

            # Format the data into strings
            telemetry_data = [
                f"Position      (X,Y,Z): {pos[0]:>8.1f}, {pos[1]:>8.1f}, {pos[2]:>8.1f}",
                f"Speed                : {vel_kmh:>8.1f} km/h",
                f"Direction Vec (X,Y,Z): {fwd[0]:>8.2f}, {fwd[1]:>8.2f}, {fwd[2]:>8.2f}",
                f"Up Vector     (X,Y,Z): {up[0]:>8.2f}, {up[1]:>8.2f}, {up[2]:>8.2f}",
                f"Rotation Quat (W,X,Y,Z): {rot[0]:>8.2f}, {rot[1]:>8.2f}, {rot[2]:>8.2f}, {rot[3]:>8.2f}"
            ]

            # Re-render the text surfaces and store them in the cache
            self.telemetry_surfaces = []
            for text in telemetry_data:
                surface = self.font.render(text, True, (0, 255, 100)) # Bright green text
                self.telemetry_surfaces.append(surface)

    def draw(self, screen):
        """
        Draws the HUD panel onto the main screen.
        """
        # Draw the background panel
        self.surface.fill((0, 15, 0, 180)) # Dark green, semi-transparent background
        pygame.draw.rect(self.surface, (0, 80, 0), self.surface.get_rect(), 2) # Border

        # Blit the cached text surfaces
        y_offset = 10
        for text_surface in self.telemetry_surfaces:
            self.surface.blit(text_surface, (10, y_offset))
            y_offset += self.font.get_height() + 2

        # Blit the entire HUD surface to the bottom of the main screen
        screen.blit(self.surface, (0, screen.get_height() - self.hud_height))
