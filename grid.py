from clock import Clock
import math

NUM_ROWS = 6
NUM_COLS = 4
DEFAULT_CLOCK_RADIUS = 20

class Grid:
    def __init__(self, center, clock_radius = DEFAULT_CLOCK_RADIUS):
        self.clocks = []

        for row in range(NUM_ROWS):
            row_clocks = []
            for col in range(NUM_COLS):
                clock_center = (
                    center[0] - (NUM_COLS / 2 - 0.5) * 2 * clock_radius + col * 2 * clock_radius,
                    center[1] - (NUM_ROWS / 2 - 0.5) * 2 * clock_radius + row * 2 * clock_radius,
                )
                row_clocks.append(
                    Clock(
                        center=clock_center,
                        radius=clock_radius,
                        circle_color=(100, 100, 100),
                        hand_length=clock_radius-1
                    )
                )
            self.clocks.append(row_clocks)

            self.num_state_dict = {
                0 : [
                    "┌", "-", "-", "┐",
                    "|", "┌", "┐", "|",
                    "|", "|", "|", "|",
                    "|", "|", "|", "|",
                    "|", "└", "┘", "|",
                    "└", "-", "-", "┘",
                ],
                1 : [
                    "┌", "-", "┐", "/",
                    "└", "┐", "|", "/",
                    "/", "|", "|", "/",
                    "/", "|", "|", "/",
                    "┌", "┘", "└", "┐",
                    "└", "-", "-", "┘",
                ],
                2: [
                    "┌", "-", "-", "┐",
                    "└", "-", "┐", "|",
                    "┌", "-", "┘", "|", 
                    "|", "┌", "-", "┘",
                    "|", "└", "-", "┐",
                    "└", "-", "-", "┘",
                ],
                3: [
                    "┌", "-", "-", "┐",
                    "└", "-", "┐", "|",
                    "/", "┌", "┘", "|",
                    "/", "└", "┐", "|",
                    "┌", "-", "┘", "|",
                    "└", "-", "-", "┘",
                ],
                4: [
                    "┌", "┐", "┌", "┐",
                    "|", "|", "|", "|",
                    "|", "└", "┘", "|",
                    "└", "-", "┐", "|",
                    "/", "/", "|", "|",
                    "/", "/", "└", "┘",
                ],
                5: [
                    "┌", "-", "-", "┐",
                    "|", "┌", "-", "┘",
                    "|", "└", "-", "┐",
                    "└", "-", "┐", "|",
                    "┌", "-", "┘", "|",
                    "└", "-", "-", "┘",
                ],
                6: [
                    "┌", "-", "-", "┐",
                    "|", "┌", "-", "┘",
                    "|", "└", "-", "┐",
                    "|", "┌", "┐", "|",
                    "|", "└", "┘", "|",
                    "└", "-", "-", "┘",
                ],
                7: [
                    "┌", "-", "-", "┐",
                    "└", "-", "┐", "|",
                    "/", "/", "|", "|",
                    "/", "/", "|", "|",
                    "/", "/", "|", "|",
                    "/", "/", "└", "┘",
                ],
                8: [
                    "┌", "-", "-", "┐",
                    "|", "┌", "┐", "|",
                    "|", "└", "┘", "|",
                    "|", "┌", "┐", "|",
                    "|", "└", "┘", "|",
                    "└", "-", "-", "┘",
                ],
                9 : [
                    "┌", "-", "-", "┐",
                    "|", "┌", "┐", "|",
                    "|", "└", "┘", "|",
                    "└", "-", "┐", "|",
                    "┌", "-", "┘", "|",
                    "└", "-", "-", "┘",
                ],

            }

    def draw(self, screen, transition_ratio, start_state, end_state):
        start_clocks_state = self.num_state_dict[start_state]
        end_clocks_state = self.num_state_dict[end_state]

        for i in range(NUM_ROWS):
            for j in range(NUM_COLS):
                self.clocks[i][j].draw(
                    screen,
                    transition_ratio,
                    start_clocks_state[i * NUM_COLS + j],
                    end_clocks_state[i * NUM_COLS + j],
                )
