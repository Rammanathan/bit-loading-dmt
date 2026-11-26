import heapq
import numpy as np
from src.baseline import allocation_energy


def greedy_heap(g, energy_budget, gap=1.0, bmax=15):
    """
    This version selects the cheapest bit with a min-heap priority queue.
    Greedy bit-loading algorithm (baseline: linear scan for the cheapest bit).
    
        Inputs:
            g : array with shape (N,)
                Channel-to-noise ratios per unit energy for N tones; finite and > 0.
            energy_budget : float
                Maximum total transmission energy available; finite scalar >= 0.
            gap : float, default=1.0
                Gap factor in the energy model; finite scalar >= 1.
            bmax : int, default=15
                Maximum integer number of bits allowed per tone; >= 0.
    
        Returns:
            dict with
                "bits" : int array with shape (N,)
                    Integer bit allocation for each tone.
                "energy_used" : float
                    Total energy of the allocation, computed from the energy formula.
    
        Failure:
            Raises ValueError if inputs are invalid:
            - g not a non-empty 1-D array, or non-positive / non-finite gains
            - energy budget not a finite non-negative scalar
            - gap not a finite scalar >= 1
            - bmax not a non-negative integer
    """
    # --- validation: copy exactly from greedy_scan ---
    g = np.asarray(g, dtype=float)
    if g.ndim != 1 or len(g) == 0:
        raise ValueError("g must be a non-empty 1D array")
    if not np.all(np.isfinite(g)) or np.any(g <= 0):
        raise ValueError("All channel gains must be positive and finite")
    if np.ndim(energy_budget) != 0 or not np.isfinite(energy_budget) or energy_budget < 0:
        raise ValueError("energy_budget must be a finite, non-negative scalar")
    if np.ndim(gap) != 0 or not np.isfinite(gap) or gap < 1:
        raise ValueError("gap must be a finite scalar >= 1")
    if isinstance(bmax, bool) or not isinstance(bmax, (int, np.integer)) or bmax < 0:
        raise ValueError("bmax must be a non-negative integer")
    # ... the same five checks ...

    N = len(g)
    bits = np.zeros(N, dtype=int)
    cost = gap / g
    remaining = float(energy_budget)

    heap = [(float(cost[i]), i) for i in range(N)] if bmax > 0 else []

    heapq.heapify(heap)

    while heap:
        next_cost, i = heap[0]          # cheapest item, NOT removed yet

        if next_cost > remaining:
            break

        heapq.heappop(heap)             # now remove it
        remaining -= next_cost
        bits[i] += 1

        if bits[i] < bmax:
            heapq.heappush(heap, (next_cost * 2.0, i))

    return {
        "bits": bits,
        "energy_used": allocation_energy(bits, g, gap),
    }