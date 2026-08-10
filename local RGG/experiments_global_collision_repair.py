"""Benchmark global repair of each collision-based resolving-set method.

The baseline CSV is authoritative for graph configurations and graph seeds. For
each baseline row, this script reconstructs the same graph, reruns the original
collision selector with the same family-specific seed used by
``experiments_all_collision_pairs.py``, and then globally repairs that exact
output. The baseline entropy measurements are copied alongside the rerun and
repair measurements for a three-way comparison. Baseline entropy timings are
historical measurements rather than same-session timings; the repaired wrapper
total is the reproduced collision-method time plus repair-only post-processing.
"""

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

from algorithms.circle_collision_method import get_metric_dimension_circle_collision
from algorithms.grid_collision_method import get_metric_dimension_grid_collision
from algorithms.ich_collision_method import get_metric_dimension_ich_collision
from algorithms.zoomed_square_collision_method import (
    get_metric_dimension_zoomed_square_collision,
)
from functions.global_collision_repair import repair_resolving_set_globally
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
    parser.add_argument(
        "--baseline-csv",
        type=Path,
        default=Path("all_collision_pairs_results.csv"),
        help=(
            "CSV produced by experiments_all_collision_pairs.py; its graph "
            "configurations, seeds, and entropy measurements are reused"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("global_collision_repair_results.csv"),
    )
    return parser.parse_args()


def _parse_bool(value):
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"cannot parse boolean value: {value!r}")


def _required_baseline_columns():
    columns = {
        "n",
        "radius",
        "repeat",
        "graph_seed",
        "k_nearest",
    }
    for family in FAMILIES:
        columns.update(
            {
                f"{family}_entropy_size",
                f"{family}_entropy_time_seconds",
                f"{family}_entropy_valid",
                f"{family}_collision_size",
                f"{family}_collision_valid",
            }
        )
    return columns


def load_baseline_rows(baseline_path):
    if not baseline_path.is_file():
        raise FileNotFoundError(f"baseline CSV not found: {baseline_path}")

    with baseline_path.open(newline="", encoding="utf-8-sig") as baseline_file:
        reader = csv.DictReader(baseline_file)
        fieldnames = set(reader.fieldnames or ())
        missing = sorted(_required_baseline_columns() - fieldnames)
        if missing:
            raise ValueError(
                "baseline CSV is missing required columns: " + ", ".join(missing)
            )
        rows = list(reader)

    if not rows:
        raise ValueError("baseline CSV contains no data rows")
    return rows


