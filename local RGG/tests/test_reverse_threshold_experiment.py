import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import igraph as ig
import networkx as nx

from algorithms.reverse_elimination import ReverseEliminationRun
from experiments_reverse_threshold import benchmark, export_public_results, normalize_best_order_metadata, summarize


class ReverseThresholdTimingTests(unittest.TestCase):
    def test_public_export_contains_only_results_and_one_chart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "work"
            output = root / "outputs"
            work.mkdir()
            (work / "results.csv").write_text("Method,Set Size\nReverse,5\n")
            (work / "crossover.png").write_bytes(b"selected chart")
            (work / "comparison.png").write_bytes(b"other chart")
            (work / "raw_results.csv").write_text("internal checkpoint")
            export_public_results(work, output)
            self.assertEqual({path.name for path in output.iterdir()}, {
                "reverse_elimination_results.csv", "reverse_elimination_threshold.png",
            })
            self.assertEqual((output / "reverse_elimination_results.csv").read_bytes(), (work / "results.csv").read_bytes())
            self.assertEqual((output / "reverse_elimination_threshold.png").read_bytes(), b"selected chart")
            export_public_results(work, output, prefix="reverse_small_radius")
            self.assertEqual({path.name for path in output.iterdir()}, {
                "reverse_elimination_results.csv", "reverse_elimination_threshold.png",
                "reverse_small_radius_results.csv", "reverse_small_radius_threshold.png",
            })
            self.assertEqual((output / "reverse_elimination_threshold.png").read_bytes(), b"selected chart")

    def test_full_timing_includes_all_forward_work_and_shared_preprocessing(self):
        graph = nx.complete_graph(4)
        converted = ig.Graph.Full(4)
        prepared = {
            "graph": graph,
            "converted": converted,
            "dist_matrix": converted.distances(),
            "summary": {"edge_density": 1.0},
            "fingerprint": "same-graph",
            "shared_preprocessing_time_seconds": 7.0,
        }
        reverse = ReverseEliminationRun({0, 1, 2}, (3, 0, 1, 2), (3,))
        forward = {
            "_final_set": {0, 1, 2}, "final_size": 3,
            "final_total_time_seconds": 0.5, "repair_probe_count": 0,
        }
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(
                n_values=[4], r_values=[1.0], repeats=1, large_repeats=None,
                resume=False, seed=18, orders=1, methods=["grid"],
                k_nearest=5, output=Path(directory), timing="full",
            )
            # Reverse takes 2 seconds, forward takes 7 seconds. Both are
            # charged 7 seconds of shared preprocessing. The helper's 0.5s
            # stage sum must not replace the actual forward wall-clock time.
            with patch("experiments_reverse_threshold._prepare_graph", return_value=prepared), \
                 patch("experiments_reverse_threshold._method_functions", return_value={"grid": {"collision": object()}}), \
                 patch("experiments_reverse_threshold.reverse_eliminate", return_value=reverse), \
                 patch("experiments_reverse_threshold._run_final_pipeline", return_value=forward), \
                 patch("experiments_reverse_threshold.time.perf_counter", side_effect=[0, 2, 10, 14, 15, 17]):
                rows = benchmark(args)
        primary = {row["method"]: row for row in rows}
        self.assertEqual(primary["reverse"]["seconds"], 9.0)
        self.assertEqual(primary["grid"]["seconds"], 14.0)
        self.assertEqual(primary["grid"]["graph_fingerprint"], primary["reverse"]["graph_fingerprint"])

    def test_sparse_only_results_report_no_dense_threshold(self):
        shared = {
            "n": 20, "radius": 0.1, "repeat": 1,
            "edge_density": 0.03, "average_degree": 0.57,
            "valid": True, "twin_lower_bound": 2,
        }
        rows = [
            {**shared, "method": "reverse", "size": 9, "seconds": 0.01},
            {**shared, "method": "grid", "size": 7, "seconds": 0.1},
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            summarize(rows, output)
            self.assertEqual(len((output / "density_thresholds.csv").read_text().splitlines()), 1)
            self.assertIn("Reverse elimination", (output / "results.csv").read_text())

    def test_best_of_orders_records_the_seed_that_produced_its_set_size(self):
        shared = {"n": 20, "radius": 0.8, "repeat": 1}
        rows = [
            {**shared, "method": "reverse_order", "order_index": 0, "algorithm_seed": 11, "size": 9},
            {**shared, "method": "reverse_order", "order_index": 1, "algorithm_seed": 22, "size": 8},
            {**shared, "method": "reverse_best", "algorithm_seed": 11, "size": 8},
        ]
        self.assertTrue(normalize_best_order_metadata(rows))
        self.assertEqual(rows[-1]["algorithm_seed"], 22)
        self.assertFalse(normalize_best_order_metadata(rows))


if __name__ == "__main__":
    unittest.main()
