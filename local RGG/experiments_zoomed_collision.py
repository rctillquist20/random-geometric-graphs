"""Paired benchmark for Zoomed Square entropy versus collision scoring."""

import argparse
import csv
from pathlib import Path
import random
import time

import igraph as ig
import networkx as nx

from algorithms.zoomed_square_collision_method import (
    get_metric_dimension_zoomed_square_collision,
    get_metric_dimension_zoomed_square_entropy_experimental,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", nargs="+", type=int, default=[50, 100, 200, 500])
    parser.add_argument("--r-values", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260807)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("zoomed_collision_comparison_results.csv"),
    )
    return parser.parse_args()


def _size_winner(entropy_valid, collision_valid, entropy_size, collision_size):
    if entropy_valid and not collision_valid:
        return "zoomed_entropy"
    if collision_valid and not entropy_valid:
        return "zoomed_collision"
    if not entropy_valid and not collision_valid:
        return "neither"
    if entropy_size < collision_size:
        return "zoomed_entropy"
    if collision_size < entropy_size:
        return "zoomed_collision"
    return "tie"


def _run_method(method, graph, radius, k_nearest, run_seed):
    random.seed(run_seed)
    start = time.perf_counter()
    run = method(graph, radius, k_nearest=k_nearest)
    elapsed = time.perf_counter() - start
    return run, elapsed


def run_benchmark(n_values, r_values, repeats, k_nearest, seed):
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if k_nearest < 2:
        raise ValueError(
            "k_nearest must be at least 2 to compare candidate scoring rules"
        )

    seed_generator = random.Random(seed)
    rows = []

    for n in n_values:
        for radius in r_values:
            for repeat in range(repeats):
                graph_seed = seed_generator.randrange(2**32)
                graph = nx.random_geometric_graph(n, radius, seed=graph_seed)
                g = ig.Graph.from_networkx(graph)
                dist_matrix = g.distances()
                run_seed = graph_seed ^ 0x9E3779B9

                methods = [
                    (
                        "zoomed_entropy",
                        get_metric_dimension_zoomed_square_entropy_experimental,
                    ),
                    (
                        "zoomed_collision",
                        get_metric_dimension_zoomed_square_collision,
                    ),
                ]
                if repeat % 2:
                    methods.reverse()

                run_data = {}
                for method_name, method in methods:
                    run, elapsed = _run_method(
                        method,
                        graph,
                        radius,
                        k_nearest,
                        run_seed,
                    )
                    run_data[method_name] = {
                        "pre_prune_size": run.pre_prune_size,
                        "size": len(run.resolving_set),
                        "time_seconds": elapsed,
                        "valid": checkIfResolvingSet_igraph(
                            g,
                            run.resolving_set,
                            dist_matrix,
                        ),
                    }

                entropy = run_data["zoomed_entropy"]
                collision = run_data["zoomed_collision"]
                rows.append(
                    {
                        "n": n,
                        "radius": radius,
                        "repeat": repeat + 1,
                        "graph_seed": graph_seed,
                        "edges": graph.number_of_edges(),
                        "components": nx.number_connected_components(graph),
                        "k_nearest": k_nearest,
                        "zoomed_entropy_pre_prune_size": entropy["pre_prune_size"],
                        "zoomed_entropy_size": entropy["size"],
                        "zoomed_entropy_time_seconds": entropy["time_seconds"],
                        "zoomed_entropy_valid": entropy["valid"],
                        "zoomed_collision_pre_prune_size": collision[
                            "pre_prune_size"
                        ],
                        "zoomed_collision_size": collision["size"],
                        "zoomed_collision_time_seconds": collision["time_seconds"],
                        "zoomed_collision_valid": collision["valid"],
                        "size_difference_collision_minus_entropy": (
                            collision["size"] - entropy["size"]
                        ),
                        "time_difference_collision_minus_entropy_seconds": (
                            collision["time_seconds"] - entropy["time_seconds"]
                        ),
                        "size_winner": _size_winner(
                            entropy["valid"],
                            collision["valid"],
                            entropy["size"],
                            collision["size"],
                        ),
                        "faster_method": (
                            "zoomed_collision"
                            if collision["time_seconds"] < entropy["time_seconds"]
                            else "zoomed_entropy"
                            if entropy["time_seconds"] < collision["time_seconds"]
                            else "tie"
                        ),
                    }
                )
                print(
                    f"n={n:4d} r={radius:.2f} repeat={repeat + 1}/{repeats} "
                    f"entropy={entropy['size']} collision={collision['size']} "
                    f"winner={rows[-1]['size_winner']}"
                )

    return rows


def write_results(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = _parse_args()
    rows = run_benchmark(
        args.n_values,
        args.r_values,
        args.repeats,
        args.k_nearest,
        args.seed,
    )
    write_results(rows, args.output)
    print(f"Wrote {len(rows)} paired runs to {args.output}")


if __name__ == "__main__":
    main()
