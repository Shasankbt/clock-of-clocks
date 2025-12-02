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
        spin_clockwise=False,
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
            "┘" :  [math.radians(270), math.radians(360)],
            "└" :  [math.radians(0),   math.radians(90)],
            "/" : [math.radians(45),  math.radians(45)],
        } # make sure that angles are in accending order for proper interpolation
        self.spin_clockwise = spin_clockwise

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

    def _intrapolate_closest_angle(self, start_angle, end_angle, transition_ratio):
        intrapolated_angles = []
        for prev_angle, next_angle in zip(start_angle, end_angle):
            prev_angle %= 2 * math.pi
            next_angle %= 2 * math.pi
            intrapolated_angles.append(prev_angle + (next_angle - prev_angle) * transition_ratio)
        
        return intrapolated_angles
    
    def _intrapolate_clockwise_angle(self, start_angle, end_angle, transition_ratio):
        end_angles = [angle + 2 * math.pi if angle < start_angle[i] else angle for i, angle in enumerate(end_angle)]
        end_angles.sort()

        intrapolated_angles = [
            start_angle + (end_angle - start_angle) * transition_ratio
            for start_angle, end_angle in zip(start_angle, end_angles)
        ]

        return intrapolated_angles

    def draw(self, screen, transition_ratio, start_state, end_state):
        hand_angles = [
            self.state_angle_mapping[start_state],
            self.state_angle_mapping[end_state],
        ]

        intrapolation_fn = self._intrapolate_clockwise_angle if self.spin_clockwise else self._intrapolate_closest_angle

        intrapolated_angles = intrapolation_fn(
            hand_angles[0],
            hand_angles[1],
            transition_ratio,
        )
        self._draw_shapes(screen, intrapolated_angles)

    


    
