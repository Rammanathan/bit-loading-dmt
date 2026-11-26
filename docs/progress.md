# Project Progress

## Plan

- **Track:** D – Data Transmission: Discrete Bit Loading (Campello, 1999).
- **Baseline:** greedy marginal-energy allocation. At each step, scan all tones, pick the one whose next bit costs the least energy, and buy it if the remaining budget allows.
- **Planned change:** replace the linear scan with a priority queue (min-heap, Python `heapq`) storing `(cost, tone index)` pairs.
- **Hypothesis:** selecting the cheapest bit drops from O(N) to O(log N), so total work drops from O(B·N) to O(N + B·log N). The heap should be faster for large N with an identical allocation. For small N it may be slower, because `np.argmin` runs in compiled code while `heapq` runs Python steps.
- **Same result expected:** ties go to the lowest index in both methods (`argmin` returns the first minimum; tuples compare the index next), and doubling a float is exact, so equal costs stay equal.

## Log

### 21 Nov 2026
- Created the repository and folder structure.
- Implemented `greedy_scan` in `src/baseline.py` with input validation and a dict return (`bits`, `energy_used`).
- Checked by hand: g = [4, 2, 1], budget 3 gives [3, 1, 0], energy 2.25.
- **Found an issue in the guide:** its sanity check says g = [1, 1], Γ = 1, E_max = 3 gives [2, 1]. That allocation needs energy (2²−1) + (2¹−1) = 4, which exceeds the budget. Our code gives [1, 1] (energy 2). Brute-force enumeration over all allocations confirms [1, 1] is optimal for budget 3.
- Energy is computed from the formula Σ Γ(2^b − 1)/g rather than by subtracting from the budget, to avoid accumulated rounding error.

### 24 Nov 2026
- Created a virtual environment (`.venv`, already covered by `.gitignore`).
- Pinned tested versions in `requirements.txt`.
- Added `tests/`, `configs/`, `results/` and `report/` folders.

## 25 Nov 2026
- Implemented `greedy_heap` in `src/modified.py`.
- Set up pytest (`conftest.py`, `src/__init__.py`); run with `python -m pytest`.
  Running test files directly failed with "No module named 'src'".
- Added 9 tests, including heap = scan on 200 random cases with ties and
  brute-force optimality. All pass.

## Next steps
- `src/data.py`, `src/metrics.py`, `run_experiments.py`, configs.