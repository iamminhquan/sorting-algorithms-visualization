"""Sorting algorithms implemented as stateful generators for visualization.

Each algorithm yields :class:`SortState` instances that describe the current
snapshot of the array, which indices should be highlighted, and a textual
description to display on screen. This design keeps the visualization logic
decoupled from the algorithm implementations, making it easy to add new
algorithms in the future.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Iterator, List, Sequence, Set, Tuple


class HighlightType(Enum):
    """Enumeration of supported highlight styles."""

    DEFAULT = "default"
    COMPARE = "compare"
    SWAP = "swap"
    PIVOT = "pivot"
    SORTED = "sorted"


@dataclass(frozen=True)
class SortState:
    """Immutable snapshot of a sorting algorithm state.

    Attributes:
        array: The full array at the current step.
        highlights: Mapping of indices to highlight styles.
        sorted_indices: Indices that are known to be in their final position.
        description: Optional textual description of the action taken.
    """

    array: Tuple[int, ...]
    highlights: Dict[int, HighlightType] = field(default_factory=dict)
    sorted_indices: Tuple[int, ...] = field(default_factory=tuple)
    description: str = ""


def _state(
    array: Sequence[int],
    highlights: Iterable[Tuple[int, HighlightType]] | None = None,
    sorted_indices: Iterable[int] | None = None,
    description: str | None = None,
) -> SortState:
    """Create a :class:`SortState` from the provided components."""

    highlight_dict: Dict[int, HighlightType] = {}
    if highlights:
        highlight_dict = {idx: hl for idx, hl in highlights}

    sorted_tuple: Tuple[int, ...] = tuple(sorted(set(sorted_indices or ())))
    return SortState(
        array=tuple(array),
        highlights=highlight_dict,
        sorted_indices=sorted_tuple,
        description=description or "",
    )


def bubble_sort(data: Sequence[int]) -> Iterator[SortState]:
    """Yield states produced by the bubble sort algorithm.

    Args:
        data: The initial array to sort.

    Yields:
        SortState instances representing each comparison, swap, and completion.
    """

    arr: List[int] = list(data)
    n: int = len(arr)
    sorted_indices: Set[int] = set()
    for i in range(n):
        for j in range(0, n - i - 1):
            yield _state(
                arr,
                highlights=((j, HighlightType.COMPARE), (j + 1, HighlightType.COMPARE)),
                sorted_indices=sorted_indices,
                description=f"Comparing indices {j} and {j + 1}",
            )
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield _state(
                    arr,
                    highlights=((j, HighlightType.SWAP), (j + 1, HighlightType.SWAP)),
                    sorted_indices=sorted_indices,
                    description=f"Swapped indices {j} and {j + 1}",
                )
        sorted_indices.add(n - i - 1)
        yield _state(
            arr,
            highlights=((n - i - 1, HighlightType.SORTED),),
            sorted_indices=sorted_indices,
            description=f"Position {n - i - 1} is sorted",
        )
    yield _state(arr, sorted_indices=range(n), description="Bubble sort complete")


def insertion_sort(data: Sequence[int]) -> Iterator[SortState]:
    """Yield states produced by the insertion sort algorithm.

    Args:
        data: The initial array to sort.

    Yields:
        SortState instances representing each comparison, shift, and insertion.
    """

    arr: List[int] = list(data)
    sorted_indices: Set[int] = set()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        yield _state(
            arr,
            highlights=((i, HighlightType.PIVOT),),
            sorted_indices=sorted_indices,
            description=f"Selecting key at index {i}",
        )
        while j >= 0 and arr[j] > key:
            yield _state(
                arr,
                highlights=((j, HighlightType.COMPARE), (j + 1, HighlightType.COMPARE)),
                sorted_indices=sorted_indices,
                description=f"Comparing key with index {j}",
            )
            arr[j + 1] = arr[j]
            yield _state(
                arr,
                highlights=((j, HighlightType.SWAP), (j + 1, HighlightType.SWAP)),
                sorted_indices=sorted_indices,
                description=f"Shifting value at index {j} to index {j + 1}",
            )
            j -= 1
        arr[j + 1] = key
        sorted_indices.update(range(i + 1))
        yield _state(
            arr,
            highlights=((j + 1, HighlightType.SWAP),),
            sorted_indices=sorted_indices,
            description=f"Inserted key at index {j + 1}",
        )
    yield _state(
        arr, sorted_indices=range(len(arr)), description="Insertion sort complete"
    )


def selection_sort(data: Sequence[int]) -> Iterator[SortState]:
    """Yield states produced by the selection sort algorithm.

    Args:
        data: The initial array to sort.

    Yields:
        SortState instances representing each selection, comparison, and swap.
    """

    arr: List[int] = list(data)
    sorted_indices: Set[int] = set()
    n: int = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield _state(
                arr,
                highlights=((min_idx, HighlightType.PIVOT), (j, HighlightType.COMPARE)),
                sorted_indices=sorted_indices,
                description=f"Finding minimum from index {i} onward",
            )
            if arr[j] < arr[min_idx]:
                min_idx = j
                yield _state(
                    arr,
                    highlights=((min_idx, HighlightType.PIVOT),),
                    sorted_indices=sorted_indices,
                    description=f"New minimum at index {min_idx}",
                )
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        sorted_indices.add(i)
        yield _state(
            arr,
            highlights=((i, HighlightType.SORTED), (min_idx, HighlightType.SWAP)),
            sorted_indices=sorted_indices,
            description=f"Swapped minimum into position {i}",
        )
    yield _state(arr, sorted_indices=range(n), description="Selection sort complete")


def _quick_sort(
    arr: List[int],
    low: int,
    high: int,
    sorted_indices: Set[int],
) -> Iterator[SortState]:
    if low >= high:
        if low == high:
            sorted_indices.add(low)
            yield _state(
                arr,
                highlights=((low, HighlightType.SORTED),),
                sorted_indices=sorted_indices,
                description=f"Index {low} is sorted",
            )
        return

    pivot = arr[high]
    i = low - 1
    yield _state(
        arr,
        highlights=((high, HighlightType.PIVOT),),
        sorted_indices=sorted_indices,
        description=f"Pivot chosen at index {high}",
    )
    for j in range(low, high):
        yield _state(
            arr,
            highlights=((j, HighlightType.COMPARE), (high, HighlightType.PIVOT)),
            sorted_indices=sorted_indices,
            description=f"Comparing index {j} with pivot",
        )
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            yield _state(
                arr,
                highlights=((i, HighlightType.SWAP), (j, HighlightType.SWAP)),
                sorted_indices=sorted_indices,
                description=f"Swapped indices {i} and {j}",
            )
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    pivot_idx = i + 1
    sorted_indices.add(pivot_idx)
    yield _state(
        arr,
        highlights=((pivot_idx, HighlightType.SORTED),),
        sorted_indices=sorted_indices,
        description=f"Pivot settled at index {pivot_idx}",
    )
    yield from _quick_sort(arr, low, pivot_idx - 1, sorted_indices)
    yield from _quick_sort(arr, pivot_idx + 1, high, sorted_indices)


def quick_sort(data: Sequence[int]) -> Iterator[SortState]:
    """Yield states produced by the quick sort algorithm."""

    arr: List[int] = list(data)
    sorted_indices: Set[int] = set()
    yield from _quick_sort(arr, 0, len(arr) - 1, sorted_indices)
    yield _state(arr, sorted_indices=range(len(arr)), description="Quick sort complete")


def _merge(
    arr: List[int],
    start: int,
    mid: int,
    end: int,
    sorted_indices: Set[int],
) -> Iterator[SortState]:
    left = arr[start : mid + 1]
    right = arr[mid + 1 : end + 1]
    i = j = 0
    k = start

    while i < len(left) and j < len(right):
        yield _state(
            arr,
            highlights=(
                (k, HighlightType.COMPARE),
                (start + i, HighlightType.COMPARE),
                (mid + 1 + j, HighlightType.COMPARE),
            ),
            sorted_indices=sorted_indices,
            description=f"Merging indices {start} to {end}",
        )
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        yield _state(
            arr,
            highlights=((k, HighlightType.SWAP),),
            sorted_indices=sorted_indices,
            description=f"Placed value at index {k}",
        )
        k += 1

    while i < len(left):
        arr[k] = left[i]
        yield _state(
            arr,
            highlights=((k, HighlightType.SWAP),),
            sorted_indices=sorted_indices,
            description=f"Copying remaining left element to index {k}",
        )
        i += 1
        k += 1

    while j < len(right):
        arr[k] = right[j]
        yield _state(
            arr,
            highlights=((k, HighlightType.SWAP),),
            sorted_indices=sorted_indices,
            description=f"Copying remaining right element to index {k}",
        )
        j += 1
        k += 1

    sorted_indices.update(range(start, end + 1))
    yield _state(
        arr,
        highlights=tuple((idx, HighlightType.SORTED) for idx in range(start, end + 1)),
        sorted_indices=sorted_indices,
        description=f"Segment {start}:{end} sorted",
    )


def _merge_sort(
    arr: List[int],
    start: int,
    end: int,
    sorted_indices: Set[int],
) -> Iterator[SortState]:
    if start >= end:
        sorted_indices.add(start)
        yield _state(
            arr,
            highlights=((start, HighlightType.SORTED),),
            sorted_indices=sorted_indices,
            description=f"Index {start} is trivially sorted",
        )
        return

    mid = (start + end) // 2
    yield from _merge_sort(arr, start, mid, sorted_indices)
    yield from _merge_sort(arr, mid + 1, end, sorted_indices)
    yield from _merge(arr, start, mid, end, sorted_indices)


def merge_sort(data: Sequence[int]) -> Iterator[SortState]:
    """Yield states produced by the merge sort algorithm."""

    arr: List[int] = list(data)
    sorted_indices: Set[int] = set()
    if arr:
        yield from _merge_sort(arr, 0, len(arr) - 1, sorted_indices)
    yield _state(arr, sorted_indices=range(len(arr)), description="Merge sort complete")
