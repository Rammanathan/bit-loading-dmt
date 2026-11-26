import time
import numpy as np


def allocation_energy(bits, g, gap=1.0):
    """Total energy needed for an allocation: sum of gap * (2**b - 1) / g."""
    bits = np.asarray(bits, dtype=float)
    g = np.asarray(g, dtype=float)
    return float(np.sum(gap * (2.0 ** bits - 1.0) / g))


def time_function(func, *args, repeats=5, **kwargs):
    """
    Time func(*args, **kwargs).

    Runs once as a warm-up (not timed), then `repeats` timed runs.
    Returns the median run time in seconds (robust to one slow run).
    """
    func(*args, **kwargs)
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        func(*args, **kwargs)
        times.append(time.perf_counter() - start)
    return float(np.median(times))