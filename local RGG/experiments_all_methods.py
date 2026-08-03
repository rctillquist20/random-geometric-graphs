"""Paired benchmark for every project method plus Grid Collision."""

import argparse
import contextlib
import csv
import io
from pathlib import Path
import random
import time

import igraph as ig
import networkx as nx
import numpy as np

from algorithms.circle_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_circle,
)
from algorithms.grid_collision_method import get_metric_dimension_grid_collision
from algorithms.grid_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_grid,
)
from algorithms.ich_multilateration import get_metric_dimension_of_graph_ich
from algorithms.zoomed_square_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_zoomed_square,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


METHOD_NAMES = (
    "grid",
    "grid_collision",
    "circle",
    "zoomed_square",
    "ich",
)


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", nargs="+", type=int, default=[50, 100, 200, 500])
    parser.add_argument("--r-values", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("all_methods_results.csv"),
    )
    return parser.parse_args()


def _method_functions(graph, radius, k_nearest):
    return {
        "grid": lambda: get_metric_dimension_of_graph_with_pruning_igraph_grid(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "grid_collision": lambda: get_metric_dimension_grid_collision(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "circle": lambda: get_metric_dimension_of_graph_with_pruning_igraph_circle(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "zoomed_square": lambda: (
            get_metric_dimension_of_graph_with_pruning_igraph_zoomed_square(
                graph,
                radius,
                k_nearest=k_nearest,
            )
        ),
        "ich": lambda: get_metric_dimension_of_graph_ich(graph),
    }


def _run_method(method_name, method, seed):
    random.seed(seed)
    np.random.seed(seed % (2**32))
    captured_output = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(captured_output):
        result = method()
    elapsed = time.perf_counter() - start

    if method_name == "grid_collision":
        return result.resolving_set, elapsed, result.pre_prune_size
    return set(result), elapsed, None


def _winning_methods(run_data, value_name):
    valid_methods = [
        name for name in METHOD_NAMES if run_data[name]["valid"]
    ]
    if not valid_methods:
        return "none"
    best_value = min(run_data[name][value_name] for name in valid_methods)
    return ", ".join(
        name for name in valid_methods if run_data[name][value_name] == best_value
    )


def run_benchmark(n_values, r_values, repeats, k_nearest, seed):
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if k_nearest < 2:
        raise ValueError("k_nearest must be at least 2 for entropy comparisons")

    seed_generator = random.Random(seed)
    rows = []

    for n in n_values:
        for radius in r_values:
            for repeat in range(repeats):
                graph_seed = seed_generator.randrange(2**32)
                graph = nx.random_geometric_graph(n, radius, seed=graph_seed)
                g = ig.Graph.from_networkx(graph)
                dist_matrix = g.distances()

                methods = list(METHOD_NAMES)
                shift = repeat % len(methods)
                methods = methods[shift:] + methods[:shift]
                functions = _method_functions(graph, radius, k_nearest)
                run_data = {}

                for method_index, method_name in enumerate(methods):
                    method_seed = (
                        graph_seed ^ 0x9E3779B9 ^ ((method_index + 1) * 0x85EBCA6B)
                    ) % (2**32)
                    resolving_set, elapsed, pre_prune_size = _run_method(
                        method_name,
                        functions[method_name],
                        method_seed,
                    )
                    run_data[method_name] = {
                        "size": len(resolving_set),
                        "time_seconds": elapsed,
                        "valid": checkIfResolvingSet_igraph(
                            g,
                            resolving_set,
                            dist_matrix,
                        ),
                        "pre_prune_size": pre_prune_size,
                    }

                row = {
                    "n": n,
                    "radius": radius,
                    "repeat": repeat + 1,
                    "graph_seed": graph_seed,
                    "edges": graph.number_of_edges(),
                    "components": nx.number_connected_components(graph),
                    "k_nearest": k_nearest,
                }
                for method_name in METHOD_NAMES:
                    method_data = run_data[method_name]
                    if method_name == "grid_collision":
                        row["grid_collision_pre_prune_size"] = method_data[
                            "pre_prune_size"
                        ]
                    row[f"{method_name}_size"] = method_data["size"]
                    row[f"{method_name}_time_seconds"] = method_data[
                        "time_seconds"
                    ]
                    row[f"{method_name}_valid"] = method_data["valid"]

                row["smallest_valid_method"] = _winning_methods(run_data, "size")
                row["fastest_valid_method"] = _winning_methods(
                    run_data,
                    "time_seconds",
                )
                rows.append(row)

                sizes = " ".join(
                    f"{name}={run_data[name]['size']}"
                    for name in METHOD_NAMES
                )
                print(
                    f"n={n:4d} r={radius:.2f} repeat={repeat + 1}/{repeats} "
                    f"{sizes}"
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
