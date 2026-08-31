"""Final paired benchmark of entropy and collision scoring for every family.

This experiment is designed as a controlled comparison of the scoring rule.
For each graph and method family, the entropy and collision selectors receive
the same graph and random seed.  Both raw outputs then receive the same global
collision-repair post-processing, so the final size comparison does not give
either scoring rule a different validity safety net.

Every repaired output also receives one explicit, identically seeded
redundancy-pruning pass.  Final cross-family comparisons therefore use sets
that have all received the same post-processing, including methods whose raw
outputs were already valid and did not need global repair.

The two pipelines are timed in the same process and their execution order is
reversed on alternating repeats.  Shared graph conversion and distance-matrix
construction are measured separately and excluded from both paired timings.
"""

import argparse
import contextlib
import csv
import hashlib
import io
import math
from pathlib import Path
import random
import statistics
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
from functions.global_collision_repair import repair_resolving_set_globally
from functions.resolving_functions import checkIfResolvingSet_igraph
from functions.zobrist_functions import prune_resolving_set_zobrist_fast


EXPERIMENT_VERSION = "final-paired-v2"
FAMILIES = ("grid", "circle", "zoomed", "ich")
STRATEGIES = ("entropy", "collision")
PAIR_SEED_MASKS = {
    "grid": 0x9E3779B9,
    "circle": 0x85EBCA6B,
    "zoomed": 0xC2B2AE35,
    "ich": 0x27D4EB2F,
}


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n-values",
        nargs="+",
        type=int,
        default=[50, 100, 200, 500],
    )
    parser.add_argument(
        "--r-values",
        nargs="+",
        type=float,
        default=[0.1, 0.3, 0.5, 0.7],
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="independent graph repeats for every (n, radius) configuration",
    )
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260819)
    parser.add_argument(
        "--verify-reproducibility",
        action="store_true",
        help=(
            "rerun every pipeline and require identical sets and repair "
            "diagnostics; approximately doubles algorithm runtime"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("final_entropy_collision_results.csv"),
    )
    return parser.parse_args()


def _validate_configuration(n_values, r_values, repeats, k_nearest):
    if not n_values:
        raise ValueError("n_values must contain at least one value")
    if not r_values:
        raise ValueError("r_values must contain at least one value")
    if len(set(n_values)) != len(n_values):
        raise ValueError("n_values must not contain duplicates")
    if len(set(r_values)) != len(r_values):
        raise ValueError("r_values must not contain duplicates")
    if any(n < 2 for n in n_values):
        raise ValueError("every n value must be at least 2")
    if any(not math.isfinite(radius) or radius <= 0 for radius in r_values):
        raise ValueError("every radius must be finite and positive")
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if k_nearest < 2:
        raise ValueError(
            "k_nearest must be at least 2 to compare candidate scoring rules"
        )


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


def _reset_random_state(run_seed):
    random.seed(run_seed)
    np.random.seed(run_seed % (2**32))


def _normalized_set(values):
    return {int(value) for value in values}


def _set_fingerprint(values):
    payload = ",".join(map(str, sorted(values))).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _run_final_pipeline(
    method,
    pair_seed,
    converted_graph,
    dist_matrix,
    family,
    strategy,
):
    # Both selectors start from exactly the same family-specific random state.
    _reset_random_state(pair_seed)
    captured_output = io.StringIO()
    selection_start = time.perf_counter()
    with contextlib.redirect_stdout(captured_output):
        original = method()
    selection_time = time.perf_counter() - selection_start

    original_set = _normalized_set(original.resolving_set)
    original_valid = checkIfResolvingSet_igraph(
        converted_graph,
        original_set,
        dist_matrix,
    )

    # Repair also starts from the same state for both strategies.  This makes
    # randomized Zobrist pruning independent of how much randomness a selector
    # happened to consume internally.
    _reset_random_state(pair_seed)
    repair_start = time.perf_counter()
    repair = repair_resolving_set_globally(
        converted_graph,
        original_set,
        dist_matrix,
    )
    repair_time = time.perf_counter() - repair_start

    repaired_set = _normalized_set(repair.resolving_set)
    repaired_valid = checkIfResolvingSet_igraph(
        converted_graph,
        repaired_set,
        dist_matrix,
    )
    _validate_pipeline_invariants(
        family=family,
        strategy=strategy,
        node_count=converted_graph.vcount(),
        original=original,
        original_set=original_set,
        original_valid=original_valid,
        repair=repair,
        repaired_set=repaired_set,
        repaired_valid=repaired_valid,
    )

    # Every family and strategy receives this identical final redundancy pass.
    # In particular, this prevents a naturally valid ICH set from skipping the
    # pruning that a locally invalid Grid set receives inside global repair.
    _reset_random_state(pair_seed)
    common_prune_start = time.perf_counter()
    common_prune_candidate = _normalized_set(
        prune_resolving_set_zobrist_fast(
            converted_graph,
            repaired_set,
            dist_matrix,
        )
    )
    common_prune_candidate_valid = checkIfResolvingSet_igraph(
        converted_graph,
        common_prune_candidate,
        dist_matrix,
    )
    common_prune_reverted = not common_prune_candidate_valid
    if common_prune_reverted:
        final_set = repaired_set
        final_valid = repaired_valid
    else:
        final_set = common_prune_candidate
        final_valid = common_prune_candidate_valid
    common_prune_time = time.perf_counter() - common_prune_start

    _validate_common_prune_invariants(
        family=family,
        strategy=strategy,
        repaired_set=repaired_set,
        repaired_valid=repaired_valid,
        common_prune_candidate=common_prune_candidate,
        common_prune_candidate_valid=common_prune_candidate_valid,
        common_prune_reverted=common_prune_reverted,
        final_set=final_set,
        final_valid=final_valid,
    )

    return {
        "original_pre_prune_size": original.pre_prune_size,
        "original_size": len(original_set),
        "original_time_seconds": selection_time,
        "original_valid": original_valid,
        "original_set_fingerprint": _set_fingerprint(original_set),
        "collisions_before_repair": repair.collision_pairs_before,
        "repair_probe_count": len(repair.repair_probes),
        "repair_probe_list": ",".join(map(str, repair.repair_probes)),
        "repair_time_seconds": repair_time,
        "repaired_pre_prune_size": repair.repaired_pre_prune_size,
        "pruned_after_repair": repair.pruned_after_repair,
        "collision_pairs_after_repair": repair.collision_pairs_after,
        "repaired_size": len(repaired_set),
        "repaired_total_time_seconds": selection_time + repair_time,
        "repaired_valid": repaired_valid,
        "repaired_set_fingerprint": _set_fingerprint(repaired_set),
        "repaired_size_change_from_original": len(repaired_set)
        - len(original_set),
        "common_prune_input_size": len(repaired_set),
        "common_pruned_count": len(repaired_set) - len(final_set),
        "common_prune_time_seconds": common_prune_time,
        "common_prune_reverted_for_exact_validity": common_prune_reverted,
        "final_size": len(final_set),
        "final_total_time_seconds": (
            selection_time + repair_time + common_prune_time
        ),
        "final_valid": final_valid,
        "final_set_fingerprint": _set_fingerprint(final_set),
        "final_size_change_from_original": len(final_set) - len(original_set),
        "captured_stdout_characters": len(captured_output.getvalue()),
        "_original_set": original_set,
        "_repaired_set": repaired_set,
        "_final_set": final_set,
        "_repair_probes": tuple(repair.repair_probes),
    }


def _validate_pipeline_invariants(
    family,
    strategy,
    node_count,
    original,
    original_set,
    original_valid,
    repair,
    repaired_set,
    repaired_valid,
):
    label = f"{family}/{strategy}"
    valid_ids = set(range(node_count))
    if not original_set <= valid_ids:
        raise RuntimeError(f"{label} produced an invalid original vertex ID")
    if not repaired_set <= valid_ids:
        raise RuntimeError(f"{label} produced an invalid repaired vertex ID")
    if original.pre_prune_size < len(original_set):
        raise RuntimeError(f"{label} original final size exceeds pre-prune size")
    if repair.original_size != len(original_set):
        raise RuntimeError(f"{label} repair original-size diagnostic is wrong")

    repair_count = len(repair.repair_probes)
    expected_repaired_pre_prune = len(original_set) + repair_count
    if repair.repaired_pre_prune_size != expected_repaired_pre_prune:
        raise RuntimeError(f"{label} repaired pre-prune size is inconsistent")
    if repair.pruned_after_repair != (
        repair.repaired_pre_prune_size - len(repaired_set)
    ):
        raise RuntimeError(f"{label} repaired prune count is inconsistent")
    if repair.collision_pairs_after != 0:
        raise RuntimeError(f"{label} repair left global collision pairs")
    if not repaired_valid:
        raise RuntimeError(f"{label} repair did not produce a resolving set")

    convention_valid_before = (
        repair.collision_pairs_before == 0 and bool(original_set)
    )
    if original_valid != convention_valid_before:
        raise RuntimeError(
            f"{label} exact validity and collision diagnostics disagree"
        )
    if original_valid:
        if repair_count != 0 or repaired_set != original_set:
            raise RuntimeError(f"{label} changed an already-valid set")
        if repair.pruned_after_repair != 0:
            raise RuntimeError(f"{label} pruned an already-valid set")
    elif repair_count == 0:
        raise RuntimeError(f"{label} invalid set received no repair probe")


def _validate_common_prune_invariants(
    family,
    strategy,
    repaired_set,
    repaired_valid,
    common_prune_candidate,
    common_prune_candidate_valid,
    common_prune_reverted,
    final_set,
    final_valid,
):
    label = f"{family}/{strategy}"
    if not repaired_valid:
        raise RuntimeError(f"{label} common prune received an invalid set")
    if not common_prune_candidate <= repaired_set:
        raise RuntimeError(f"{label} common prune added a vertex")
    if common_prune_reverted != (not common_prune_candidate_valid):
        raise RuntimeError(f"{label} common-prune revert flag is inconsistent")
    if common_prune_reverted:
        if final_set != repaired_set:
            raise RuntimeError(
                f"{label} did not restore the exact safe pre-prune set"
            )
    elif final_set != common_prune_candidate:
        raise RuntimeError(f"{label} discarded a valid common-prune result")
    if len(final_set) > len(repaired_set):
        raise RuntimeError(f"{label} final set grew during common pruning")
    if not final_valid:
        raise RuntimeError(f"{label} common final set is not resolving")


def _assert_reproduced(first, second, family, strategy):
    exact_fields = (
        "original_pre_prune_size",
        "original_size",
        "original_valid",
        "original_set_fingerprint",
        "collisions_before_repair",
        "repair_probe_count",
        "repair_probe_list",
        "repaired_pre_prune_size",
        "pruned_after_repair",
        "collision_pairs_after_repair",
        "repaired_size",
        "repaired_valid",
        "repaired_set_fingerprint",
        "repaired_size_change_from_original",
        "common_prune_input_size",
        "common_pruned_count",
        "common_prune_reverted_for_exact_validity",
        "final_size",
        "final_valid",
        "final_set_fingerprint",
        "final_size_change_from_original",
    )
    disagreements = [
        field for field in exact_fields if first[field] != second[field]
    ]
    if disagreements:
        raise RuntimeError(
            f"{family}/{strategy} failed seeded reproducibility check: "
            + ", ".join(disagreements)
        )


def _graph_fingerprint(graph):
    digest = hashlib.sha256()
    for node in sorted(graph.nodes()):
        x_position, y_position = graph.nodes[node]["pos"]
        digest.update(
            f"v:{node}:{x_position:.17g}:{y_position:.17g}\n".encode("ascii")
        )
    for source, target in sorted(
        (min(source, target), max(source, target))
        for source, target in graph.edges()
    ):
        digest.update(f"e:{source}:{target}\n".encode("ascii"))
    return digest.hexdigest()


def _graph_summary(graph):
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    components = list(nx.connected_components(graph))
    degrees = [degree for _, degree in graph.degree()]
    possible_edges = node_count * (node_count - 1) / 2
    return {
        "edge_count": edge_count,
        "component_count": len(components),
        "largest_component_size": max(map(len, components), default=0),
        "connected": len(components) == 1,
        "isolated_node_count": sum(degree == 0 for degree in degrees),
        "average_degree": statistics.fmean(degrees) if degrees else 0.0,
        "degree_population_stddev": (
            statistics.pstdev(degrees) if len(degrees) > 1 else 0.0
        ),
        "minimum_degree": min(degrees, default=0),
        "maximum_degree": max(degrees, default=0),
        "edge_density": (edge_count / possible_edges) if possible_edges else 0.0,
    }


def _prepare_graph(n, radius, graph_seed):
    generation_start = time.perf_counter()
    graph = nx.random_geometric_graph(n, radius, seed=graph_seed)
    graph_generation_time = time.perf_counter() - generation_start

    fingerprint = _graph_fingerprint(graph)
    reproduced = nx.random_geometric_graph(n, radius, seed=graph_seed)
    if _graph_fingerprint(reproduced) != fingerprint:
        raise RuntimeError("graph generation failed its seeded reproducibility check")

    preprocessing_start = time.perf_counter()
    converted = ig.Graph.from_networkx(graph)
    if converted.vcount() != n:
        raise RuntimeError("NetworkX-to-igraph conversion changed node count")
    if "_nx_name" in converted.vs.attributes():
        if list(converted.vs["_nx_name"]) != list(range(n)):
            raise RuntimeError(
                "igraph vertex indices do not match NetworkX integer node IDs"
            )
    dist_matrix = converted.distances()
    preprocessing_time = time.perf_counter() - preprocessing_start

    return {
        "graph": graph,
        "converted": converted,
        "dist_matrix": dist_matrix,
        "fingerprint": fingerprint,
        "generation_time_seconds": graph_generation_time,
        "shared_preprocessing_time_seconds": preprocessing_time,
        "summary": _graph_summary(graph),
    }


def _size_winner(entropy, collision, stage="final"):
    if stage not in {"original", "repaired", "final"}:
        raise ValueError(f"unknown comparison stage: {stage}")
    prefix = stage
    entropy_valid = entropy[f"{prefix}_valid"]
    collision_valid = collision[f"{prefix}_valid"]
    if entropy_valid and not collision_valid:
        return "entropy"
    if collision_valid and not entropy_valid:
        return "collision"
    if not entropy_valid and not collision_valid:
        return "neither"
    entropy_size = entropy[f"{prefix}_size"]
    collision_size = collision[f"{prefix}_size"]
    if entropy_size < collision_size:
        return "entropy"
    if collision_size < entropy_size:
        return "collision"
    return "tie"


def _pareto_result(entropy, collision):
    entropy_size = entropy["final_size"]
    collision_size = collision["final_size"]
    entropy_time = entropy["final_total_time_seconds"]
    collision_time = collision["final_total_time_seconds"]
    if (
        entropy_size <= collision_size
        and entropy_time <= collision_time
        and (entropy_size < collision_size or entropy_time < collision_time)
    ):
        return "entropy_dominates"
    if (
        collision_size <= entropy_size
        and collision_time <= entropy_time
        and (collision_size < entropy_size or collision_time < entropy_time)
    ):
        return "collision_dominates"
    if entropy_size == collision_size and entropy_time == collision_time:
        return "exact_tie"
    return "tradeoff"


def _large_size_gap_flag(entropy_size, collision_size):
    threshold = max(10, math.ceil(0.25 * min(entropy_size, collision_size)))
    difference = collision_size - entropy_size
    if difference >= threshold:
        return "collision_much_larger"
    if difference <= -threshold:
        return "entropy_much_larger"
    return "none"


def _large_time_gap_flag(entropy_time, collision_time):
    if entropy_time <= 0 or collision_time <= 0:
        return "not_comparable"
    ratio = collision_time / entropy_time
    if ratio >= 2:
        return "collision_at_least_2x_slower"
    if ratio <= 0.5:
        return "collision_at_least_2x_faster"
    return "none"


def _repair_need_comparison(entropy, collision):
    entropy_needed = entropy["repair_probe_count"] > 0
    collision_needed = collision["repair_probe_count"] > 0
    if entropy_needed and collision_needed:
        return "both"
    if entropy_needed:
        return "entropy_only"
    if collision_needed:
        return "collision_only"
    return "neither"


def _raw_validity_comparison(entropy, collision):
    if entropy["original_valid"] and collision["original_valid"]:
        return "both_valid"
    if entropy["original_valid"]:
        return "entropy_only_valid"
    if collision["original_valid"]:
        return "collision_only_valid"
    return "neither_valid"


def _public_pipeline_data(pipeline):
    return {
        key: value for key, value in pipeline.items() if not key.startswith("_")
    }


def _paired_metrics(entropy, collision):
    entropy_time = entropy["final_total_time_seconds"]
    collision_time = collision["final_total_time_seconds"]
    entropy_size = entropy["final_size"]
    collision_size = collision["final_size"]
    return {
        "both_original_valid": (
            entropy["original_valid"] and collision["original_valid"]
        ),
        "both_repaired_valid": (
            entropy["repaired_valid"] and collision["repaired_valid"]
        ),
        "both_final_valid": entropy["final_valid"] and collision["final_valid"],
        "original_size_winner": _size_winner(
            entropy,
            collision,
            stage="original",
        ),
        "final_size_difference_collision_minus_entropy": (
            collision_size - entropy_size
        ),
        "final_time_difference_collision_minus_entropy_seconds": (
            collision_time - entropy_time
        ),
        "collision_to_entropy_final_size_ratio": (
            collision_size / entropy_size if entropy_size else 0.0
        ),
        "collision_to_entropy_final_time_ratio": (
            collision_time / entropy_time if entropy_time else 0.0
        ),
        "collision_final_speedup_factor_vs_entropy": (
            entropy_time / collision_time if collision_time else 0.0
        ),
        "final_size_winner": _size_winner(entropy, collision),
        "final_faster_method": (
            "collision"
            if collision_time < entropy_time
            else "entropy"
            if entropy_time < collision_time
            else "tie"
        ),
        "final_pareto_result": _pareto_result(entropy, collision),
        "repair_need_comparison": _repair_need_comparison(
            entropy,
            collision,
        ),
        "raw_validity_comparison": _raw_validity_comparison(
            entropy,
            collision,
        ),
        "large_final_size_gap_flag": _large_size_gap_flag(
            entropy_size,
            collision_size,
        ),
        "large_final_time_gap_flag": _large_time_gap_flag(
            entropy_time,
            collision_time,
        ),
    }


def run_benchmark(
    n_values,
    r_values,
    repeats,
    k_nearest,
    seed,
    verify_reproducibility=False,
):
    _validate_configuration(n_values, r_values, repeats, k_nearest)
    seed_generator = random.Random(seed)
    used_graph_seeds = set()
    rows = []
    graph_sequence = 0
    configuration_sequence = 0
    total_graphs = len(n_values) * len(r_values) * repeats

    for n in n_values:
        for radius in r_values:
            configuration_sequence += 1
            for repeat_index in range(repeats):
                graph_sequence += 1
                graph_seed = seed_generator.randrange(2**32)
                while graph_seed in used_graph_seeds:
                    graph_seed = seed_generator.randrange(2**32)
                used_graph_seeds.add(graph_seed)

                prepared = _prepare_graph(n, radius, graph_seed)
                graph = prepared["graph"]
                converted = prepared["converted"]
                dist_matrix = prepared["dist_matrix"]
                methods = _method_functions(graph, radius, k_nearest)

                family_order = list(FAMILIES)
                family_shift = (
                    configuration_sequence - 1 + repeat_index
                ) % len(family_order)
                family_order = (
                    family_order[family_shift:] + family_order[:family_shift]
                )
                strategy_order = (
                    ("entropy", "collision")
                    if (configuration_sequence - 1 + repeat_index) % 2 == 0
                    else ("collision", "entropy")
                )
                graph_run_data = {}

                for family_position, family in enumerate(family_order, start=1):
                    pair_seed = (
                        graph_seed ^ PAIR_SEED_MASKS[family]
                    ) % (2**32)
                    family_data = {}

                    for strategy_position, strategy in enumerate(
                        strategy_order,
                        start=1,
                    ):
                        pipeline = _run_final_pipeline(
                            methods[family][strategy],
                            pair_seed,
                            converted,
                            dist_matrix,
                            family,
                            strategy,
                        )
                        if verify_reproducibility:
                            reproduced = _run_final_pipeline(
                                methods[family][strategy],
                                pair_seed,
                                converted,
                                dist_matrix,
                                family,
                                strategy,
                            )
                            _assert_reproduced(
                                pipeline,
                                reproduced,
                                family,
                                strategy,
                            )
                        pipeline["strategy_execution_position"] = strategy_position
                        family_data[strategy] = pipeline

                    entropy = family_data["entropy"]
                    collision = family_data["collision"]
                    paired = _paired_metrics(entropy, collision)
                    if not paired["both_final_valid"]:
                        raise RuntimeError(
                            f"{family} paired final outputs were not both valid"
                        )

                    row = {
                        "experiment_version": EXPERIMENT_VERSION,
                        "benchmark_seed": seed,
                        "configuration_sequence": configuration_sequence,
                        "graph_sequence": graph_sequence,
                        "graph_id": (
                            f"n{n}_r{radius:g}_repeat{repeat_index + 1}"
                        ),
                        "n": n,
                        "radius": radius,
                        "repeat": repeat_index + 1,
                        "graph_seed": graph_seed,
                        "graph_fingerprint_sha256": prepared["fingerprint"],
                        **prepared["summary"],
                        "graph_generation_time_seconds": prepared[
                            "generation_time_seconds"
                        ],
                        "shared_preprocessing_time_seconds": prepared[
                            "shared_preprocessing_time_seconds"
                        ],
                        "shared_preprocessing_excluded_from_paired_times": True,
                        "method_reproducibility_check_performed": (
                            verify_reproducibility
                        ),
                        "k_nearest": k_nearest,
                        "family": family,
                        "family_execution_position": family_position,
                        "family_execution_order": ",".join(family_order),
                        "pair_seed": pair_seed,
                        "repair_seed": pair_seed,
                        "strategy_execution_order": ",".join(strategy_order),
                    }
                    for strategy in STRATEGIES:
                        for metric, value in _public_pipeline_data(
                            family_data[strategy]
                        ).items():
                            row[f"{strategy}_{metric}"] = value
                    row.update(paired)
                    rows.append(row)
                    graph_run_data[family] = (entropy, collision)

                sizes = " ".join(
                    f"{family}:e={graph_run_data[family][0]['final_size']}"
                    f"/c={graph_run_data[family][1]['final_size']}"
                    for family in FAMILIES
                )
                print(
                    f"[{graph_sequence:03d}/{total_graphs:03d}] "
                    f"n={n:4d} r={radius:.2f} repeat={repeat_index + 1}/"
                    f"{repeats} {sizes}"
                )

    expected_rows = total_graphs * len(FAMILIES)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"benchmark produced {len(rows)} rows; expected {expected_rows}"
        )
    return rows


def write_results(rows, output_path):
    if not rows:
        raise ValueError("cannot write an empty benchmark")
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
        verify_reproducibility=args.verify_reproducibility,
    )
    write_results(rows, args.output)
    print(f"Wrote {len(rows)} paired family results to {args.output}")


if __name__ == "__main__":
    main()
