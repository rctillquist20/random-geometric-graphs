"""Paired seeded density sweep comparing reverse deletion to forward methods.

    uv run --with networkx --with igraph --with numpy --with scipy \
      --with shapely --with jax --with matplotlib python experiments_reverse_threshold.py

The same point cloud is reused across radii within a repeat. Reverse's first
order is the primary comparison; the best of several orders is separate and
charged their cumulative runtime. All forward pipelines receive the existing
exact global repair and common pruning. Times include distance computation and
final checking. Full wall-clock timing charges conversion and distance
preprocessing to every method, plus the entire existing forward pipeline.
The older stage-sum timing is available only for reproducing earlier runs.

With --pruning-backend shared-optimized, reverse and every forward pruning
stage use the same 128-bit cached deletion kernel with seeded random orders.
The wrapper leaves the original modules intact. The forward deletion order
changes from the legacy scan, so final set sizes can change as well as times.
"""

import argparse
from collections import Counter
import contextlib
import csv
import json
import math
from pathlib import Path
import random
import re
import shutil
import statistics
import time
from unittest.mock import patch
import uuid

from algorithms.reverse_elimination import reverse_eliminate
from algorithms.shared_pruning_experimental import shared_pruning_backend
from functions.optimized_pruning import prune_resolving_set_optimized
from functions.reverse_pruning_control import reverse_eliminate_existing_pruner
from experiments_final_entropy_collision import (
    _method_functions, _prepare_graph, _run_final_pipeline,
)

TIMING_VERSION = "reverse-threshold-v2"
THRESHOLD_COLUMNS = (
    "method", "minimum_density", "graph_count", "independent_point_cloud_count",
    "size_and_speed_successes", "success_fraction",
    "median_speedup_vs_fastest_forward", "maximum_extra_landmarks",
)


def twin_lower_bound(graph):
    """Every true/false twin class of t vertices forces at least t-1 probes."""
    open_classes = Counter(tuple(sorted(graph.neighbors(node))) for node in graph)
    closed_classes = Counter(tuple(sorted({node, *graph.neighbors(node)})) for node in graph)
    return sum(size - 1 for size in open_classes.values()) + sum(size - 1 for size in closed_classes.values())


