"""Focused pilot comparing three Collision selectors on clustered RGGs.

The experiment deliberately leaves the existing algorithms unchanged.  It
generates connected point clouds with five Gaussian hotspots in the unit
square, calibrates
the geometric radius to target *realized* average degree, and runs Grid,
Zoomed Square, and Circle Collision on the exact same graphs.

Every method output goes through the same global collision repair, seeded
redundancy prune, and exact validity checks used by the final Entropy versus
Collision benchmark.  Shared graph construction and validation preprocessing
are recorded separately from method runtime.
"""

import argparse
import csv
from dataclasses import dataclass
import hashlib
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
)
from algorithms.grid_collision_method import get_metric_dimension_grid_collision
from algorithms.zoomed_square_collision_method import (
    get_metric_dimension_zoomed_square_collision,
)
from experiments_final_entropy_collision import (
    _assert_reproduced,
    _graph_fingerprint,
    _graph_summary,
    _public_pipeline_data,
    _run_final_pipeline,
)


EXPERIMENT_VERSION = "clustered-collision-pilot-v1"
METHODS = ("grid", "zoomed", "circle")
DEFAULT_TARGET_AVERAGE_DEGREES = (15.0, 107.0, 240.0)
DEFAULT_CLUSTER_COUNT = 5
DEFAULT_CLUSTER_SIGMA = 0.12
DEFAULT_CENTER_MARGIN = 0.15
DEFAULT_MINIMUM_CENTER_SEPARATION = 0.20
DEFAULT_UNIFORM_BACKGROUND_FRACTION = 0.60
RUN_SEED_MASK = 0xD1B54A32
RESULT_COLUMNS = (
    "Cloud",
    "Density (avg degree)",
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


@dataclass(frozen=True)
class ClusteredPointCloud:
    position_seed: int
    positions: dict
    centers: tuple
    cluster_assignments: tuple
    cluster_sizes: tuple
    rejected_clouds_before_acceptance: int


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument(
        "--target-average-degrees",
        nargs="+",
        type=float,
        default=list(DEFAULT_TARGET_AVERAGE_DEGREES),
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=6,
        help="independent accepted position clouds reused across all densities",
    )
    parser.add_argument("--k-nearest", type=int, default=5)
    parser.add_argument(
        "--cluster-count",
        type=int,
        default=DEFAULT_CLUSTER_COUNT,
    )
    parser.add_argument("--cluster-sigma", type=float, default=0.12)
    parser.add_argument(
        "--uniform-background-fraction",
        type=float,
        default=DEFAULT_UNIFORM_BACKGROUND_FRACTION,
    )
    parser.add_argument("--center-margin", type=float, default=0.15)
    parser.add_argument("--minimum-center-separation", type=float, default=0.20)
    parser.add_argument("--max-connectivity-attempts", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument(
        "--verify-reproducibility",
        action="store_true",
        help="rerun every method pipeline and compare exact set diagnostics",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/clustered_collision_pilot_results.csv"),
    )
    return parser.parse_args()


def _validate_configuration(
    n,
    target_average_degrees,
    repeats,
    k_nearest,
    cluster_count,
    cluster_sigma,
    uniform_background_fraction,
    center_margin,
    minimum_center_separation,
    max_connectivity_attempts,
):
    if n < 4:
        raise ValueError("n must be at least 4")
    if not target_average_degrees:
        raise ValueError("target_average_degrees must not be empty")
    if len(set(target_average_degrees)) != len(target_average_degrees):
        raise ValueError("target_average_degrees must not contain duplicates")
    if any(
        not math.isfinite(value) or value <= 0 or value >= n - 1
        for value in target_average_degrees
    ):
        raise ValueError("every target average degree must be in (0, n - 1)")
    target_edge_counts = [
        int(round(value * n / 2.0)) for value in target_average_degrees
    ]
    if len(set(target_edge_counts)) != len(target_edge_counts):
        raise ValueError(
            "target average degrees must imply distinct integer edge counts"
        )
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if k_nearest < 1:
        raise ValueError("k_nearest must be positive")
    if cluster_count < 2 or cluster_count > n:
        raise ValueError("cluster_count must be between 2 and n")
    if not math.isfinite(cluster_sigma) or cluster_sigma <= 0:
        raise ValueError("cluster_sigma must be finite and positive")
    if (
        not math.isfinite(uniform_background_fraction)
        or not 0 <= uniform_background_fraction < 1
    ):
        raise ValueError("uniform_background_fraction must be in [0, 1)")
    if n - int(round(n * uniform_background_fraction)) < cluster_count:
        raise ValueError("not enough hotspot points for the requested clusters")
    if not math.isfinite(center_margin) or not 0 <= center_margin < 0.5:
        raise ValueError("center_margin must be in [0, 0.5)")
    if (
        not math.isfinite(minimum_center_separation)
        or minimum_center_separation <= 0
    ):
        raise ValueError("minimum_center_separation must be positive")
    if max_connectivity_attempts < 1:
        raise ValueError("max_connectivity_attempts must be at least 1")


def _sample_cluster_centers(
    rng,
    cluster_count,
    center_margin,
    minimum_center_separation,
    max_draws=10000,
):
    centers = []
    for _ in range(max_draws):
        candidate = rng.uniform(
            center_margin,
            1.0 - center_margin,
            size=2,
        )
        if all(
            np.linalg.norm(candidate - existing)
            >= minimum_center_separation
            for existing in centers
        ):
            centers.append(candidate)
            if len(centers) == cluster_count:
                return np.asarray(centers, dtype=float)
    raise RuntimeError("could not sample sufficiently separated cluster centers")


def _sample_truncated_gaussian(rng, center, sigma):
    for _ in range(10000):
        candidate = center + rng.normal(0.0, sigma, size=2)
        if np.all((candidate >= 0.0) & (candidate <= 1.0)):
            return candidate
    raise RuntimeError("could not sample a cluster point inside the unit square")


def _sample_clustered_point_cloud(
    n,
    position_seed,
    cluster_count=DEFAULT_CLUSTER_COUNT,
    cluster_sigma=DEFAULT_CLUSTER_SIGMA,
    uniform_background_fraction=DEFAULT_UNIFORM_BACKGROUND_FRACTION,
    center_margin=DEFAULT_CENTER_MARGIN,
    minimum_center_separation=DEFAULT_MINIMUM_CENTER_SEPARATION,
    rejected_clouds_before_acceptance=0,
):
    rng = np.random.default_rng(position_seed)
    centers = _sample_cluster_centers(
        rng,
        cluster_count,
        center_margin,
        minimum_center_separation,
    )

    uniform_background_count = int(round(n * uniform_background_fraction))
    hotspot_point_count = n - uniform_background_count
    base_size, remainder = divmod(hotspot_point_count, cluster_count)
    cluster_sizes = tuple(
        base_size + (cluster_index < remainder)
        for cluster_index in range(cluster_count)
    )
    assignments = np.concatenate(
        [np.full(uniform_background_count, -1, dtype=int)]
        + [
            np.full(size, cluster_index, dtype=int)
            for cluster_index, size in enumerate(cluster_sizes)
        ]
    )
    rng.shuffle(assignments)

    coordinates = np.empty((n, 2), dtype=float)
    for node, cluster_index in enumerate(assignments):
        if cluster_index < 0:
            coordinates[node] = rng.random(2)
        else:
            coordinates[node] = _sample_truncated_gaussian(
                rng,
                centers[int(cluster_index)],
                cluster_sigma,
            )

    return ClusteredPointCloud(
        position_seed=int(position_seed),
        positions={
            node: (float(coordinates[node, 0]), float(coordinates[node, 1]))
            for node in range(n)
        },
        centers=tuple(
            (float(center[0]), float(center[1])) for center in centers
        ),
        cluster_assignments=tuple(map(int, assignments)),
        cluster_sizes=cluster_sizes,
        rejected_clouds_before_acceptance=rejected_clouds_before_acceptance,
    )


def _position_fingerprint(point_cloud):
    digest = hashlib.sha256()
    for cluster_index, center in enumerate(point_cloud.centers):
        digest.update(
            f"c:{cluster_index}:{center[0]:.17g}:{center[1]:.17g}\n".encode(
                "ascii"
            )
        )
    for node in range(len(point_cloud.positions)):
        x_position, y_position = point_cloud.positions[node]
        digest.update(
            f"v:{node}:{point_cloud.cluster_assignments[node]}:"
            f"{x_position:.17g}:{y_position:.17g}\n".encode("ascii")
        )
    return digest.hexdigest()


def _calibrated_geometric_graph(point_cloud, target_average_degree):
    n = len(point_cloud.positions)
    target_edge_count = int(round(target_average_degree * n / 2.0))
    possible_edges = n * (n - 1) // 2
    if not 1 <= target_edge_count <= possible_edges:
        raise ValueError("target average degree implies an invalid edge count")

    coordinates = np.asarray(
        [point_cloud.positions[node] for node in range(n)],
        dtype=float,
    )
    source_indices, target_indices = np.triu_indices(n, k=1)
    differences = coordinates[source_indices] - coordinates[target_indices]
    distances = np.sqrt(np.einsum("ij,ij->i", differences, differences))
    threshold_index = target_edge_count - 1
    if target_edge_count == possible_edges:
        radius = math.nextafter(float(np.max(distances)), math.inf)
    else:
        partitioned = np.partition(
            distances,
            (threshold_index, threshold_index + 1),
        )
        lower_distance = float(partitioned[threshold_index])
        upper_distance = float(partitioned[threshold_index + 1])
        if lower_distance == upper_distance:
            raise RuntimeError(
                "a pair-distance tie prevented exact average-degree calibration"
            )
        radius = (lower_distance + upper_distance) / 2.0
    selected = distances <= radius
    selected_edge_count = int(np.count_nonzero(selected))
    if selected_edge_count != target_edge_count:
        raise RuntimeError(
            "a pair-distance tie prevented exact average-degree calibration"
        )

    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(
        zip(
            map(int, source_indices[selected]),
            map(int, target_indices[selected]),
        )
    )
    nx.set_node_attributes(graph, point_cloud.positions, "pos")
    achieved_average_degree = 2.0 * graph.number_of_edges() / n
    return graph, radius, achieved_average_degree


def _method_functions(graph, radius, k_nearest):
    return {
        "grid": lambda: get_metric_dimension_grid_collision(
            graph,
            radius,
            k_nearest=k_nearest,
        ),
        "zoomed": lambda: get_metric_dimension_zoomed_square_collision(
            graph,
            radius,
            k_nearest=k_nearest,
            max_iters=1000,
        ),
        "circle": lambda: get_metric_dimension_circle_collision(
            graph,
            radius,
            k_nearest=k_nearest,
            max_iters=1000,
        ),
    }


def _rotated(values, shift):
    values = tuple(values)
    normalized_shift = shift % len(values)
    return values[normalized_shift:] + values[:normalized_shift]


def _density_label(density_index, density_count):
    if density_count == 3:
        return ("low", "medium", "high")[density_index]
    return f"level_{density_index + 1}_of_{density_count}"


def _cluster_metadata(
    point_cloud,
    cluster_sigma,
    uniform_background_fraction,
):
    centers = np.asarray(point_cloud.centers, dtype=float)
    coordinates = np.asarray(
        [
            point_cloud.positions[node]
            for node in range(len(point_cloud.positions))
        ],
        dtype=float,
    )
    center_distances = []
    for left in range(len(centers)):
        for right in range(left + 1, len(centers)):
            center_distances.append(
                float(np.linalg.norm(centers[left] - centers[right]))
            )

    radial_offsets = []
    boundary_count = 0
    for node, position in point_cloud.positions.items():
        coordinate = np.asarray(position, dtype=float)
        cluster_assignment = point_cloud.cluster_assignments[node]
        if cluster_assignment >= 0:
            radial_offsets.append(
                float(
                    np.linalg.norm(
                        coordinate - centers[cluster_assignment]
                    )
                )
            )
        if min(coordinate[0], coordinate[1], 1 - coordinate[0], 1 - coordinate[1]) <= 0.1:
            boundary_count += 1

    coordinate_differences = coordinates[:, np.newaxis, :] - coordinates[
        np.newaxis, :, :
    ]
    squared_distances = np.einsum(
        "ijk,ijk->ij",
        coordinate_differences,
        coordinate_differences,
    )
    np.fill_diagonal(squared_distances, np.inf)
    mean_nearest_neighbor_distance = float(
        np.mean(np.sqrt(np.min(squared_distances, axis=1)))
    )

    return {
        "cluster_count": len(point_cloud.centers),
        "cluster_sigma": cluster_sigma,
        "uniform_background_fraction": uniform_background_fraction,
        "uniform_background_count": sum(
            assignment < 0 for assignment in point_cloud.cluster_assignments
        ),
        "hotspot_point_fraction": 1.0 - uniform_background_fraction,
        "cluster_sizes": ",".join(map(str, point_cloud.cluster_sizes)),
        "cluster_centers": ";".join(
            f"{x_position:.8f},{y_position:.8f}"
            for x_position, y_position in point_cloud.centers
        ),
        "minimum_center_distance": min(center_distances),
        "mean_center_distance": statistics.fmean(center_distances),
        "maximum_center_distance": max(center_distances),
        "mean_point_distance_from_assigned_center": statistics.fmean(
            radial_offsets
        ),
        "mean_nearest_neighbor_distance": mean_nearest_neighbor_distance,
        "boundary_point_fraction_0_1": boundary_count
        / len(point_cloud.positions),
    }


def _prepare_graph(point_cloud, target_average_degree):
    generation_start = time.perf_counter()
    graph, radius, achieved_average_degree = _calibrated_geometric_graph(
        point_cloud,
        target_average_degree,
    )
    generation_time = time.perf_counter() - generation_start
    fingerprint = _graph_fingerprint(graph)

    preprocessing_start = time.perf_counter()
    converted = ig.Graph.from_networkx(graph)
    if converted.vcount() != graph.number_of_nodes():
        raise RuntimeError("NetworkX-to-igraph conversion changed node count")
    if "_nx_name" in converted.vs.attributes():
        if list(converted.vs["_nx_name"]) != list(range(graph.number_of_nodes())):
            raise RuntimeError(
                "igraph vertex indices do not match NetworkX integer node IDs"
            )
    dist_matrix = converted.distances()
    preprocessing_time = time.perf_counter() - preprocessing_start

    summary = _graph_summary(graph)
    if not summary["connected"]:
        raise RuntimeError("accepted clustered graph is unexpectedly disconnected")
    if abs(summary["average_degree"] - achieved_average_degree) > 1e-12:
        raise RuntimeError("average-degree calibration diagnostic is inconsistent")

    graph_distances = np.asarray(dist_matrix, dtype=float)
    upper_distances = graph_distances[np.triu_indices(converted.vcount(), k=1)]
    summary.update(
        {
            "degree_coefficient_of_variation": (
                summary["degree_population_stddev"] / summary["average_degree"]
                if summary["average_degree"]
                else 0.0
            ),
            "average_clustering_coefficient": nx.average_clustering(graph),
            "transitivity": nx.transitivity(graph),
            "graph_diameter": int(np.max(upper_distances)),
            "mean_graph_distance": float(np.mean(upper_distances)),
        }
    )
    return {
        "graph": graph,
        "converted": converted,
        "dist_matrix": dist_matrix,
        "radius": radius,
        "achieved_average_degree": achieved_average_degree,
        "fingerprint": fingerprint,
        "generation_time_seconds": generation_time,
        "shared_preprocessing_time_seconds": preprocessing_time,
        "summary": summary,
    }


def _find_connected_point_cloud(
    n,
    sparse_target_average_degree,
    seed_generator,
    used_position_seeds,
    cluster_count,
    cluster_sigma,
    uniform_background_fraction,
    center_margin,
    minimum_center_separation,
    max_connectivity_attempts,
):
    for attempt in range(1, max_connectivity_attempts + 1):
        position_seed = seed_generator.randrange(2**32)
        while position_seed in used_position_seeds:
            position_seed = seed_generator.randrange(2**32)
        used_position_seeds.add(position_seed)
        point_cloud = _sample_clustered_point_cloud(
            n=n,
            position_seed=position_seed,
            cluster_count=cluster_count,
            cluster_sigma=cluster_sigma,
            uniform_background_fraction=uniform_background_fraction,
            center_margin=center_margin,
            minimum_center_separation=minimum_center_separation,
            rejected_clouds_before_acceptance=attempt - 1,
        )
        sparse_graph, _, _ = _calibrated_geometric_graph(
            point_cloud,
            sparse_target_average_degree,
        )
        if not nx.is_connected(sparse_graph):
            continue

        reproduced = _sample_clustered_point_cloud(
            n=n,
            position_seed=position_seed,
            cluster_count=cluster_count,
            cluster_sigma=cluster_sigma,
            uniform_background_fraction=uniform_background_fraction,
            center_margin=center_margin,
            minimum_center_separation=minimum_center_separation,
            rejected_clouds_before_acceptance=attempt - 1,
        )
        if _position_fingerprint(reproduced) != _position_fingerprint(
            point_cloud
        ):
            raise RuntimeError("clustered point generation is not reproducible")
        reproduced_graph, _, _ = _calibrated_geometric_graph(
            reproduced,
            sparse_target_average_degree,
        )
        if _graph_fingerprint(reproduced_graph) != _graph_fingerprint(
            sparse_graph
        ):
            raise RuntimeError("clustered graph generation is not reproducible")
        return point_cloud

    raise RuntimeError(
        "could not generate a connected sparse clustered graph within "
        f"{max_connectivity_attempts} attempts"
    )


def _rank(value, all_values):
    return 1 + sum(candidate < value for candidate in all_values)


def _pareto_frontier(method, method_data):
    current = method_data[method]
    for competitor, candidate in method_data.items():
        if competitor == method:
            continue
        no_worse = (
            candidate["final_size"] <= current["final_size"]
            and candidate["final_total_time_seconds"]
            <= current["final_total_time_seconds"]
        )
        strictly_better = (
            candidate["final_size"] < current["final_size"]
            or candidate["final_total_time_seconds"]
            < current["final_total_time_seconds"]
        )
        if no_worse and strictly_better:
            return False
    return True


def run_benchmark(
    n,
    target_average_degrees,
    repeats,
    k_nearest,
    cluster_count,
    cluster_sigma,
    uniform_background_fraction,
    center_margin,
    minimum_center_separation,
    max_connectivity_attempts,
    seed,
    verify_reproducibility=False,
):
    _validate_configuration(
        n=n,
        target_average_degrees=target_average_degrees,
        repeats=repeats,
        k_nearest=k_nearest,
        cluster_count=cluster_count,
        cluster_sigma=cluster_sigma,
        uniform_background_fraction=uniform_background_fraction,
        center_margin=center_margin,
        minimum_center_separation=minimum_center_separation,
        max_connectivity_attempts=max_connectivity_attempts,
    )
    target_average_degrees = tuple(sorted(target_average_degrees))
    seed_generator = random.Random(seed)
    used_position_seeds = set()
    rows = []
    graph_sequence = 0
    total_graphs = repeats * len(target_average_degrees)

    for repeat_index in range(repeats):
        point_cloud = _find_connected_point_cloud(
            n=n,
            sparse_target_average_degree=target_average_degrees[0],
            seed_generator=seed_generator,
            used_position_seeds=used_position_seeds,
            cluster_count=cluster_count,
            cluster_sigma=cluster_sigma,
            uniform_background_fraction=uniform_background_fraction,
            center_margin=center_margin,
            minimum_center_separation=minimum_center_separation,
            max_connectivity_attempts=max_connectivity_attempts,
        )
        position_fingerprint = _position_fingerprint(point_cloud)
        cluster_metadata = _cluster_metadata(
            point_cloud,
            cluster_sigma,
            uniform_background_fraction,
        )

        density_order = _rotated(target_average_degrees, repeat_index)
        for density_execution_position, target_average_degree in enumerate(
            density_order,
            start=1,
        ):
            graph_sequence += 1
            density_index = target_average_degrees.index(target_average_degree)
            density_level = _density_label(
                density_index,
                len(target_average_degrees),
            )
            prepared = _prepare_graph(point_cloud, target_average_degree)
            graph = prepared["graph"]
            method_functions = _method_functions(
                graph,
                prepared["radius"],
                k_nearest,
            )
            method_order = _rotated(
                METHODS,
                density_index + repeat_index,
            )
            run_seed = (
                point_cloud.position_seed
                ^ RUN_SEED_MASK
                ^ int(round(target_average_degree * 1000))
            ) % (2**32)
            method_data = {}

            for method_execution_position, method in enumerate(
                method_order,
                start=1,
            ):
                pipeline = _run_final_pipeline(
                    method=method_functions[method],
                    pair_seed=run_seed,
                    converted_graph=prepared["converted"],
                    dist_matrix=prepared["dist_matrix"],
                    family=method,
                    strategy="collision",
                )
                if verify_reproducibility:
                    reproduced = _run_final_pipeline(
                        method=method_functions[method],
                        pair_seed=run_seed,
                        converted_graph=prepared["converted"],
                        dist_matrix=prepared["dist_matrix"],
                        family=method,
                        strategy="collision",
                    )
                    _assert_reproduced(
                        pipeline,
                        reproduced,
                        method,
                        "collision",
                    )
                pipeline["method_execution_position"] = (
                    method_execution_position
                )
                method_data[method] = pipeline

            sizes = [method_data[method]["final_size"] for method in METHODS]
            times = [
                method_data[method]["final_total_time_seconds"]
                for method in METHODS
            ]
            smallest_size = min(sizes)
            fastest_time = min(times)
            size_best_methods = ",".join(
                method
                for method in METHODS
                if method_data[method]["final_size"] == smallest_size
            )
            fastest_methods = ",".join(
                method
                for method in METHODS
                if method_data[method]["final_total_time_seconds"]
                == fastest_time
            )

            graph_id = (
                f"clustered_n{n}_degree{target_average_degree:g}_"
                f"repeat{repeat_index + 1}"
            )
            for method in METHODS:
                pipeline = method_data[method]
                if not pipeline["final_valid"]:
                    raise RuntimeError(f"{graph_id}/{method} is not valid")
                row = {
                    "experiment_version": EXPERIMENT_VERSION,
                    "benchmark_seed": seed,
                    "graph_sequence": graph_sequence,
                    "graph_id": graph_id,
                    "graph_model": "uniform_background_plus_gaussian_hotspots",
                    "n": n,
                    "repeat": repeat_index + 1,
                    "position_cloud_seed": point_cloud.position_seed,
                    "position_cloud_fingerprint_sha256": position_fingerprint,
                    "rejected_clouds_before_acceptance": (
                        point_cloud.rejected_clouds_before_acceptance
                    ),
                    "accepted_cloud_attempt": (
                        point_cloud.rejected_clouds_before_acceptance + 1
                    ),
                    "center_margin": center_margin,
                    "minimum_center_separation": (
                        minimum_center_separation
                    ),
                    "max_connectivity_attempts": max_connectivity_attempts,
                    **cluster_metadata,
                    "target_average_degree": target_average_degree,
                    "target_edge_count": int(
                        round(target_average_degree * n / 2.0)
                    ),
                    "achieved_average_degree": prepared[
                        "achieved_average_degree"
                    ],
                    "density_level": density_level,
                    "calibrated_radius": prepared["radius"],
                    "density_execution_position": density_execution_position,
                    "density_execution_order": ",".join(
                        f"{value:g}" for value in density_order
                    ),
                    "graph_seed": point_cloud.position_seed,
                    "graph_fingerprint_sha256": prepared["fingerprint"],
                    **prepared["summary"],
                    "graph_generation_time_seconds": prepared[
                        "generation_time_seconds"
                    ],
                    "shared_preprocessing_time_seconds": prepared[
                        "shared_preprocessing_time_seconds"
                    ],
                    "shared_preprocessing_excluded_from_method_times": True,
                    "method_reproducibility_check_performed": (
                        verify_reproducibility
                    ),
                    "k_nearest": k_nearest,
                    "method": method,
                    "method_execution_position": pipeline[
                        "method_execution_position"
                    ],
                    "method_execution_order": ",".join(method_order),
                    "run_seed": run_seed,
                    "repair_seed": run_seed,
                    **_public_pipeline_data(pipeline),
                    "final_size_over_n": pipeline["final_size"] / n,
                    "graph_smallest_final_size": smallest_size,
                    "graph_fastest_final_time_seconds": fastest_time,
                    "size_best_methods": size_best_methods,
                    "fastest_methods": fastest_methods,
                    "is_size_best": pipeline["final_size"] == smallest_size,
                    "is_fastest": pipeline["final_total_time_seconds"]
                    == fastest_time,
                    "final_size_rank": _rank(pipeline["final_size"], sizes),
                    "final_time_rank": _rank(
                        pipeline["final_total_time_seconds"],
                        times,
                    ),
                    "size_above_graph_best": (
                        pipeline["final_size"] - smallest_size
                    ),
                    "time_ratio_to_graph_fastest": (
                        pipeline["final_total_time_seconds"] / fastest_time
                    ),
                    "on_size_time_pareto_frontier": _pareto_frontier(
                        method,
                        method_data,
                    ),
                }
                rows.append(row)

            size_text = " ".join(
                f"{method}={method_data[method]['final_size']}"
                for method in METHODS
            )
            print(
                f"[{graph_sequence:02d}/{total_graphs:02d}] "
                f"repeat={repeat_index + 1}/{repeats} "
                f"target_degree={target_average_degree:g} "
                f"radius={prepared['radius']:.4f} {size_text}"
            )

    expected_rows = total_graphs * len(METHODS)
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
        writer = csv.DictWriter(output_file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "Cloud": row["repeat"],
                    "Density (avg degree)": (
                        f"{row['density_level'].title()} "
                        f"({row['target_average_degree']:g})"
                    ),
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
    rows = run_benchmark(
        n=args.n,
        target_average_degrees=args.target_average_degrees,
        repeats=args.repeats,
        k_nearest=args.k_nearest,
        cluster_count=args.cluster_count,
        cluster_sigma=args.cluster_sigma,
        uniform_background_fraction=args.uniform_background_fraction,
        center_margin=args.center_margin,
        minimum_center_separation=args.minimum_center_separation,
        max_connectivity_attempts=args.max_connectivity_attempts,
        seed=args.seed,
        verify_reproducibility=args.verify_reproducibility,
    )
    write_results(rows, args.output)
    print(f"Wrote {len(rows)} clustered Collision results to {args.output}")


if __name__ == "__main__":
    main()
