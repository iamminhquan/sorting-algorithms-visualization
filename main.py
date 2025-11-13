"""Entry point for the Pygame-based sorting visualizer."""

from __future__ import annotations

import random
from typing import Callable, Dict, Iterable, Iterator, Tuple

import pygame

import settings
from sorting_algorithms import (
    SortState,
    bubble_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
from visualizer import ArrayVisualizer

AlgorithmFunction = Callable[[Iterable[int]], Iterator[SortState]]


def _build_algorithm_map() -> Dict[int, Tuple[str, AlgorithmFunction]]:
    """Return key bindings mapped to algorithm metadata."""

    return {
        pygame.K_1: ("Bubble Sort", bubble_sort),
        pygame.K_2: ("Insertion Sort", insertion_sort),
        pygame.K_3: ("Selection Sort", selection_sort),
        pygame.K_4: ("Quick Sort", quick_sort),
        pygame.K_5: ("Merge Sort", merge_sort),
    }


class SortApp:
    """Main controller for the sorting visualization application."""

    def __init__(self) -> None:
        """Initialize Pygame, the visualizer, and shared state."""

        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        self.screen = pygame.display.set_mode(settings.SCREEN_SIZE)
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.visualizer = ArrayVisualizer(self.screen)

        self.algorithms = _build_algorithm_map()
        self.active_key = pygame.K_1
        self.algorithm_name, self.algorithm_fn = self.algorithms[self.active_key]

        self.delay_ms = settings.INITIAL_DELAY_MS
        self.paused = False
        self.sort_complete = False
        self._last_step_tick = 0
        self._running = True

        self.data = self._generate_data()
        self.state_iter = iter(())
        self.current_state = SortState(array=tuple(self.data))
        self._start_algorithm()

    def run(self) -> None:
        """Run the main application loop."""

        while self._running:
            self._handle_events()
            self._update_state()
            self.visualizer.draw(self.current_state, self.algorithm_name, self.delay_ms)
            self.clock.tick(60)

        pygame.quit()

    def _handle_events(self) -> None:
        """Process user input events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        """Handle keyboard shortcuts."""

        if key == pygame.K_ESCAPE:
            self._running = False
        elif key == pygame.K_r:
            self._restart_with_shuffle()
        elif key in self.algorithms:
            self._switch_algorithm(key)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._adjust_delay(settings.DELAY_STEP_MS)
        elif key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self._adjust_delay(-settings.DELAY_STEP_MS)
        elif key == pygame.K_SPACE:
            self.paused = not self.paused

    def _update_state(self) -> None:
        """Advance the sorting generator when appropriate."""

        if self.paused or self.sort_complete:
            return

        now = pygame.time.get_ticks()
        if now - self._last_step_tick < self.delay_ms:
            return

        try:
            next_state = next(self.state_iter)
        except StopIteration:
            self.sort_complete = True
            return

        self.current_state = next_state
        self.visualizer.play_swap_sound(next_state)
        self._last_step_tick = now

    def _restart_with_shuffle(self) -> None:
        """Shuffle the array and restart the active algorithm."""

        self.data = self._generate_data()
        self._start_algorithm()

    def _switch_algorithm(self, key: int) -> None:
        """Switch to a new sorting algorithm while preserving the array."""

        self.active_key = key
        self.algorithm_name, self.algorithm_fn = self.algorithms[key]
        self._start_algorithm()

    def _start_algorithm(self) -> None:
        """Initialize the active sorting generator."""

        self.state_iter = iter(self.algorithm_fn(self.data))
        self.current_state = SortState(array=tuple(self.data))
        self.sort_complete = False
        self._last_step_tick = pygame.time.get_ticks()

    def _adjust_delay(self, delta: int) -> None:
        """Adjust the animation delay, clamped to configured bounds."""

        self.delay_ms = int(
            max(
                settings.MIN_DELAY_MS, min(settings.MAX_DELAY_MS, self.delay_ms + delta)
            )
        )

    def _generate_data(self) -> list[int]:
        """Return a randomized list of bar heights."""

        return [
            random.randint(settings.ARRAY_MIN_VALUE, settings.ARRAY_MAX_VALUE)
            for _ in range(settings.ARRAY_SIZE)
        ]


def main() -> None:
    """Create and run the sorting visualizer application."""

    app = SortApp()
    app.run()


if __name__ == "__main__":
    main()
