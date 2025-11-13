# Sorting Algorithms Visualization

This project is a Pygame application that brings popular sorting algorithms to life. Every step of an algorithm is rendered as a set of colored bars, making it easy to watch comparisons, swaps, and sorted sections in real time.

## Features

- Five algorithms included: Bubble, Insertion, Selection, Quick, and Merge sort.
- Distinct colors for comparisons, swaps, pivot selection, and sorted positions.
- Keyboard controls to switch algorithms, pause the animation, reshuffle the data, and adjust speed.
- Gentle finishing glow when the array becomes fully sorted.
- Optional click sound for swap steps (toggle by changing `ENABLE_AUDIO` in `settings.py`).
- Modular code layout designed for easy addition of new algorithms or visual effects.

## Installation

1. (Recommended) create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS / Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the app

```bash
python main.py
```

When the Pygame window appears, use the shortcuts below:

| Key | Action |
| --- | --- |
| `1` → `5` | Choose Bubble, Insertion, Selection, Quick, or Merge sort |
| `R` | Shuffle the array and restart the current algorithm |
| `+` / `=` | Speed up (shorter delay between steps) |
| `-` | Slow down |
| `Space` | Pause / resume the animation |
| `Esc` | Exit the application |

## Project structure

- `main.py`: Sets up Pygame, handles the main loop, and routes user input.
- `sorting_algorithms.py`: Generator-based sorting implementations that yield `SortState` snapshots.
- `visualizer.py`: Draws bars, renders HUD information, plays audio, and animates finishing effects.
- `settings.py`: Central place for screen dimensions, colors, array size, and timing.
- `requirements.txt`: Python dependencies.

## Adding a new algorithm

1. Implement a new generator in `sorting_algorithms.py`. It should accept an iterable of numbers and yield `SortState` objects.
2. Register a key binding for the new algorithm in `_build_algorithm_map()` inside `main.py`.
3. (Optional) Update `settings.py` if you need bespoke colors or parameters.

## Notes

- The app uses the bundled Pygame font `freesansbold.ttf`.
- If the audio mixer fails to initialize (e.g., on systems without audio support), the visualization still runs without sound.

