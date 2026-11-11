"""Rapid collision-method sweep across theory-driven RGG radii.

For n nodes, the sweep uses three evenly spaced values below
t = sqrt(pi * ln(n) / n), t itself, and ten evenly spaced values after t
through the unit-square maximum radius sqrt(2).  Each repeat reuses the same
uniform point cloud at every radius, so its graphs are nested.
"""

import argparse
import csv
import math
from pathlib import Path
import random

from experiments_clustered_collision import METHODS, _method_functions, _rotated
from experiments_final_entropy_collision import (
    _prepare_graph,
    _public_pipeline_data,
    _run_final_pipeline,
)


EXPERIMENT_VERSION = "radius-sweep-collision-v1"
RUN_SEED_MASK = 0xA24BAED4
RESULT_COLUMNS = (
    "Repeat",
    "Radius Index",
    "Radius",
    "Threshold t",
    "Threshold Region",
    "Average Degree",
    "Components",
    "Connected",
    "Method",
    "Final Set Size",
    "Runtime (s)",
    "Raw Set Size",
    "Raw Valid",
    "Repair Added",
    "Repair Pruned",
    "Final Valid",
)
METHOD_DISPLAY_NAMES = {
    "grid": "Grid",
    "zoomed": "Zoomed Square",
    "circle": "Circle",
}


def radius_schedule(n):
    if n < 2:
        raise ValueError("n must be at least 2")
    threshold = math.sqrt(math.pi * math.log(n) / n)
    below = [threshold * fraction / 4 for fraction in range(1, 4)]
    above_step = (math.sqrt(2) - threshold) / 10
    above = [threshold + above_step * index for index in range(1, 11)]
    above[-1] = math.sqrt(2)
    radii = tuple(below + [threshold] + above)
    if len(radii) != 14 or not all(
        0 < left < right <= math.sqrt(2)
        for left, right in zip(radii, radii[1:])
    ):
        raise RuntimeError("radius schedule is not strictly increasing")
    return threshold, radii


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="independent point clouds; positions are reused across radii",
    )
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/radius_sweep_collision_results.csv"),
    )
    return parser.parse_args()


def run_benchmark(n, repeats, k_nearest, seed):
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if k_nearest < 1:
        raise ValueError("k_nearest must be positive")

    threshold, radii = radius_schedule(n)
    seed_generator = random.Random(seed)
    point_seeds = [seed_generator.randrange(2**32) for _ in range(repeats)]
    rows = []
    total_graphs = repeats * len(radii)
    graph_sequence = 0

    for repeat_index, point_seed in enumerate(point_seeds, start=1):
        previous_edges = -1
        for radius_index, radius in enumerate(radii, start=1):
            graph_sequence += 1
            prepared = _prepare_graph(n, radius, point_seed)
            summary = prepared["summary"]
            if summary["edge_count"] < previous_edges:
                raise RuntimeError("nested graph edge count decreased")
            previous_edges = summary["edge_count"]

            methods = _method_functions(
                prepared["graph"],
                radius,
                k_nearest,
            )
            method_order = _rotated(
                METHODS,
                repeat_index - 1 + radius_index - 1,
            )
            run_seed = (
                point_seed
                ^ RUN_SEED_MASK
                ^ int(round(radius * 1_000_000_000))
            ) % (2**32)
            method_data = {}

            for method_position, method in enumerate(method_order, start=1):
                pipeline = _run_final_pipeline(
                    method=methods[method],
                    pair_seed=run_seed,
                    converted_graph=prepared["converted"],
                    dist_matrix=prepared["dist_matrix"],
                    family=method,
                    strategy="collision",
                )
                if not pipeline["final_valid"]:
                    raise RuntimeError(
                        f"repeat {repeat_index}, radius {radius}, {method} invalid"
                    )
                pipeline["method_execution_position"] = method_position
                method_data[method] = pipeline

            threshold_region = (
                "below"
                if radius < threshold
                else "threshold"
                if math.isclose(radius, threshold, rel_tol=0, abs_tol=1e-15)
                else "above"
            )
            for method in METHODS:
                pipeline = method_data[method]
                rows.append(
                    {
                        "experiment_version": EXPERIMENT_VERSION,
                        "benchmark_seed": seed,
                        "n": n,
                        "repeat": repeat_index,
                        "radius_index": radius_index,
                        "radius": radius,
                        "threshold": threshold,
                        "threshold_region": threshold_region,
                        "point_seed": point_seed,
                        "edge_count": summary["edge_count"],
                        "average_degree": summary["average_degree"],
                        "component_count": summary["component_count"],
                        "connected": summary["connected"],
                        "isolated_node_count": summary["isolated_node_count"],
                        "method": method,
                        "method_execution_position": pipeline[
                            "method_execution_position"
                        ],
                        "method_execution_order": ",".join(method_order),
                        **_public_pipeline_data(pipeline),
                    }
                )

            size_text = " ".join(
                f"{method}={method_data[method]['final_size']}"
                for method in METHODS
            )
            print(
                f"[{graph_sequence:02d}/{total_graphs:02d}] "
                f"repeat={repeat_index}/{repeats} r={radius:.4f} "
                f"degree={summary['average_degree']:.1f} "
                f"components={summary['component_count']} {size_text}",
                flush=True,
            )

    return threshold, radii, rows


def write_results(rows, output_path):
    if not rows:
        raise ValueError("cannot write an empty benchmark")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "Repeat": row["repeat"],
                    "Radius Index": row["radius_index"],
                    "Radius": row["radius"],
                    "Threshold t": row["threshold"],
                    "Threshold Region": row["threshold_region"],
                    "Average Degree": row["average_degree"],
                    "Components": row["component_count"],
                    "Connected": "Yes" if row["connected"] else "No",
                    "Method": METHOD_DISPLAY_NAMES[row["method"]],
                    "Final Set Size": row["final_size"],
                    "Runtime (s)": row["final_total_time_seconds"],
                    "Raw Set Size": row["original_size"],
                    "Raw Valid": "Yes" if row["original_valid"] else "No",
                    "Repair Added": row["repair_probe_count"],
                    "Repair Pruned": row["pruned_after_repair"],
                    "Final Valid": "Yes" if row["final_valid"] else "No",
                }
            )


def main():
    args = _parse_args()
    threshold, radii, rows = run_benchmark(
        n=args.n,
        repeats=args.repeats,
        k_nearest=args.k_nearest,
        seed=args.seed,
    )
    write_results(rows, args.output)
    print(f"threshold={threshold:.12f}")
    print("radii=" + ",".join(f"{radius:.12f}" for radius in radii))
    print(f"Wrote {len(rows)} results to {args.output}")


if __name__ == "__main__":
    main()
