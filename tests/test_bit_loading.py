import numpy as np
import pytest
import itertools
from src.baseline import greedy_scan
from src.modified import greedy_heap


def test_hand_example():
    result = greedy_scan([4, 2, 1], 3)
    assert result["bits"].tolist() == [3, 1, 0]
    assert np.isclose(result["energy_used"], 2.25)


def test_heap_matches_scan_on_small_cases():
    for g, B in [([4, 2, 1], 3), ([1, 1], 3), ([1, 1, 1, 1], 10), ([2, 5], 0)]:
        assert np.array_equal(greedy_scan(g, B)["bits"], greedy_heap(g, B)["bits"])


def test_bmax_zero_gives_all_zeros():
    assert greedy_heap([5, 3], 10, bmax=0)["bits"].tolist() == [0, 0]

def test_zero_budget():
    assert greedy_scan([1, 2], 0)["bits"].tolist() == [0, 0]
    assert greedy_heap([1, 2], 0)["bits"].tolist() == [0, 0]

def test_g_is_not_changed():
    g = np.array([2.0, 1.0])
    original = g.copy()
    greedy_scan(g, 3)
    assert g.tolist() == original.tolist()
    greedy_heap(g, 3)
    assert g.tolist() == original.tolist()

def test_energy_within_budget():
    budget = 5.0
    g = [1.0, 2.0, 3.0]
    scan_result = greedy_scan(g, budget)
    heap_result = greedy_heap(g, budget)
    assert scan_result["energy_used"] <= budget + 1e-12
    assert heap_result["energy_used"] <= budget + 1e-12

def test_guide_example():
    result = greedy_scan([1, 1], 3)
    assert result["bits"].tolist() == [1, 1]
    assert np.isclose(result["energy_used"], 2.0)

def test_heap_matches_scan_on_random_cases():
    rng = np.random.default_rng(0)
    for _ in range(200):
        N = int(rng.integers(1, 10))
        if rng.random() < 0.5:
            g = rng.choice([0.5, 1.0, 2.0, 4.0], size=N)    # lots of exact ties
        else:
            g = rng.uniform(0.1, 5.0, size=N)
        budget = float(rng.uniform(0, 20))
        bmax = int(rng.integers(0, 6))
        scan_result = greedy_scan(g, budget, bmax=bmax)
        heap_result = greedy_heap(g, budget, bmax=bmax)
        assert np.array_equal(scan_result["bits"], heap_result["bits"])
        assert np.isclose(scan_result["energy_used"], heap_result["energy_used"])

def test_brute_force_optimality():
    g = np.array([1.0, 2.0, 3.0])
    bmax = 3
    gap = 1.0
    for budget in [0, 1, 2, 3, 5, 10, 15]:
        greedy_total = int(np.sum(greedy_scan(g, budget, gap=gap, bmax=bmax)["bits"]))
        heap_total = int(np.sum(greedy_heap(g, budget, gap=gap, bmax=bmax)["bits"]))

        feasible_totals = []
        for allocation in itertools.product(range(bmax + 1), repeat=3):
            allocation = np.array(allocation)
            energy = np.sum((gap / g) * (2.0 ** allocation - 1.0))
            if energy <= budget + 1e-12:
                feasible_totals.append(np.sum(allocation))
        best_total = max(feasible_totals)

        assert greedy_total == best_total
        assert heap_total == best_total

def test_invalid_inputs_raise_value_error():
    bad_cases = [
        dict(g=[], energy_budget=3),                # empty g
        dict(g=[[1, 2], [3, 4]], energy_budget=3),  # g not 1-D
        dict(g=[1, -1], energy_budget=3),           # negative gain
        dict(g=[1, 0], energy_budget=3),            # zero gain
        dict(g=[1, np.nan], energy_budget=3),       # non-finite gain
        dict(g=[1, 1], energy_budget=-1),           # negative budget
        dict(g=[1, 1], energy_budget=np.inf),       # infinite budget
        dict(g=[1, 1], energy_budget=[3, 4]),       # budget not a scalar
        dict(g=[1, 1], energy_budget=3, gap=0.5),   # gap below 1
        dict(g=[1, 1], energy_budget=3, bmax=-1),   # negative cap
        dict(g=[1, 1], energy_budget=3, bmax=2.5),  # non-integer cap
    ]
    for method in (greedy_scan, greedy_heap):
        for kwargs in bad_cases:
            with pytest.raises(ValueError):
                method(**kwargs)