from .core import min_platforms


def test_min_platforms():
    intervals = [(900, 910), (940, 1200), (950, 1120), (1100, 1130), (1500, 1900), (1800, 2000)]
    assert min_platforms(intervals) == 3
