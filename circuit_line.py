import math
from abc import ABC, abstractmethod

import pygame

Point = pygame.math.Vector2
Color = pygame.Color

SIGNAL_GRADIENT_STEPS = 24
ARC_BASE_SEGMENTS = 48


def _lerp_color(from_color: Color, to_color: Color, t: float):
    """Blend from_color -> to_color; t 0.0 -> from_color, 1.0 -> to_color."""
    t = max(0.0, min(1.0, t))
    return tuple(int(from_color[i] + (to_color[i] - from_color[i]) * t) for i in range(3))


def _thick_segment(p1: Point, p2: Point, width: float):
    """Rectangle (4 corners) of `width` centered on the p1->p2 segment."""
    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    perp_x = -math.sin(angle) * width / 2
    perp_y = math.cos(angle) * width / 2
    return [
        (p1[0] + perp_x, p1[1] + perp_y),
        (p1[0] - perp_x, p1[1] - perp_y),
        (p2[0] - perp_x, p2[1] - perp_y),
        (p2[0] + perp_x, p2[1] + perp_y),
    ]


class CircuitPath(ABC):
    """Pure geometry of a circuit segment; effects (visitors) do all the drawing."""

    def __init__(
        self,
        start_point: Point,
        end_point: Point,
        width: float,
        def_color: Color,
        activated_color: Color,
    ):
        self.start_point = Point(start_point)
        self.end_point = Point(end_point)
        self.width = width
        self.def_color = def_color
        self.activated_color = activated_color

    @abstractmethod
    def get_path_length(self):
        pass

    @abstractmethod
    def point_at(self, ratio: float) -> Point:
        """Position at ratio in [0, 1] along the path."""
        pass

    @abstractmethod
    def accept(self, effect):
        pass


class LinePath(CircuitPath):
    def __init__(
        self,
        start_point: Point,
        end_point: Point,
        width: float,
        def_color: Color,
        activated_color: Color,
    ):
        super().__init__(start_point, end_point, width, def_color, activated_color)
        self.distance = self.start_point.distance_to(self.end_point)
        self.direction = self.end_point - self.start_point

    def get_path_length(self):
        return self.distance

    def point_at(self, ratio: float) -> Point:
        return self.start_point + self.direction * ratio

    def accept(self, effect):
        effect.visit_line(self)


class CircularPath(CircuitPath):
    def __init__(
        self,
        start_point: Point,
        end_point: Point,
        width: float,
        def_color: Color,
        activated_color: Color,
        arc_angle: float,
    ):
        super().__init__(start_point, end_point, width, def_color, activated_color)
        self.arc_angle = arc_angle

        chord = self.start_point.distance_to(self.end_point)
        # signed radius flips the center to the other side of the chord when arc_angle < 0
        signed_radius = chord / (2 * math.sin(arc_angle / 2))
        midpoint = (self.start_point + self.end_point) / 2
        chord_normal = Point(-(self.end_point - self.start_point).y, (self.end_point - self.start_point).x).normalize()

        self.center = midpoint + chord_normal * (signed_radius * math.cos(arc_angle / 2))
        self.radius = abs(signed_radius)
        self.start_angle = math.atan2(self.start_point.y - self.center.y, self.start_point.x - self.center.x)
        self.arc_length = self.radius * abs(arc_angle)

    def get_path_length(self):
        return self.arc_length

    def point_at(self, ratio: float) -> Point:
        angle = self.start_angle + self.arc_angle * ratio
        return Point(
            self.center.x + self.radius * math.cos(angle),
            self.center.y + self.radius * math.sin(angle),
        )

    def accept(self, effect):
        effect.visit_circular(self)


class SignalEffect(ABC):
    """Visitor over a chain of CircuitPaths; concrete effects define how each shape lights up."""

    def __init__(self, paths):
        self.paths = paths
        self.lengths = [p.get_path_length() for p in paths]
        self.total_length = sum(self.lengths)
        self.starts = [sum(self.lengths[:i]) for i in range(len(paths))]

    def update(self, dt):
        pass

    def render(self, screen):
        self._screen = screen
        for path, start, length in zip(self.paths, self.starts, self.lengths):
            self._path_start, self._path_length = start, length
            path.accept(self)

    def _draw_outline(self, path, base_segments, color):
        prev = path.point_at(0.0)
        for i in range(1, base_segments + 1):
            curr = path.point_at(i / base_segments)
            pygame.draw.polygon(self._screen, color, _thick_segment(prev, curr, path.width))
            prev = curr

    @abstractmethod
    def visit_line(self, line: LinePath):
        pass

    @abstractmethod
    def visit_circular(self, arc: CircularPath):
        pass


