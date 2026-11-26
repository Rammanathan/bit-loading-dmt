"""
Run the scan-vs-heap bit-loading comparison described in a config file.

Usage:
    python run_experiments.py --config configs/smoke.json
    python run_experiments.py --config configs/final.json

For every (channel type, tone count N, seed) it generates one channel,
runs both methods on exactly the same g, budget, gap and cap, checks the
allocations, times both, and writes one row per case to a CSV file.
"""
import argparse
import csv
import heapq
import json
import platform
import sys
from pathlib import Path

import numpy as np

from src.baseline import greedy_scan
from src.data import make_loading_case
from src.metrics import time_function
from src.modified import greedy_heap


def build_heap_only(g, gap):
    """Heap setup step alone (list of (cost, index) + heapify), for timing."""
    cost = gap / g
    heap = [(float(cost[i]), i) for i in range(len(g))]
    heapq.heapify(heap)
    return heap


def run_case(g, budget, gap, bmax, repeats):
    """Run and time both methods on one channel; return a dict of results."""
    scan = greedy_scan(g, budget, gap=gap, bmax=bmax)
    heap = greedy_heap(g, budget, gap=gap, bmax=bmax)

    scan_time = time_function(greedy_scan, g, budget, gap=gap, bmax=bmax, repeats=repeats)
    heap_time = time_function(greedy_heap, g, budget, gap=gap, bmax=bmax, repeats=repeats)
    setup_time = time_function(build_heap_only, g, gap, repeats=repeats)

    return {
        "scan_bits": int(scan["bits"].sum()),
        "heap_bits": int(heap["bits"].sum()),
        "scan_energy": scan["energy_used"],
        "heap_energy": heap["energy_used"],
        "scan_violation": max(0.0, scan["energy_used"] - budget),
        "heap_violation": max(0.0, heap["energy_used"] - budget),
        "identical": bool(np.array_equal(scan["bits"], heap["bits"])),
        "scan_time_s": scan_time,
        "heap_time_s": heap_time,
        "heap_setup_s": setup_time,
        "speedup": scan_time / heap_time,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="path to a JSON config")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text())
    seeds = range(config["seed_start"], config["seed_start"] + config["num_seeds"])
    output = Path(config["output"])
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for channel in config["channels"]:
        for N in config["tones"]:
            budget = config["rho"] * N
            for seed in seeds:
                g_true, g_hat = make_loading_case(seed, tones=N)
                g = g_true if channel == "g_true" else g_hat
                result = run_case(g, budget, config["gap"], config["bmax"], config["repeats"])
                rows.append({"channel": channel, "N": N, "seed": seed,
                             "budget": budget, **result})
            group = [r for r in rows if r["channel"] == channel and r["N"] == N]
            print(f"{channel:6s} N={N:5d}  identical={all(r['identical'] for r in group)}  "
                  f"median speed-up={np.median([r['speedup'] for r in group]):.2f}x")

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    env = output.with_name(output.stem + "_environment.txt")
    env.write_text(
        f"config: {args.config}\n"
        f"python: {sys.version.split()[0]}\n"
        f"numpy: {np.__version__}\n"
        f"platform: {platform.platform()}\n"
        f"processor: {platform.processor() or 'unknown'}\n"
    )
    print(f"Wrote {len(rows)} rows to {output} and environment info to {env}")


if __name__ == "__main__":
    main()