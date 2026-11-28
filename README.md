# Discrete Bit Loading for DMT: Scan vs Heap

EEP55C36 Computational Methods and Algorithms, final project (Track D). Based on J. Campello, "Practical bit loading for DMT," IEEE ICC 1999.

## Summary
Greedy bit loading repeatedly gives the next bit to the tone where it costs the least energy. The baseline finds that tone with a linear scan (O(N) per bit). The modification keeps tones in a min-heap of (cost, index) pairs (O(log N) per bit). Ties break by lowest index in both, so allocations are identical.

**Result:** identical allocations in all 240 test cases, no budget violations, and the heap was faster at every size: about 4x at N = 8, rising to about 11-12x at N = 4096.

## Setup
Tested with Python 3.13.0 on Windows 11 (versions pinned in `requirements.txt`).

```
git clone https://github.com/Rammanathan/bit-loading-dmt.git
cd bit-loading-dmt
python -m venv .venv
.venv\Scripts\Activate.ps1          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## How to run
| Step | Command | Time | Output |
|---|---|---|---|
| Tests | `python -m pytest` | ~1 s | 10 passed |
| Smoke run | `python run_experiments.py --config configs/smoke.json` | ~1 s | `results/smoke.csv` |
| Final run | `python run_experiments.py --config configs/final.json` | ~1 min | `results/final.csv` |
| Figures | `python make_figures.py` | ~3 s | `results/summary.csv`, `fig_speedup.png`, `fig_runtime.png` |

Timings depend on the machine; run on mains power with other programs closed.

## Repository layout
- `src/baseline.py`: `greedy_scan` (baseline)
- `src/modified.py`: `greedy_heap` (modification)
- `src/data.py`: synthetic channel generator (from the course guide)
- `src/metrics.py`: allocation energy and timing helper
- `tests/`: pytest checks (hand examples, brute force, heap = scan, invalid inputs)
- `configs/`: smoke and final experiment settings
- `results/`: final results, summary and figures
- `docs/progress.md`: development log

## Experiment design
- N = 8, 16, 64, 256, 1024, 4096 (4096 = stress case)
- 20 test channels per N (seeds 1000-1019); development used seeds 0-2
- Both `g_true` (ideal) and `g_hat` (estimated from pilots), same inputs for both methods
- Budget E_max = 1.0 x N; gap = 1; bmax = 15
- Time = median of 5 runs after one warm-up; heap setup timed separately
- Speed-up: geometric mean with 95% Student-t confidence interval
- Ablation: the scan baseline is the heap with only the selection step switched off

## Limitations
- Timings are for one machine and pure Python/NumPy.
- Allocations under `g_hat` are predictions, not proof of physical reliability.
- The course guide's hand example (g = [1, 1], E_max = 3 gives [2, 1]) needs energy 4 > 3; our code returns the feasible optimum [1, 1].

## AI use declaration
AI was used to explain project concepts, review and debug code, and figure-generation scripts. I reviewed and ran all submitted code, checked the generated results, and understand the methods and implementation. I take responsibility for the submitted work and can explain the code and results.