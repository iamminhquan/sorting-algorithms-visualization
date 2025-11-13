"""Rendering helpers for the sorting visualizer."""

from __future__ import annotations

import math
from array import array
from dataclasses import dataclass
from typing import Optional, Sequence

import pygame

import settings
from sorting_algorithms import HighlightType, SortState


@dataclass
class VisualizerAssets:
    """Pygame assets needed for rendering and audio playback."""

    font: pygame.font.Font
    info_font: pygame.font.Font
    click_sound: Optional[pygame.mixer.Sound] = None


class ArrayVisualizer:
    """Helper class that draws the array and overlays."""

    def __init__(self, screen: pygame.Surface):
        """Initialize the visualizer."""

        self.screen = screen
        self.assets = self._load_assets()
        self._finish_start_ticks: Optional[int] = None

    def _load_assets(self) -> VisualizerAssets:
        """Load fonts and optional audio assets."""

        font = pygame.font.Font(settings.PRIMARY_FONT_NAME, settings.TITLE_FONT_SIZE)
        info_font = pygame.font.Font(
            settings.PRIMARY_FONT_NAME, settings.INFO_FONT_SIZE
        )
        click_sound: Optional[pygame.mixer.Sound] = None

        if settings.ENABLE_AUDIO and pygame.mixer.get_init():
            click_sound = self._create_click_sound()
            if click_sound:
                click_sound.set_volume(settings.SOUND_VOLUME)

        return VisualizerAssets(font=font, info_font=info_font, click_sound=click_sound)

    def _create_click_sound(
        self,
        frequency: int = 1000,
        duration_ms: int = 50,
        sample_rate: int = 44100,
    ) -> Optional[pygame.mixer.Sound]:
        """Generate a short percussive click sound."""

        try:
            sample_count = int(sample_rate * duration_ms / 1000)
            samples = array("h")
            for i in range(sample_count):
                envelope = math.exp(-3.0 * i / sample_count)
                value = int(
                    envelope
                    * 1600
                    * math.sin(2 * math.pi * frequency * i / sample_rate)
                )
                samples.append(value)
            sample_bytes = samples.tobytes()
            return pygame.mixer.Sound(buffer=sample_bytes)
        except pygame.error:
            return None

    def draw(
        self,
        state: SortState,
        algorithm_name: str,
        delay_ms: int,
        show_description: bool = True,
    ) -> None:
        """Render the array bars and informational overlays."""

        self.screen.fill(settings.BACKGROUND_COLOR)
        array_values: Sequence[int] = state.array
        bar_width = self._calculate_bar_width(len(array_values))
        max_value = max(array_values) if array_values else 1
        finish_effect = self._compute_finish_effect(state, len(array_values))

        for index, value in enumerate(array_values):
            normalized_height = value / max_value
            bar_height = int(normalized_height * (settings.SCREEN_HEIGHT - 120))
            x_pos = index * bar_width
            y_pos = settings.SCREEN_HEIGHT - bar_height - 60
            color = self._resolve_color(index, state, finish_effect)
            pygame.draw.rect(
                self.screen,
                color,
                pygame.Rect(x_pos, y_pos, bar_width - 1, bar_height),
            )

        self._draw_headers(algorithm_name, delay_ms, len(array_values))

        if show_description and state.description:
            self._draw_description(state.description)

        pygame.display.flip()

    def _calculate_bar_width(self, count: int) -> int:
        """Return the pixel width of each bar."""

        if count == 0:
            return settings.SCREEN_WIDTH
        return max(2, settings.SCREEN_WIDTH // count)

    def _resolve_color(
        self,
        index: int,
        state: SortState,
        finish_effect: Optional[pygame.Color],
    ) -> pygame.Color:
        """Choose the appropriate color for a bar."""

        if finish_effect is not None:
            return finish_effect

        highlight = state.highlights.get(index)
        if highlight == HighlightType.COMPARE:
            return pygame.Color(*settings.COMPARE_COLOR)
        if highlight == HighlightType.SWAP:
            return pygame.Color(*settings.SWAP_COLOR)
        if highlight == HighlightType.PIVOT:
            return pygame.Color(*settings.PIVOT_COLOR)

        if index in state.sorted_indices:
            return pygame.Color(*settings.SORTED_COLOR)

        return pygame.Color(*settings.BAR_COLOR)

    def _draw_headers(
        self, algorithm_name: str, delay_ms: int, array_length: int
    ) -> None:
        """Draw informational text at the top of the screen."""

        title_surface = self.assets.font.render(
            f"Algorithm: {algorithm_name}",
            True,
            settings.TEXT_COLOR,
        )
        self.screen.blit(title_surface, (20, 20))

        speed_surface = self.assets.info_font.render(
            f"Delay: {delay_ms} ms | Size: {array_length}",
            True,
            settings.TEXT_COLOR,
        )
        self.screen.blit(speed_surface, (20, 50))

        controls_lines = [
            "Controls: 1-Bubble 2-Insertion 3-Selection 4-Quick 5-Merge",
            "R-Restart  +/- Adjust Speed  SPACE Pause/Resume  ESC Quit",
        ]
        for idx, line in enumerate(controls_lines):
            control_surface = self.assets.info_font.render(
                line, True, settings.TEXT_COLOR
            )
            self.screen.blit(
                control_surface, (20, settings.SCREEN_HEIGHT - 50 + idx * 20)
            )

    def _draw_description(self, description: str) -> None:
        """Render the step description."""

        desc_surface = self.assets.info_font.render(
            description, True, settings.TEXT_COLOR
        )
        desc_rect = desc_surface.get_rect()
        desc_rect.topright = (settings.SCREEN_WIDTH - 20, 50)
        self.screen.blit(desc_surface, desc_rect)

    def _contains_swap(self, state: SortState) -> bool:
        """Return True if the current state contains a swap highlight."""

        return any(hl == HighlightType.SWAP for hl in state.highlights.values())

    def play_swap_sound(self, state: SortState) -> None:
        """Play the swap audio clip if the state represents a swap."""

        if self.assets.click_sound and self._contains_swap(state):
            self.assets.click_sound.play()

    def _compute_finish_effect(
        self,
        state: SortState,
        array_length: int,
    ) -> Optional[pygame.Color]:
        """Return a transient finish color if the array is sorted."""

        if array_length == 0:
            return None

        all_sorted = len(state.sorted_indices) == array_length
        current_ticks = pygame.time.get_ticks()

        if all_sorted:
            if self._finish_start_ticks is None:
                self._finish_start_ticks = current_ticks
            elapsed = current_ticks - self._finish_start_ticks
            if elapsed <= settings.FINISH_EFFECT_DURATION_MS:
                phase = elapsed / settings.FINISH_EFFECT_DURATION_MS * math.pi
                glow = 0.5 * (1 + math.sin(phase * 4))
                base = pygame.Color(*settings.SORTED_COLOR)
                boosted = pygame.Color(
                    min(255, int(base.r + glow * 40)),
                    min(255, int(base.g + glow * 40)),
                    min(255, int(base.b + glow * 40)),
                )
                return boosted
            return pygame.Color(*settings.SORTED_COLOR)

        self._finish_start_ticks = None
        return None
