"""Application-wide constants for the sorting visualizer.

This module centralizes tweakable parameters such as screen dimensions,
colors, and animation pacing so that the application is easy to configure
and extend.
"""

from typing import Tuple

# Screen configuration.
SCREEN_WIDTH: int = 960
SCREEN_HEIGHT: int = 540
SCREEN_SIZE: Tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT)
WINDOW_TITLE: str = "Sorting Algorithms Visualizer"

# Data configuration.
ARRAY_SIZE: int = 100
ARRAY_MIN_VALUE: int = 10
ARRAY_MAX_VALUE: int = SCREEN_HEIGHT - 100

# Animation timing (in milliseconds). Lower is faster.
INITIAL_DELAY_MS: int = 40
MIN_DELAY_MS: int = 5
MAX_DELAY_MS: int = 200
DELAY_STEP_MS: int = 5

# Colors (RGB).
BACKGROUND_COLOR: Tuple[int, int, int] = (24, 24, 24)
BAR_COLOR: Tuple[int, int, int] = (100, 180, 255)
COMPARE_COLOR: Tuple[int, int, int] = (255, 99, 71)
SWAP_COLOR: Tuple[int, int, int] = (255, 215, 0)
SORTED_COLOR: Tuple[int, int, int] = (80, 220, 120)
TEXT_COLOR: Tuple[int, int, int] = (230, 230, 230)
PIVOT_COLOR: Tuple[int, int, int] = (186, 85, 211)

# Fonts.
PRIMARY_FONT_NAME: str = "freesansbold.ttf"
TITLE_FONT_SIZE: int = 24
INFO_FONT_SIZE: int = 18

# Audio configuration.
ENABLE_AUDIO: bool = True
SOUND_VOLUME: float = 0.4

# Visual effects.
FINISH_EFFECT_DURATION_MS: int = 1200
