"""
Summarise results/final.csv and draw the comparison figures.

Usage:
    python make_figures.py                      # uses results/final.csv
    python make_figures.py --csv results/final.csv

Writes:
    results/summary.csv      per (channel, N): agreement, bits, times, speed-up with 95% CI
    results/fig_speedup.png  speed-up vs N with 95% confidence intervals
    results/fig_runtime.png  median runtime vs N for scan, heap and heap setup
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                  # draw to files, never open a window
import matplotlib.pyplot as plt
import numpy as np

# Two-sided 95% Student-t critical values, t(0.975, df).
T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
         8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
         14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
         20: 2.086, 24: 2.064, 29: 2.045, 39: 2.023, 49: 2.010}


def t_critical(df):
    """t(0.975, df) from the table; the nearest smaller listed df is conservative."""
    usable = [d for d in T_975 if d <= df]
    return T_975[max(usable)] if usable else T_975[1]


def mean_ci(values):
    """Mean and half-width of the 95% t confidence interval."""
    values = np.asarray(values, dtype=float)
    n = values.size
    mean = float(values.mean())
    if n < 2:
        return mean, float("nan")
    half = t_critical(n - 1) * values.std(ddof=1) / np.sqrt(n)
    return mean, float(half)


def summarise(rows):
    """One summary row per (channel, N)."""
    summary = []
    for channel in sorted({r["channel"] for r in rows}, reverse=True):
        for N in sorted({int(r["N"]) for r in rows}):
            group = [r for r in rows if r["channel"] == channel and int(r["N"]) == N]
            if not group:
                continue
            # Speed-up is a ratio, so average its log and transform back:
            # this gives a geometric mean and a CI that cannot go below zero.
            log_speedup = np.log([float(r["speedup"]) for r in group])
            m, h = mean_ci(log_speedup)
            summary.append({
                "channel": channel,
                "N": N,
                "cases": len(group),
                "identical_allocations": sum(r["identical"] == "True" for r in group),
                "mean_bits": float(np.mean([int(r["scan_bits"]) for r in group])),
                "max_violation": max(float(r["scan_violation"]) for r in group)
                                 + max(float(r["heap_violation"]) for r in group),
                "median_scan_ms": 1e3 * float(np.median([float(r["scan_time_s"]) for r in group])),
                "median_heap_ms": 1e3 * float(np.median([float(r["heap_time_s"]) for r in group])),
                "median_setup_ms": 1e3 * float(np.median([float(r["heap_setup_s"]) for r in group])),
                "speedup_geomean": float(np.exp(m)),
                "speedup_ci_low": float(np.exp(m - h)),
                "speedup_ci_high": float(np.exp(m + h)),
            })
    return summary


def plot_speedup(summary, path):
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, channel in enumerate(sorted({s["channel"] for s in summary}, reverse=True)):
        part = [s for s in summary if s["channel"] == channel]
        N = np.array([s["N"] for s in part], dtype=float)
        y = np.array([s["speedup_geomean"] for s in part])
        low = y - np.array([s["speedup_ci_low"] for s in part])
        high = np.array([s["speedup_ci_high"] for s in part]) - y
        shift = 1.04 if i else 0.96                 # small offset so whiskers don't overlap
        ax.errorbar(N * shift, y, yerr=[low, high], marker="o", capsize=3, label=channel)
    ax.axhline(1.0, color="0.5", linestyle="--", linewidth=1, label="no speed-up")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("number of tones N")
    ax.set_ylabel("speed-up (scan time / heap time)")
    ax.set_title("Heap vs scan: speed-up with 95% CI (20 channels per N)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_runtime(summary, path, channel="g_hat"):
    part = [s for s in summary if s["channel"] == channel]
    N = np.array([s["N"] for s in part], dtype=float)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(N, [s["median_scan_ms"] for s in part], "o-", label="scan (baseline)")
    ax.plot(N, [s["median_heap_ms"] for s in part], "s-", label="heap (total)")
    ax.plot(N, [s["median_setup_ms"] for s in part], "^--", label="heap setup only")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("number of tones N")
    ax.set_ylabel("median runtime (ms)")
    ax.set_title(f"Runtime vs problem size ({channel})")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="results/final.csv")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))

    summary = summarise(rows)
    out_dir = csv_path.parent
    with open(out_dir / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    plot_speedup(summary, out_dir / "fig_speedup.png")
    plot_runtime(summary, out_dir / "fig_runtime.png")

    for s in summary:
        print(f"{s['channel']:6s} N={s['N']:5d}  identical {s['identical_allocations']}/{s['cases']}  "
              f"speed-up {s['speedup_geomean']:.2f}x "
              f"[{s['speedup_ci_low']:.2f}, {s['speedup_ci_high']:.2f}]")
    print(f"Wrote {out_dir / 'summary.csv'}, fig_speedup.png, fig_runtime.png")


if __name__ == "__main__":
    main()