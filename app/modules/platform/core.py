from typing import List, Tuple


def min_platforms(intervals: List[Tuple[int, int]]) -> int:
    """
    intervals: list of (arrival, departure) in minutes.
    Uses sweep-line / greedy to compute minimum platforms.
    """
    events = []
    for arr, dep in intervals:
        events.append((arr, 1))   # train arrives
        events.append((dep, -1))  # train departs

    events.sort()
    current = 0
    max_platforms = 0
    for _, delta in events:
        current += delta
        max_platforms = max(max_platforms, current)
    return max_platforms

"""notes for me: this sorting uses timsort which is mix of insertion and merge sort, and also is lexicographic, means if first values are equal go for the second parameters of it and so on.."""
