import pygame
import time
import math

from grid import Grid
from clock import Clock

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
w, h = screen.get_size()

TRANSITION_DURATION_MS = 250
GMT_OFFSET = [5, 30]  # hours, minutes

CLOCK_RADIUS = min(w, h) / 50
GRID_SEPERATION1 = CLOCK_RADIUS
GRID_SEPERATION2 = CLOCK_RADIUS * 2

print("Clock radius:", CLOCK_RADIUS)

class Clock_of_Clocks:
    def __init__(self):
        self.update_needed = True

        grid_centers = [
            (w/2 - 3 * GRID_SEPERATION1/2 - GRID_SEPERATION2 - 20 * CLOCK_RADIUS, h/2),
            (w/2 - GRID_SEPERATION1/2 - GRID_SEPERATION2 - 12 * CLOCK_RADIUS, h/2),
            (w/2 - GRID_SEPERATION1/2 - 4 * CLOCK_RADIUS, h/2),
            (w/2 + GRID_SEPERATION1/2 + 4 * CLOCK_RADIUS, h/2),
            (w/2 + GRID_SEPERATION1/2 + GRID_SEPERATION2 + 12 * CLOCK_RADIUS, h/2),
            (w/2 + 3 * GRID_SEPERATION1/2 + GRID_SEPERATION2 + 20 * CLOCK_RADIUS, h/2),
        ]

        self.grids = [
            Grid(center=center, clock_radius=CLOCK_RADIUS, spin_clockwise=True)
            for center in grid_centers
        ]

        seperator_centers = [
            (w/2 - GRID_SEPERATION1/2 - GRID_SEPERATION2/2 - 8 * CLOCK_RADIUS, h/2 - CLOCK_RADIUS/2),
            (w/2 - GRID_SEPERATION1/2 - GRID_SEPERATION2/2 - 8 * CLOCK_RADIUS, h/2 + CLOCK_RADIUS/2),
            (w/2 + GRID_SEPERATION1/2 + GRID_SEPERATION2/2 + 8 * CLOCK_RADIUS, h/2 - CLOCK_RADIUS/2),
            (w/2 + GRID_SEPERATION1/2 + GRID_SEPERATION2/2 + 8 * CLOCK_RADIUS, h/2 + CLOCK_RADIUS/2),
        ]

        self.seperators = [
            Clock(
                center=center,
                radius=CLOCK_RADIUS/2,
                circle_color=(100, 100, 100),
                circle_thickness=max(1, CLOCK_RADIUS // 50),
                hand_length=CLOCK_RADIUS/2 - 2,
                hand_thickness=max(1, CLOCK_RADIUS // 50),
                hand_color=(150, 150, 150),
                spin_clockwise=True,
            )
            for center in seperator_centers
        ]

    def _get_digits(self, time):
        hours = (int(time) // 3600) % 24
        minutes = (int(time) // 60) % 60
        seconds = int(time) % 60

        hour_digits = [hours // 10, hours % 10]
        minute_digits = [minutes // 10, minutes % 10]
        second_digits = [seconds // 10, seconds % 10]

        return hour_digits, minute_digits, second_digits

    def _smooth_transition(self, t):
        t = max(0.0, min(1.0, t))
        return t * t * (3 - 2 * t)

    def update_screen(self):
        now = time.time() + (5 * 3600) + (30 * 60)
        
        start_time = now - TRANSITION_DURATION_MS/2000.0
        end_time = now + TRANSITION_DURATION_MS/2000.0

        if int(start_time) != int(end_time):
            self.update_needed = True
        elif self.update_needed:
            self.update_needed = False
        else:
            time.sleep(1 - math.modf(end_time)[0])
            return
        
        transition_ratio = self._smooth_transition(math.modf(now + TRANSITION_DURATION_MS/2000)[0] * (1000.0 / TRANSITION_DURATION_MS))
        
        start_hour_digits, start_minute_digits, start_seconds_digits = self._get_digits(start_time)
        end_hour_digits, end_minute_digits, end_seconds_digits = self._get_digits(end_time)

        start_digits = start_hour_digits + start_minute_digits + start_seconds_digits
        end_digits = end_hour_digits + end_minute_digits + end_seconds_digits


        screen.fill((30, 30, 30))
        for grid, start_digit, end_digit in zip(self.grids, start_digits, end_digits):
            grid.draw(screen, transition_ratio, start_digit, end_digit)

        f = lambda x: "/" if x % 2 == 0 else "\\"

        sec_sep_start = f(start_seconds_digits[1])
        sec_sep_end = f(end_seconds_digits[1])
        min_sep_start = f(start_minute_digits[1])
        min_sep_end = f(end_minute_digits[1])
        
        self.seperators[0].draw(screen, transition_ratio, min_sep_start, min_sep_end)
        self.seperators[1].draw(screen, transition_ratio, min_sep_start, min_sep_end)
        self.seperators[2].draw(screen, transition_ratio, sec_sep_start, sec_sep_end)
        self.seperators[3].draw(screen, transition_ratio, sec_sep_start, sec_sep_end)



clock = pygame.time.Clock()
main_clock = Clock_of_Clocks()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    main_clock.update_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()