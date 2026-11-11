import csv
from pathlib import Path
import tempfile
import unittest

import networkx as nx

from experiments_clustered_collision import (
    METHODS,
    RESULT_COLUMNS,
    _calibrated_geometric_graph,
    _position_fingerprint,
    _rotated,
    _sample_clustered_point_cloud,
    _validate_configuration,
    run_benchmark,
    write_results,
)


class ClusteredCollisionExperimentTests(unittest.TestCase):
    def test_point_cloud_is_seeded_balanced_and_inside_unit_square(self):
        first = _sample_clustered_point_cloud(
            n=50,
            position_seed=7241,
            cluster_count=5,
            uniform_background_fraction=0.6,
        )
        second = _sample_clustered_point_cloud(
            n=50,
            position_seed=7241,
            cluster_count=5,
            uniform_background_fraction=0.6,
        )

        self.assertEqual(_position_fingerprint(first), _position_fingerprint(second))
        self.assertEqual(first.cluster_sizes, (4, 4, 4, 4, 4))
        self.assertEqual(
            sum(assignment < 0 for assignment in first.cluster_assignments),
            30,
        )
        self.assertEqual(set(first.positions), set(range(50)))
        for x_position, y_position in first.positions.values():
            self.assertGreaterEqual(x_position, 0.0)
            self.assertLessEqual(x_position, 1.0)
            self.assertGreaterEqual(y_position, 0.0)
            self.assertLessEqual(y_position, 1.0)

    def test_radius_calibration_hits_the_requested_average_degree(self):
        point_cloud = _sample_clustered_point_cloud(
            n=60,
            position_seed=391,
            cluster_count=5,
            uniform_background_fraction=0.6,
        )
        graph, radius, achieved = _calibrated_geometric_graph(
            point_cloud,
            target_average_degree=10,
        )

        self.assertGreater(radius, 0.0)
        self.assertEqual(graph.number_of_edges(), 300)
        self.assertEqual(achieved, 10.0)
        self.assertEqual(set(graph.nodes()), set(range(60)))
        self.assertEqual(nx.get_node_attributes(graph, "pos"), point_cloud.positions)

    def test_execution_orders_are_balanced_over_six_repeats(self):
        targets = (15.0, 107.0, 240.0)
        method_positions = {
            (target, method): [] for target in targets for method in METHODS
        }
        density_positions = {target: [] for target in targets}

        for repeat_index in range(6):
            density_order = _rotated(targets, repeat_index)
            for density_position, target in enumerate(density_order, start=1):
                density_positions[target].append(density_position)
                density_index = targets.index(target)
                method_order = _rotated(METHODS, density_index + repeat_index)
                for method_position, method in enumerate(method_order, start=1):
                    method_positions[(target, method)].append(method_position)

        for positions in density_positions.values():
            self.assertEqual(sorted(positions), [1, 1, 2, 2, 3, 3])
        for positions in method_positions.values():
            self.assertEqual(sorted(positions), [1, 1, 2, 2, 3, 3])

    def test_small_seeded_benchmark_returns_three_exact_valid_outputs(self):
        rows = run_benchmark(
            n=30,
            target_average_degrees=[10],
            repeats=1,
            k_nearest=3,
            cluster_count=3,
            cluster_sigma=0.12,
            uniform_background_fraction=0.6,
            center_margin=0.15,
            minimum_center_separation=0.15,
            max_connectivity_attempts=50,
            seed=9876,
            verify_reproducibility=True,
        )

        self.assertEqual(len(rows), 3)
        self.assertEqual({row["method"] for row in rows}, set(METHODS))
        self.assertTrue(all(row["final_valid"] for row in rows))
        self.assertTrue(all(row["collision_pairs_after_repair"] == 0 for row in rows))
        self.assertEqual(len({row["graph_fingerprint_sha256"] for row in rows}), 1)

    def test_invalid_background_fraction_is_rejected(self):
        with self.assertRaises(ValueError):
            _validate_configuration(
                n=30,
                target_average_degrees=[10],
                repeats=1,
                k_nearest=3,
                cluster_count=3,
                cluster_sigma=0.12,
                uniform_background_fraction=1.0,
                center_margin=0.15,
                minimum_center_separation=0.15,
                max_connectivity_attempts=10,
            )

    def test_writer_saves_only_the_essential_result_columns(self):
        row = {
            "repeat": 2,
            "density_level": "medium",
            "target_average_degree": 107.0,
            "method": "zoomed",
            "final_size": 63,
            "final_total_time_seconds": 0.918,
            "original_size": 65,
            "original_valid": False,
            "repair_probe_count": 1,
            "pruned_after_repair": 3,
            "final_valid": True,
        }

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "results.csv"
            write_results([row], output_path)
            with output_path.open(newline="", encoding="utf-8") as output_file:
                reader = csv.DictReader(output_file)
                saved_rows = list(reader)

        self.assertEqual(tuple(reader.fieldnames), RESULT_COLUMNS)
        self.assertEqual(len(saved_rows), 1)
        self.assertEqual(saved_rows[0]["Density (avg degree)"], "Medium (107)")
        self.assertEqual(saved_rows[0]["Method"], "Zoomed Square")
        self.assertEqual(saved_rows[0]["Raw Valid"], "No")
        self.assertEqual(saved_rows[0]["Final Valid"], "Yes")


if __name__ == "__main__":
    unittest.main()
