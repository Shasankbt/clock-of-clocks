import pygame
import math

DEFAULT_RADIUS = 100
DEFAULT_THICKNESS = 2
DEFAULT_COLOR = (255, 255, 255)
DEFAULT_HAND_LENGTH = 90

class Clock:
    def __init__(
        self,
        center,
        radius=DEFAULT_RADIUS,
        circle_thickness=DEFAULT_THICKNESS,
        circle_color=DEFAULT_COLOR,
        hand_length = DEFAULT_HAND_LENGTH,
        hand_color=DEFAULT_COLOR,
        hand_thickness=DEFAULT_THICKNESS,
    ):
        self.radius = radius
        self.center = center

        self.circle_thickness = circle_thickness
        self.circle_color = circle_color

        self.hand_length = hand_length
        self.hand_color = hand_color
        self.hand_thickness = hand_thickness

        self.state_angle_mapping = {
            "|" :   [math.radians(0),   math.radians(180)],
            "-" :   [math.radians(90),  math.radians(270)],
            "┌" :  [math.radians(90),  math.radians(180)],
            "┐" :  [math.radians(180), math.radians(270)],
            "┘" :  [math.radians(270), math.radians(0)],
            "└" :  [math.radians(0),   math.radians(90)],
            "/" : [math.radians(45),  math.radians(45)],
        }

    def _draw_shapes(self, screen, hand_angles):
        def _get_rect_coords(angle, center, length, half_width):
            return [
                (center[0] + half_width * math.cos(angle), center[1] + half_width * math.sin(angle)),
                (center[0] - half_width * math.cos(angle), center[1] - half_width * math.sin(angle)),
                (center[0] + length * math.sin(angle) - half_width * math.cos(angle), center[1] - length * math.cos(angle) - half_width * math.sin(angle)),
                (center[0] + length * math.sin(angle) + half_width * math.cos(angle), center[1] - length * math.cos(angle) + half_width * math.sin(angle)),
            ]
        
        pygame.draw.circle(
            screen,
            self.circle_color,
            self.center,
            self.radius,
            self.circle_thickness,
        )

        for angle in hand_angles:
            pygame.draw.polygon(
                screen,
                self.hand_color,
                _get_rect_coords(angle, self.center, self.hand_length, self.hand_thickness / 2),
            )

    def draw(self, screen, transition_ratio, start_state, end_state):
        hand_angles = [
            self.state_angle_mapping[start_state],
            self.state_angle_mapping[end_state],
        ]
        transition_ratio = max(0.0, min(1.0, transition_ratio))

        intrapolated_angles = [prev_angle + (next_angle - prev_angle) * transition_ratio for prev_angle, next_angle in zip(hand_angles[0], hand_angles[1])]

        self._draw_shapes(screen, intrapolated_angles)

    


    
