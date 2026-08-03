"""Paired benchmark for entropy versus collision-aware landmark selection."""

import argparse
import csv
from pathlib import Path
import random
import time

import igraph as ig
import networkx as nx

from algorithms.grid_collision_method import (
    get_metric_dimension_grid_collision,
    get_metric_dimension_grid_entropy_experimental,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", nargs="+", type=int, default=[50, 100, 200, 500])
    parser.add_argument("--r-values", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("collision_comparison_results.csv"),
    )
    return parser.parse_args()


def _winner(entropy_valid, collision_valid, entropy_size, collision_size):
    if entropy_valid and not collision_valid:
        return "entropy"
    if collision_valid and not entropy_valid:
        return "collision"
    if not entropy_valid and not collision_valid:
        return "neither"
    if entropy_size < collision_size:
        return "entropy"
    if collision_size < entropy_size:
        return "collision"
    return "tie"


def _run_method(method, graph, radius, k_nearest, prune_seed):
    random.seed(prune_seed)
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
                components = nx.number_connected_components(graph)
                edge_count = graph.number_of_edges()
                prune_seed = graph_seed ^ 0x9E3779B9

                methods = [
                    ("entropy", get_metric_dimension_grid_entropy_experimental),
                    ("collision", get_metric_dimension_grid_collision),
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
                        prune_seed,
                    )
                    valid = checkIfResolvingSet_igraph(
                        g,
                        run.resolving_set,
                        dist_matrix,
                    )
                    run_data[method_name] = {
                        "size": len(run.resolving_set),
                        "pre_prune_size": run.pre_prune_size,
                        "time_seconds": elapsed,
                        "valid": valid,
                    }

                entropy = run_data["entropy"]
                collision = run_data["collision"]
                winner = _winner(
                    entropy["valid"],
                    collision["valid"],
                    entropy["size"],
                    collision["size"],
                )
                rows.append(
                    {
                        "n": n,
                        "radius": radius,
                        "repeat": repeat + 1,
                        "graph_seed": graph_seed,
                        "edges": edge_count,
                        "components": components,
                        "k_nearest": k_nearest,
                        "entropy_pre_prune_size": entropy["pre_prune_size"],
                        "entropy_size": entropy["size"],
                        "entropy_time_seconds": entropy["time_seconds"],
                        "entropy_valid": entropy["valid"],
                        "collision_pre_prune_size": collision["pre_prune_size"],
                        "collision_size": collision["size"],
                        "collision_time_seconds": collision["time_seconds"],
                        "collision_valid": collision["valid"],
                        "size_difference_collision_minus_entropy": (
                            collision["size"] - entropy["size"]
                        ),
                        "winner": winner,
                    }
                )
                print(
                    f"n={n:4d} r={radius:.2f} repeat={repeat + 1}/{repeats} "
                    f"entropy={entropy['size']} collision={collision['size']} "
                    f"winner={winner}"
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
