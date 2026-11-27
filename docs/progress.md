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
- Set up pytest (`conftest.py`, `src/__init__.py`); run with `python -m pytest`. Running test files directly failed with "No module named 'src'".
- Added 9 tests, including heap = scan on 200 random cases with ties and brute-force optimality. All pass.

### 26 Nov 2026
- Added `src/data.py` (channel generator from the course guide).
- Added `src/metrics.py` (`allocation_energy` moved here; `time_function`: one warm-up run, then the median of repeated runs).
- Added `run_experiments.py` and configs: N = 8, 16, 64, 256, 1024, 4096; 20 test seeds (1000–1019) per size; g_true and g_hat; budget = 1.0 × N; timings are the median of 5 runs after a warm-up. Heap setup timed separately.

### 27 Nov 2026
- Added `make_figures.py`: summary table (`results/summary.csv`) and two figures (speed-up vs N with 95% CI, runtime vs N). Speed-up uses the geometric mean (it is a ratio) and a Student-t interval (20 cases per N).
- Problem: the first final run showed g_true and g_hat taking up to 8x different times for the same work. Cause: all g_true cases ran first and the laptop slowed down partway through. Fix: interleaved the channel types inside the seed loop and reran on mains power with other apps closed.
- Result: identical allocations in all 240 cases, no budget violations; the heap is faster at every N, with the speed-up growing as N grows.