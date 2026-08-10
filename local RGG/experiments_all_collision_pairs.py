"""Paired entropy-versus-collision benchmark for every project method."""

import argparse
import contextlib
import csv
import io
import math
from pathlib import Path
import random
import time

import igraph as ig
import networkx as nx
import numpy as np

from algorithms.circle_collision_method import (
    get_metric_dimension_circle_collision,
    get_metric_dimension_circle_entropy_experimental,
)
from algorithms.grid_collision_method import (
    get_metric_dimension_grid_collision,
    get_metric_dimension_grid_entropy_experimental,
)
from algorithms.ich_collision_method import (
    get_metric_dimension_ich_collision,
    get_metric_dimension_ich_entropy_experimental,
)
from algorithms.zoomed_square_collision_method import (
    get_metric_dimension_zoomed_square_collision,
    get_metric_dimension_zoomed_square_entropy_experimental,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


FAMILIES = ("grid", "circle", "zoomed", "ich")
PAIR_SEED_MASKS = {
    "grid": 0x9E3779B9,
    "circle": 0x85EBCA6B,
    "zoomed": 0xC2B2AE35,
    "ich": 0x27D4EB2F,
}


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", nargs="+", type=int, default=[50, 100, 200, 500])
    parser.add_argument("--r-values", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("all_collision_pairs_results.csv"),
    )
    return parser.parse_args()


def _method_functions(graph, radius, k_nearest):
    return {
        "grid": {
            "entropy": lambda: get_metric_dimension_grid_entropy_experimental(
                graph,
                radius,
                k_nearest=k_nearest,
            ),
            "collision": lambda: get_metric_dimension_grid_collision(
                graph,
                radius,
                k_nearest=k_nearest,
            ),
        },
        "circle": {
            "entropy": lambda: get_metric_dimension_circle_entropy_experimental(
                graph,
                radius,
                k_nearest=k_nearest,
            ),
            "collision": lambda: get_metric_dimension_circle_collision(
                graph,
                radius,
                k_nearest=k_nearest,
            ),
        },
        "zoomed": {
            "entropy": lambda: (
                get_metric_dimension_zoomed_square_entropy_experimental(
                    graph,
                    radius,
                    k_nearest=k_nearest,
                )
            ),
            "collision": lambda: get_metric_dimension_zoomed_square_collision(
                graph,
                radius,
                k_nearest=k_nearest,
            ),
        },
        "ich": {
            "entropy": lambda: get_metric_dimension_ich_entropy_experimental(
                graph
            ),
            "collision": lambda: get_metric_dimension_ich_collision(graph),
        },
    }


def _run_method(method, run_seed):
    random.seed(run_seed)
    np.random.seed(run_seed % (2**32))
    captured_output = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(captured_output):
        result = method()
    elapsed = time.perf_counter() - start
    return result, elapsed


def _size_winner(entropy, collision):
    if entropy["valid"] and not collision["valid"]:
        return "entropy"
    if collision["valid"] and not entropy["valid"]:
        return "collision"
    if not entropy["valid"] and not collision["valid"]:
        return "neither"
    if entropy["size"] < collision["size"]:
        return "entropy"
    if collision["size"] < entropy["size"]:
        return "collision"
    return "tie"


def _outlier_type(entropy, collision):
    threshold = max(10, math.ceil(0.25 * entropy["size"]))
    unusually_large = collision["size"] - entropy["size"] >= threshold
    if unusually_large and not collision["valid"]:
        return "large_and_invalid"
    if unusually_large:
        return "large_but_valid"
    if entropy["valid"] and not collision["valid"]:
        return "validity_regression"
    return "none"


def _graph_summary(graph):
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    components = list(nx.connected_components(graph))
    possible_edges = node_count * (node_count - 1) / 2
    return {
        "edges": edge_count,
        "components": len(components),
        "largest_component_size": max(map(len, components), default=0),
        "average_degree": (
            (2 * edge_count / node_count) if node_count else 0.0
        ),
        "edge_density": (edge_count / possible_edges) if possible_edges else 0.0,
    }


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
                converted = ig.Graph.from_networkx(graph)
                dist_matrix = converted.distances()
                graph_summary = _graph_summary(graph)
                method_functions = _method_functions(graph, radius, k_nearest)
                run_data = {}
                execution_order = []

                family_order = list(FAMILIES)
                shift = repeat % len(family_order)
                family_order = family_order[shift:] + family_order[:shift]

                for family in family_order:
                    pair_seed = (graph_seed ^ PAIR_SEED_MASKS[family]) % (2**32)
                    strategies = ["entropy", "collision"]
                    if repeat % 2:
                        strategies.reverse()

                    for strategy in strategies:
                        execution_order.append(f"{family}_{strategy}")
                        result, elapsed = _run_method(
                            method_functions[family][strategy],
                            pair_seed,
                        )
                        resolving_set = set(result.resolving_set)
                        run_data[(family, strategy)] = {
                            "pre_prune_size": result.pre_prune_size,
                            "size": len(resolving_set),
                            "time_seconds": elapsed,
                            "valid": checkIfResolvingSet_igraph(
                                converted,
                                resolving_set,
                                dist_matrix,
                            ),
                        }

                row = {
                    "n": n,
                    "radius": radius,
                    "repeat": repeat + 1,
                    "graph_seed": graph_seed,
                    **graph_summary,
                    "k_nearest": k_nearest,
                    "execution_order": ",".join(execution_order),
                }

                for family in FAMILIES:
                    entropy = run_data[(family, "entropy")]
                    collision = run_data[(family, "collision")]
                    for strategy, method_data in (
                        ("entropy", entropy),
                        ("collision", collision),
                    ):
                        prefix = f"{family}_{strategy}"
                        row[f"{prefix}_pre_prune_size"] = method_data[
                            "pre_prune_size"
                        ]
                        row[f"{prefix}_size"] = method_data["size"]
                        row[f"{prefix}_time_seconds"] = method_data[
                            "time_seconds"
                        ]
                        row[f"{prefix}_valid"] = method_data["valid"]

                    row[f"{family}_both_valid"] = (
                        entropy["valid"] and collision["valid"]
                    )
                    row[f"{family}_size_difference_collision_minus_entropy"] = (
                        collision["size"] - entropy["size"]
                    )
                    row[f"{family}_pre_prune_difference_collision_minus_entropy"] = (
                        collision["pre_prune_size"]
                        - entropy["pre_prune_size"]
                    )
                    row[f"{family}_time_difference_collision_minus_entropy"] = (
                        collision["time_seconds"] - entropy["time_seconds"]
                    )
                    row[f"{family}_collision_entropy_size_ratio"] = (
                        collision["size"] / entropy["size"]
                        if entropy["size"]
                        else 0.0
                    )
                    row[f"{family}_entropy_pruned_count"] = (
                        entropy["pre_prune_size"] - entropy["size"]
                    )
                    row[f"{family}_collision_pruned_count"] = (
                        collision["pre_prune_size"] - collision["size"]
                    )
                    row[f"{family}_size_winner"] = _size_winner(
                        entropy,
                        collision,
                    )
                    row[f"{family}_faster_method"] = (
                        "collision"
                        if collision["time_seconds"] < entropy["time_seconds"]
                        else "entropy"
                        if entropy["time_seconds"] < collision["time_seconds"]
                        else "tie"
                    )
                    row[f"{family}_outlier_type"] = _outlier_type(
                        entropy,
                        collision,
                    )

                rows.append(row)
                sizes = " ".join(
                    f"{family}:e={run_data[(family, 'entropy')]['size']}"
                    f"/c={run_data[(family, 'collision')]['size']}"
                    for family in FAMILIES
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
    print(f"Wrote {len(rows)} paired graph runs to {args.output}")


if __name__ == "__main__":
    main()
