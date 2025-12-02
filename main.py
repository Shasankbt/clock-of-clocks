import pygame
import time
import math
pygame.init()

from grid import Grid

def get_digits(time):
    hours = (int(time) // 3600) % 24
    minutes = (int(time) // 60) % 60
    seconds = int(time) % 60

    hour_digits = [hours // 10, hours % 10]
    minute_digits = [minutes // 10, minutes % 10]
    second_digits = [seconds // 10, seconds % 10]

    return hour_digits, minute_digits, second_digits

transition_duration_ms = 200

def smooth_transition(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


screen = pygame.display.set_mode((1200, 400))
clock = pygame.time.Clock()

grid_centers = [
    (150, 200),
    (320, 200),
    (510, 200),
    (680, 200),
    (870, 200),
    (1040, 200),
]

grids = [
    Grid(center=center, clock_radius=20, spin_clockwise=False)
    for center in grid_centers
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    now = time.time() + (5 * 3600) + (30 * 60)

    now /= 1.0
    
    start_time = now - transition_duration_ms/2000.0
    end_time = now + transition_duration_ms/2000.0
    transition_ratio = smooth_transition(math.modf(now + transition_duration_ms/2000)[0] * (1000.0 / transition_duration_ms))
    
    start_hour_digits, start_minute_digits, start_seconds_digits = get_digits(start_time)
    end_hour_digits, end_minute_digits, end_seconds_digits = get_digits(end_time)

    start_digits = start_hour_digits + start_minute_digits + start_seconds_digits
    end_digits = end_hour_digits + end_minute_digits + end_seconds_digits


    screen.fill((30, 30, 30))
    for grid, start_digit, end_digit in zip(grids, start_digits, end_digits):
        grid.draw(screen, transition_ratio, start_digit, end_digit)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()