class TrailingSignal(SignalEffect):
    """A pulse head that travels the chain, trailing a gradient fading back to def_color."""

    def __init__(self, paths, trailing_length: float, speed: float):
        super().__init__(paths)
        self.trailing_length = trailing_length
        self.speed = speed
        self.head = 0.0

    def update(self, dt):
        self.head = (self.head + self.speed * dt) % self.total_length

    def visit_line(self, line: LinePath):
        self._draw_outline(line, 1, line.def_color)
        self._draw_trailing(line)

    def visit_circular(self, arc: CircularPath):
        self._draw_outline(arc, ARC_BASE_SEGMENTS, arc.def_color)
        self._draw_trailing(arc)

    def _draw_trailing(self, path):
        # primary pass, plus a wrap pass one lap ahead so the trail spans the loop seam
        self._draw_trailing_pass(path, (self.head - self._path_start) / self._path_length)
        self._draw_trailing_pass(path, (self.head + self.total_length - self._path_start) / self._path_length)

    def _draw_trailing_pass(self, path, progress_ratio):
        trailing_ratio = self.trailing_length / self._path_length
        if not (0 < progress_ratio < 1 + trailing_ratio):
            return

        head_ratio = min(progress_ratio, 1.0)
        tail_ratio = max(progress_ratio - trailing_ratio, 0.0)
        if head_ratio <= tail_ratio:
            return

        span = head_ratio - tail_ratio
        for i in range(SIGNAL_GRADIENT_STEPS):
            seg_head_ratio = tail_ratio + span * (i + 1) / SIGNAL_GRADIENT_STEPS
            seg_tail_ratio = tail_ratio + span * i / SIGNAL_GRADIENT_STEPS

            # intensity anchored to the conceptual head (progress_ratio), fading over the trail
            intensity = 1.0 - (progress_ratio - seg_head_ratio) / trailing_ratio

            coords = _thick_segment(path.point_at(seg_head_ratio), path.point_at(seg_tail_ratio), path.width)
            pygame.draw.polygon(self._screen, _lerp_color(path.def_color, path.activated_color, intensity), coords)


class Illuminate(SignalEffect):
    """The whole chain pulses brightness up and down together, no travelling position."""

    def __init__(self, paths, frequency: float = 0.6):
        super().__init__(paths)
        self.frequency = frequency
        self.t = 0.0
        self.brightness = 0.0

    def update(self, dt):
        self.t += dt
        self.brightness = 0.5 * (1 + math.sin(2 * math.pi * self.frequency * self.t))

    def visit_line(self, line: LinePath):
        self._draw_outline(line, 1, _lerp_color(line.def_color, line.activated_color, self.brightness))

    def visit_circular(self, arc: CircularPath):
        self._draw_outline(arc, ARC_BASE_SEGMENTS, _lerp_color(arc.def_color, arc.activated_color, self.brightness))


def demo():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("CircuitPath demo (TAB toggles effect)")
    clock = pygame.time.Clock()

    def_color = Color(40, 40, 60)
    activated_color = Color(0, 200, 255)
    width = 8

    # closed rounded-rectangle loop: straights joined by clockwise 90-degree arcs.
    # each segment starts where the previous ends, so tangents stay continuous.
    x0, y0, x1, y1, r = 120, 140, 680, 460, 90
    q = math.pi / 2
    paths = [
        LinePath((x0 + r, y0), (x1 - r, y0), width, def_color, activated_color),
        CircularPath((x1 - r, y0), (x1, y0 + r), width, def_color, activated_color, q),
        LinePath((x1, y0 + r), (x1, y1 - r), width, def_color, activated_color),
        CircularPath((x1, y1 - r), (x1 - r, y1), width, def_color, activated_color, q),
        LinePath((x1 - r, y1), (x0 + r, y1), width, def_color, activated_color),
        CircularPath((x0 + r, y1), (x0, y1 - r), width, def_color, activated_color, q),
        LinePath((x0, y1 - r), (x0, y0 + r), width, def_color, activated_color),
        CircularPath((x0, y0 + r), (x0 + r, y0), width, def_color, activated_color, q),
    ]

    effects = [Illuminate(paths), TrailingSignal(paths, trailing_length=180, speed=600)]
    active = 0
    fps = 240

    running = True
    while running:
        dt = clock.tick(fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_TAB, pygame.K_SPACE):
                    active = (active + 1) % len(effects)

        effects[active].update(dt)

        screen.fill((0, 0, 0))
        effects[active].render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    demo()
