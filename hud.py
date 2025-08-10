import pygame
import numpy as np
import math

def quaternion_to_euler(q):
    """Converts a quaternion (w, x, y, z) to Euler angles (roll, pitch, yaw) in degrees."""
    w, x, y, z = q

    # Roll (x-axis rotation)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    # Pitch (y-axis rotation)
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    # Yaw (z-axis rotation)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return np.degrees(roll_x), np.degrees(pitch_y), np.degrees(yaw_z)


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

            # Convert orientation to Euler angles in degrees
            roll, pitch, yaw = quaternion_to_euler(ship.orientation)

            # Format the data into strings
            telemetry_data = [
                f"Speed           : {vel_kmh:>8.1f} km/h   |   Thrust: {thrust_n:>8.0f} N",
                f"Position (X,Y,Z): {pos[0]:>8.1f}, {pos[1]:>8.1f}, {pos[2]:>8.1f}",
                f"Direction   (Vec): <{ship.get_forward_vector()[0]:.2f}, {ship.get_forward_vector()[1]:.2f}, {ship.get_forward_vector()[2]:.2f}>",
                f"Orientation (R,P,Y): {roll:>8.1f}°, {pitch:>8.1f}°, {yaw:>8.1f}°"
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