def write_csv(rows, path, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize_best_order_metadata(rows):
    """Recover the winning seed from order records in older draft results."""
    orders = {}
    for row in rows:
        if row["method"] == "reverse_order":
            key = (int(row["n"]), float(row["radius"]), int(row["repeat"]))
            orders.setdefault(key, []).append(row)
    changed = False
    for row in rows:
        if row["method"] != "reverse_best":
            continue
        key = (int(row["n"]), float(row["radius"]), int(row["repeat"]))
        best = min(orders[key], key=lambda order: (int(order["size"]), int(order["order_index"])))
        if int(row["algorithm_seed"]) != int(best["algorithm_seed"]):
            row["algorithm_seed"] = best["algorithm_seed"]
            changed = True
    return changed


def export_public_results(work_dir, output_dir, prefix="reverse_elimination"):
    """Expose only the compact results list and one useful chart."""
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(work_dir / "results.csv", output_dir / f"{prefix}_results.csv")
    chart = work_dir / "crossover.png"
    if not chart.exists():
        chart = work_dir / "comparison.png"
    shutil.copyfile(chart, output_dir / f"{prefix}_threshold.png")


def benchmark(args):
    shared_backend = getattr(args, "pruning_backend", "original") == "shared-optimized"
    rows = []
    if args.resume and (args.output / "raw_results.csv").exists():
        with (args.output / "raw_results.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    completed = {(int(row["n"]), float(row["radius"]), int(row["repeat"])) for row in rows}
    repeat_counts = {n: (args.large_repeats if n >= 500 and args.large_repeats is not None else args.repeats) for n in args.n_values}
    total = sum(repeat_counts.values()) * len(args.r_values)
    done = 0
    for n in args.n_values:
        for repeat in range(repeat_counts[n]):
            point_seed = random.Random(args.seed + n * 1009 + repeat * 7919).randrange(2**32)
            for radius_index, radius in enumerate(args.r_values):
                if (n, radius, repeat + 1) in completed:
                    done += 1
                    continue
                prepared = _prepare_graph(n, radius, point_seed)
                graph = prepared["graph"]
                g, distances = prepared["converted"], prepared["dist_matrix"]
                run_seed = point_seed ^ int(round(radius * 1e9))
                base = {
                    "experiment_version": "reverse-shared-pruning-v1" if shared_backend else TIMING_VERSION,
                    "pruning_backend": "shared-optimized" if shared_backend else "original",
                    "pruning_bits": 128 if shared_backend else "mixed-original",
                    "prune_calls": 0, "pruning_seconds": 0.0,
                    "timing": args.timing,
                    "n": n, "radius": radius, "repeat": repeat + 1,
                    "point_seed": point_seed, "benchmark_seed": args.seed,
                    "k_nearest": args.k_nearest,
                    "twin_lower_bound": twin_lower_bound(graph),
                    **prepared["summary"],
                    "shared_preprocessing_seconds": prepared["shared_preprocessing_time_seconds"],
                    "graph_fingerprint": prepared["fingerprint"],
                }
                result = {}
                resolving_sets = {}
                # Rotate to avoid consistently timing one method first.
                names = ["reverse"] + args.methods
                offset = (repeat + radius_index) % len(names)
                names = names[offset:] + names[:offset]
                methods = _method_functions(graph, radius, args.k_nearest)
                for name in names:
                    if name == "reverse":
                        sizes, times, seeds = [], [], []
                        for order_index in range(args.orders):
                            order_seed = (run_seed + order_index * 104729) % (2**32)
                            start = time.perf_counter()
                            current_set = (
                                prune_resolving_set_optimized(g, range(n), distances, seed=order_seed, bits=128)
                                if shared_backend else reverse_eliminate(g, distances, seed=order_seed).resolving_set
                            )
                            elapsed = time.perf_counter() - start
                            sizes.append(len(current_set))
                            times.append(elapsed)
                            seeds.append(order_seed)
                            if order_index == 0:
                                resolving_sets["reverse"] = current_set
                            rows.append({
                                **base, "method": "reverse_order", "order_index": order_index,
                                "algorithm_seed": order_seed, "size": sizes[-1],
                                "seconds": elapsed + base["shared_preprocessing_seconds"],
                                "valid": True, "repair_added": 0,
                                "prune_calls": 1, "pruning_seconds": elapsed,
                            })
                        result["reverse"] = (sizes[0], times[0] + base["shared_preprocessing_seconds"])
                        result["reverse_best"] = (min(sizes), sum(times) + base["shared_preprocessing_seconds"])
                        for key in ("reverse", "reverse_best"):
                            rows.append({
                                **base, "method": key, "order_index": -1,
                                "algorithm_seed": seeds[0 if key == "reverse" else sizes.index(min(sizes))], "size": result[key][0],
                                "seconds": result[key][1], "valid": True, "repair_added": 0,
                                "prune_calls": 1 if key == "reverse" else len(times),
                                "pruning_seconds": times[0] if key == "reverse" else sum(times),
                            })
                    elif name == "reverse_control":
                        start = time.perf_counter()
                        control = reverse_eliminate_existing_pruner(
                            g, distances, seed=run_seed % (2**32), bits=128,
                        )
                        elapsed = time.perf_counter() - start
                        resolving_sets[name] = control
                        result[name] = (len(control), elapsed + base["shared_preprocessing_seconds"])
                        rows.append({
                            **base, "method": name, "order_index": -1,
                            "algorithm_seed": run_seed % (2**32), "size": len(control),
                            "seconds": result[name][1], "valid": True, "repair_added": 0,
                        })
                    else:
                        family, strategy = ("ich", "collision") if name == "ich_shared" else (name.split("_") if "_" in name else (name, "collision"))
                        # Preserve the ICH selector and inject the same shortest
                        # paths, bypassing only its Python Floyd-Warshall stage.
                        shared_ich = name == "ich_shared"
                        matrix_context = patch("algorithms.ich_collision_method._distance_matrix", return_value=distances) if shared_ich else contextlib.nullcontext()
                        backend_context = shared_pruning_backend(run_seed % (2**32)) if shared_backend else contextlib.nullcontext()
                        with backend_context as backend_stats:
                            pipeline_start = time.perf_counter()
                            with matrix_context:
                                run = _run_final_pipeline(
                                    methods[family][strategy], run_seed % (2**32), g, distances, family, strategy
                                )
                            # Include the complete pipeline and exact checking.
                            from functions.resolving_functions import checkIfResolvingSet_igraph
                            start = time.perf_counter()
                            valid = checkIfResolvingSet_igraph(g, run["_final_set"], distances)
                            check_time = time.perf_counter() - start
                            if args.timing == "full":
                                elapsed = time.perf_counter() - pipeline_start
                                total_seconds = elapsed + base["shared_preprocessing_seconds"]
                            else:
                                total_seconds = run["final_total_time_seconds"] + check_time + (base["shared_preprocessing_seconds"] if shared_ich else 0)
                        result[name] = (run["final_size"], total_seconds)
                        if not valid:
                            raise RuntimeError(f"invalid {name} output")
                        rows.append({
                            **base, "method": name, "order_index": -1,
                            "algorithm_seed": run_seed % (2**32),
                            "size": result[name][0], "seconds": result[name][1],
                            "valid": valid, "repair_added": run["repair_probe_count"],
                            "prune_calls": backend_stats.calls if shared_backend else 0,
                            "pruning_seconds": backend_stats.seconds if shared_backend else 0.0,
                        })
                if "reverse_control" in resolving_sets and resolving_sets["reverse_control"] != resolving_sets["reverse"]:
                    raise RuntimeError("same-order control and optimized reverse produced different sets")
                done += 1
                print(f"[{done}/{total}] n={n} r={radius:.4f} repeat={repeat+1} "
                      f"density={base['edge_density']:.3f} " + " ".join(
                          f"{key}={size}/{seconds:.3f}s" for key, (size, seconds) in result.items()
                      ), flush=True)
                write_csv(rows, args.output / "raw_results.csv")
    return rows


def summarize(rows, output):
    order_count = len({int(row["order_index"]) for row in rows if row["method"] == "reverse_order"})
    display_names = {"reverse": "Reverse elimination (one order)", "reverse_best": f"Reverse elimination (best of {order_count} orders)", "reverse_control": "Reverse (existing pruner, same order)", "grid": "Grid collision", "circle": "Circle collision", "zoomed": "Zoomed Square collision", "ich_shared": "ICH collision"}
    show_components = any(int(row.get("component_count", 1)) > 1 for row in rows)
    readable = [
        {
            "Nodes": row["n"], "Radius": row["radius"],
            "Density (%)": round(float(row["edge_density"]) * 100, 4),
            **({"Components": int(row.get("component_count", 1))} if show_components else {}),
            "Repeat": row["repeat"], "Method": display_names[row["method"]],
            "Set Size": row["size"], "Runtime (s)": round(float(row["seconds"]), 6),
            "Valid": "Yes" if str(row["valid"]).lower() == "true" else "No",
        }
        for row in sorted(rows, key=lambda item: (int(item["n"]), float(item["radius"]), int(item["repeat"]), item["method"]))
        if row["method"] in display_names
    ]
    write_csv(readable, output / "results.csv")
    groups = {}
    for row in rows:
        if row["method"] == "reverse_order":
            continue
        key = (int(row["n"]), float(row["radius"]), row["method"])
        groups.setdefault(key, []).append(row)
    paired = {}
    for row in rows:
        if row["method"] != "reverse_order":
            paired.setdefault((int(row["n"]), float(row["radius"]), int(row["repeat"])), {})[row["method"]] = row
    summary = []
    for (n, radius, method), entries in sorted(groups.items()):
        size_deltas, wins, joint = [], [], []
        for row in entries:
            trial = paired[n, radius, int(row["repeat"])]
            competitors = [value for key, value in trial.items() if not key.startswith("reverse")]
            best_size = min(int(value["size"]) for value in competitors)
            size_deltas.append(int(row["size"]) - best_size)
            wins.append(int(row["size"]) <= best_size)
            joint.append(any(int(row["size"]) <= int(value["size"]) and float(row["seconds"]) < float(value["seconds"]) for value in competitors))
        summary.append({
            "n": n, "radius": radius, "method": method, "repeats": len(entries),
            "mean_density": statistics.fmean(float(row["edge_density"]) for row in entries),
            "mean_degree": statistics.fmean(float(row["average_degree"]) for row in entries),
            "mean_twin_lower_bound": statistics.fmean(int(row.get("twin_lower_bound", 0)) for row in entries),
            "mean_size": statistics.fmean(int(row["size"]) for row in entries),
            "median_seconds": statistics.median(float(row["seconds"]) for row in entries),
            "mean_size_gap_vs_best_forward": statistics.fmean(size_deltas),
            "matches_or_beats_best_forward_fraction": statistics.fmean(wins),
            "dominates_at_least_one_forward_fraction": statistics.fmean(joint),
        })
    write_csv(summary, output / "summary.csv")
    comparisons = []
    for (n, radius, repeat), trial in sorted(paired.items()):
        reverse = trial["reverse"]
        competitors = [value for key, value in trial.items() if not key.startswith("reverse")]
        best_size = min(int(value["size"]) for value in competitors)
        fastest_time = min(float(value["seconds"]) for value in competitors)
        comparison = {
            "n": n, "radius": radius, "repeat": repeat,
            "density": float(reverse["edge_density"]),
            "average_degree": float(reverse["average_degree"]),
            "reverse_size": int(reverse["size"]),
            "best_forward_size": best_size,
            "reverse_size_gap": int(reverse["size"]) - best_size,
            "reverse_seconds": float(reverse["seconds"]),
            "fastest_forward_seconds": fastest_time,
            "speedup_vs_fastest_forward": fastest_time / float(reverse["seconds"]),
            "size_and_speed_success": int(reverse["size"]) <= best_size and float(reverse["seconds"]) < fastest_time,
        }
        if "reverse_best" in trial:
            best_orders = trial["reverse_best"]
            comparison.update({
                "best_orders_size": int(best_orders["size"]),
                "best_orders_size_gap": int(best_orders["size"]) - best_size,
                "best_orders_seconds": float(best_orders["seconds"]),
                "best_orders_speedup": fastest_time / float(best_orders["seconds"]),
                "best_orders_success": int(best_orders["size"]) <= best_size and float(best_orders["seconds"]) < fastest_time,
            })
        if "reverse_control" in trial:
            control = trial["reverse_control"]
            comparison.update({
                "existing_pruner_size": int(control["size"]),
                "existing_pruner_seconds": float(control["seconds"]),
                "optimized_speedup_vs_existing_pruner": float(control["seconds"]) / float(reverse["seconds"]),
                "existing_pruner_speedup_vs_fastest_forward": fastest_time / float(control["seconds"]),
            })
        comparisons.append(comparison)
    write_csv(comparisons, output / "paired_comparison.csv")
    radius_summary = []
    for n, radius in sorted({(row["n"], row["radius"]) for row in comparisons}):
        selected = [row for row in comparisons if (row["n"], row["radius"]) == (n, radius)]
        radius_summary.append({
            "Nodes": n, "Radius": radius, "Graphs": len(selected),
            "Mean Density (%)": 100 * statistics.fmean(row["density"] for row in selected),
            "Median Reverse Size": statistics.median(row["reverse_size"] for row in selected),
            "Median Best Collision Size": statistics.median(row["best_forward_size"] for row in selected),
            "Worst Extra Probes": max(row["reverse_size_gap"] for row in selected),
            "Matches Size And Faster": sum(row["size_and_speed_success"] for row in selected),
            "Median Reverse Seconds": statistics.median(row["reverse_seconds"] for row in selected),
            "Median Fastest Collision Seconds": statistics.median(row["fastest_forward_seconds"] for row in selected),
            "Median Speedup": statistics.median(row["speedup_vs_fastest_forward"] for row in selected),
            **({
                "Best Orders Worst Extra Probes": max(row["best_orders_size_gap"] for row in selected),
                "Best Orders Matches Size And Faster": sum(row["best_orders_success"] for row in selected),
                "Best Orders Median Speedup": statistics.median(row["best_orders_speedup"] for row in selected),
            } if all("best_orders_success" in row for row in selected) else {}),
        })
    write_csv(radius_summary, output / "radius_summary.csv")
    thresholds = []
    variants = [("reverse", "size_and_speed_success", "speedup_vs_fastest_forward", "reverse_size_gap")]
    if all("best_orders_success" in row for row in comparisons):
        variants.append(("reverse_best", "best_orders_success", "best_orders_speedup", "best_orders_size_gap"))
    for method, success_key, speed_key, gap_key in variants:
        for cutoff in (0.9, 0.95, 0.96, 0.97, 0.98, 0.985, 0.99, 0.995, 0.997, 0.998, 0.999):
            selected = [row for row in comparisons if row["density"] >= cutoff]
            if not selected:
                continue
            successes = sum(row[success_key] for row in selected)
            count = len(selected)
            fraction = successes / count
            thresholds.append({
                "method": method, "minimum_density": cutoff, "graph_count": count,
                "independent_point_cloud_count": len({(row["n"], row["repeat"]) for row in selected}),
                "size_and_speed_successes": successes, "success_fraction": fraction,
                "median_speedup_vs_fastest_forward": statistics.median(row[speed_key] for row in selected),
                "maximum_extra_landmarks": max(row[gap_key] for row in selected),
            })
    write_csv(thresholds, output / "density_thresholds.csv", THRESHOLD_COLUMNS)
    return summary


def plot(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ns = sorted({row["n"] for row in summary})
    methods = sorted({row["method"] for row in summary})
    display_names = {"grid": "Grid collision", "circle": "Circle collision", "zoomed": "Zoomed Square collision", "reverse": "Reverse: one order", "reverse_best": "Reverse: best of orders", "reverse_control": "Reverse: existing pruner (same order)", "ich_shared": "ICH collision"}
    fig, axes = plt.subplots(2, len(ns), figsize=(max(10, 6 * len(ns)), 8), squeeze=False)
    for column, n in enumerate(ns):
        for method in methods:
            selected = sorted((row for row in summary if row["n"] == n and row["method"] == method), key=lambda row: row["radius"])
            for axis, metric in ((axes[0, column], "mean_size"), (axes[1, column], "median_seconds")):
                axis.plot([row["radius"] for row in selected], [row[metric] for row in selected], marker="s" if method == "reverse_control" else "o", linestyle="--" if method == "reverse_control" else "-", markersize=3, label=display_names[method])
                axis.grid(alpha=0.25)
                axis.set_xlabel("Connection radius r (unit square)")
        axes[0, column].set_title(f"n = {n}")
        axes[0, column].set_ylabel("Mean valid resolving-set size")
        axes[1, column].set_ylabel("Median runtime, seconds")
        axes[1, column].set_yscale("log")
    axes[0, -1].legend(fontsize=8)
    fig.suptitle("Reverse elimination vs repaired forward methods; seeded paired graphs")
    fig.tight_layout()
    fig.savefig(output / "comparison.png", dpi=160)
    plt.close(fig)
    with (output / "paired_comparison.csv").open(newline="", encoding="utf-8") as stream:
        comparisons = list(csv.DictReader(stream))
    compared = comparisons
    if not compared:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained")
    config_path = output / "configuration.json"
    order_count = json.loads(config_path.read_text())["orders"] if config_path.exists() else "several"
    for n in sorted({int(row["n"]) for row in compared}):
        radii = sorted({float(row["radius"]) for row in compared if int(row["n"]) == n})
        variants = [("One order", "reverse_size_gap", "speedup_vs_fastest_forward", "o", "-")]
        if all("best_orders_success" in row for row in compared):
            variants.append((f"Best of {order_count} orders", "best_orders_size_gap", "best_orders_speedup", "s", "--"))
        if all("existing_pruner_speedup_vs_fastest_forward" in row for row in compared):
            variants.append(("Existing pruner (one order)", "reverse_size_gap", "existing_pruner_speedup_vs_fastest_forward", "D", ":"))
        for label, size_metric, time_metric, marker, linestyle in variants:
            for axis, metric in ((axes[0], size_metric), (axes[1], time_metric)):
                if axis is axes[0] and label.startswith("Existing pruner"):
                    continue  # same exact set as the optimized one-order run
                samples = [[float(row[metric]) for row in compared if int(row["n"]) == n and float(row["radius"]) == radius] for radius in radii]
                medians = [statistics.median(sample) for sample in samples]
                axis.errorbar(radii, medians, yerr=[[median - min(sample) for median, sample in zip(medians, samples)], [max(sample) - median for median, sample in zip(medians, samples)]], marker=marker, linestyle=linestyle, capsize=4, label=f"{label}, n={n}")
                axis.set_xlabel("Connection radius r (unit square)")
                axis.grid(alpha=0.2)
    axes[0].axhline(0, color="0.3", linewidth=1, linestyle="--")
    axes[0].set_title("Resolving-set size penalty")
    axes[0].set_ylabel("Extra probes vs smallest collision result")
    axes[1].axhline(1, color="0.3", linewidth=1, linestyle="--")
    axes[1].set_title("Runtime crossover: above 1 favors reverse")
    axes[1].set_ylabel("Fastest collision time / reverse time")
    axes[1].set_yscale("log")
    axes[0].legend()
    axes[1].legend()
    backend_label = "Shared optimized pruning; " if config_path.exists() and json.loads(config_path.read_text()).get("pruning_backend") == "shared-optimized" else ""
    fig.suptitle(backend_label + "median and min-max across point clouds")
    fig.savefig(output / "crossover.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", nargs="+", type=int, default=[100, 200, 500])
    parser.add_argument("--r-values", nargs="+", type=float, default=[0.03, 0.06, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2, math.sqrt(2)])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--large-repeats", type=int, default=None, help="optional separate repeat count for n >= 500")
    parser.add_argument("--resume", action="store_true", help="reuse completed graphs in --work-dir; keep configuration unchanged")
    parser.add_argument("--orders", type=int, default=3)
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261007)
    parser.add_argument("--methods", nargs="+", choices=["grid", "circle", "zoomed", "ich_shared", "reverse_control"], default=["grid", "circle", "zoomed"])
    parser.add_argument("--timing", choices=["full", "stages"], default="full")
    parser.add_argument("--pruning-backend", choices=["original", "shared-optimized"], default="original")
    parser.add_argument("--output", type=Path, default=Path("outputs"), help="directory for the results CSV and one chart")
    parser.add_argument("--work-dir", type=Path, help="internal checkpoint directory; defaults to an ignored .experiment_cache run")
    parser.add_argument("--result-prefix", default="reverse_elimination", help="filename prefix for the two public result files")
    parser.add_argument("--analyze-only", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.result_prefix):
        parser.error("--result-prefix must contain only letters, numbers, underscores or hyphens")
    if args.pruning_backend == "shared-optimized" and any(method not in {"grid", "circle", "zoomed"} for method in args.methods):
        parser.error("shared optimized pruning supports Grid, Circle and Zoomed Square")
    public_output = args.output
    if (args.resume or args.analyze_only) and args.work_dir is None:
        parser.error("--resume and --analyze-only require --work-dir")
    args.work_dir = args.work_dir or Path(".experiment_cache") / f"reverse_threshold_{uuid.uuid4().hex[:12]}"
    args.output = args.work_dir
    if not args.analyze_only:
        if min(args.n_values) < 2 or args.repeats < 1 or (args.large_repeats is not None and args.large_repeats < 1) or args.orders < 1 or any(not math.isfinite(r) or not 0 < r <= math.sqrt(2) for r in args.r_values):
            parser.error("radii in (0, sqrt(2)], n >= 2, repeats >= 1, orders >= 1 required")
        config_path = args.output / "configuration.json"
        if (args.output / "raw_results.csv").exists():
            if not args.resume:
                parser.error("results already exist; use a new output directory or --resume")
            if not config_path.exists():
                parser.error("cannot resume results without their configuration")
            previous = json.loads(config_path.read_text(encoding="utf-8"))
            for key in ("n_values", "r_values", "repeats", "large_repeats", "orders", "k_nearest", "seed", "methods", "timing", "pruning_backend"):
                if previous.get(key, "original" if key == "pruning_backend" else None) != getattr(args, key):
                    parser.error(f"cannot resume with a different {key}")
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "configuration.json").write_text(json.dumps({**vars(args), "output": str(args.output), "work_dir": str(args.work_dir), "results_output": str(public_output)}, indent=2), encoding="utf-8")
        rows = benchmark(args)
    else:
        with (args.output / "raw_results.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    if normalize_best_order_metadata(rows):
        write_csv(rows, args.output / "raw_results.csv")
    summary = summarize(rows, args.output)
    plot(summary, args.output)
    export_public_results(args.output, public_output, args.result_prefix)
    print(f"Wrote results CSV and one chart to {public_output}", flush=True)


if __name__ == "__main__":
    main()