def _collision_method_functions(graph, radius, k_nearest):
    return {
        "grid": lambda: get_metric_dimension_grid_collision(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "circle": lambda: get_metric_dimension_circle_collision(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "zoomed": lambda: get_metric_dimension_zoomed_square_collision(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "ich": lambda: get_metric_dimension_ich_collision(graph),
    }


def _reset_random_state(run_seed):
    random.seed(run_seed)
    np.random.seed(run_seed % (2**32))


def _run_collision_method(method, run_seed):
    _reset_random_state(run_seed)
    captured_output = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(captured_output):
        result = method()
    return result, time.perf_counter() - start


def _run_global_repair(converted_graph, resolving_set, dist_matrix, run_seed):
    # The repair may invoke randomized Zobrist pruning. Resetting here makes the
    # repair stage reproducible and independent of how many random values the
    # original selector consumed.
    _reset_random_state(run_seed)
    start = time.perf_counter()
    repaired = repair_resolving_set_globally(
        converted_graph,
        resolving_set,
        dist_matrix,
    )
    return repaired, time.perf_counter() - start


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


def _validate_reconstructed_graph(baseline_row, graph_summary):
    integer_fields = ("edges", "components", "largest_component_size")
    for field in integer_fields:
        baseline_value = baseline_row.get(field, "")
        if baseline_value == "":
            continue
        if int(baseline_value) != graph_summary[field]:
            raise ValueError(
                f"reconstructed graph disagrees with baseline {field}: "
                f"{graph_summary[field]} != {baseline_value}"
            )


def _validate_repair_invariants(
    family,
    node_count,
    original_set,
    repair,
    repaired_set,
    repaired_valid,
):
    repair_count = len(repair.repair_probes)
    expected_pre_prune_size = len(original_set) + repair_count

    if repair.original_size != len(original_set):
        raise RuntimeError(
            f"{family} repair reported original size {repair.original_size}, "
            f"expected {len(original_set)}"
        )
    if repair.repaired_pre_prune_size != expected_pre_prune_size:
        raise RuntimeError(
            f"{family} repaired pre-prune size "
            f"{repair.repaired_pre_prune_size}, expected "
            f"{expected_pre_prune_size}"
        )
    if len(repaired_set) > repair.repaired_pre_prune_size:
        raise RuntimeError(
            f"{family} repaired final size exceeds its pre-prune size"
        )
    if repair.pruned_after_repair != (
        repair.repaired_pre_prune_size - len(repaired_set)
    ):
        raise RuntimeError(
            f"{family} post-repair prune count is inconsistent with sizes"
        )
    if node_count > 1 and (repair_count > 0) != (
        repair.collision_pairs_before > 0
    ):
        raise RuntimeError(
            f"{family} repair-probe count disagrees with collisions before repair"
        )
    if repair_count == 0 and (
        repaired_set != original_set
        or repair.repaired_pre_prune_size != len(original_set)
        or repair.pruned_after_repair != 0
    ):
        raise RuntimeError(
            f"{family} changed a set that required no global repair"
        )
    if repair.collision_pairs_after != 0:
        raise RuntimeError(
            f"{family} repair left {repair.collision_pairs_after} collision pairs"
        )
    if not repaired_valid:
        raise RuntimeError(f"{family} global repair did not produce a resolving set")


def run_benchmark(baseline_rows):
    rows = []
    total_rows = len(baseline_rows)

    for row_index, baseline in enumerate(baseline_rows, start=1):
        n = int(baseline["n"])
        radius = float(baseline["radius"])
        repeat = int(baseline["repeat"])
        graph_seed = int(baseline["graph_seed"])
        k_nearest = int(baseline["k_nearest"])

        graph = nx.random_geometric_graph(n, radius, seed=graph_seed)
        converted = ig.Graph.from_networkx(graph)
        dist_matrix = converted.distances()
        graph_summary = _graph_summary(graph)
        _validate_reconstructed_graph(baseline, graph_summary)
        methods = _collision_method_functions(graph, radius, k_nearest)

        family_order = list(FAMILIES)
        shift = (repeat - 1) % len(family_order)
        family_order = family_order[shift:] + family_order[:shift]
        run_data = {}

        for family in family_order:
            pair_seed = (graph_seed ^ PAIR_SEED_MASKS[family]) % (2**32)
            original, original_time = _run_collision_method(
                methods[family],
                pair_seed,
            )
            original_set = set(original.resolving_set)
            original_valid = checkIfResolvingSet_igraph(
                converted,
                original_set,
                dist_matrix,
            )

            repair, repair_time = _run_global_repair(
                converted,
                original_set,
                dist_matrix,
                pair_seed,
            )
            repaired_set = set(repair.resolving_set)
            repaired_valid = checkIfResolvingSet_igraph(
                converted,
                repaired_set,
                dist_matrix,
            )

            _validate_repair_invariants(
                family,
                n,
                original_set,
                repair,
                repaired_set,
                repaired_valid,
            )

            baseline_collision_size = int(
                baseline[f"{family}_collision_size"]
            )
            baseline_collision_valid = _parse_bool(
                baseline[f"{family}_collision_valid"]
            )
            reproduced_size_matches = (
                len(original_set) == baseline_collision_size
            )
            reproduced_valid_matches = (
                original_valid == baseline_collision_valid
            )
            if not reproduced_size_matches or not reproduced_valid_matches:
                raise RuntimeError(
                    f"{family} collision rerun did not reproduce baseline for "
                    f"n={n}, radius={radius}, repeat={repeat}: "
                    f"size {len(original_set)} vs {baseline_collision_size}, "
                    f"valid {original_valid} vs {baseline_collision_valid}"
                )

            run_data[family] = {
                "entropy_size": int(baseline[f"{family}_entropy_size"]),
                "entropy_time_seconds": float(
                    baseline[f"{family}_entropy_time_seconds"]
                ),
                "entropy_valid": _parse_bool(
                    baseline[f"{family}_entropy_valid"]
                ),
                "baseline_collision_size": baseline_collision_size,
                "baseline_collision_valid": baseline_collision_valid,
                "original_collision_pre_prune_size": original.pre_prune_size,
                "original_collision_size": len(original_set),
                "original_collision_time_seconds": original_time,
                "original_collision_valid": original_valid,
                "reproduced_size_matches_baseline": reproduced_size_matches,
                "reproduced_valid_matches_baseline": reproduced_valid_matches,
                "collisions_before_repair": repair.collision_pairs_before,
                "repair_probe_count": len(repair.repair_probes),
                "repair_probe_list": ",".join(map(str, repair.repair_probes)),
                "repair_only_time_seconds": repair_time,
                "repaired_pre_prune_size": repair.repaired_pre_prune_size,
                "repaired_size": len(repaired_set),
                "repaired_postprocessing_wrapper_total_time_seconds": (
                    original_time + repair_time
                ),
                "repaired_valid": repaired_valid,
                "collision_pairs_after_repair": repair.collision_pairs_after,
                "pruned_after_repair": repair.pruned_after_repair,
                "final_size_change": len(repaired_set) - len(original_set),
            }

        output_row = {
            "n": n,
            "radius": radius,
            "repeat": repeat,
            "graph_seed": graph_seed,
            **graph_summary,
            "k_nearest": k_nearest,
            "family_execution_order": ",".join(family_order),
            "baseline_entropy_timing_note": (
                "historical baseline; not timed in this repair session"
            ),
        }
        for family in FAMILIES:
            for metric, value in run_data[family].items():
                output_row[f"{family}_{metric}"] = value
        rows.append(output_row)

        repair_counts = " ".join(
            f"{family}=+{run_data[family]['repair_probe_count']}"
            for family in FAMILIES
        )
        print(
            f"[{row_index:02d}/{total_rows:02d}] n={n:4d} r={radius:.2f} "
            f"repeat={repeat} repairs {repair_counts}"
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
    baseline_rows = load_baseline_rows(args.baseline_csv)
    rows = run_benchmark(baseline_rows)
    write_results(rows, args.output)
    print(f"Wrote {len(rows)} repaired graph runs to {args.output}")


if __name__ == "__main__":
    main()
