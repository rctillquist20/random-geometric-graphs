import random
import unittest
from unittest.mock import patch

import igraph as ig
import networkx as nx
import numpy as np

from algorithms.collision_repaired_methods import (
    get_metric_dimension_circle_collision_repaired,
    get_metric_dimension_grid_collision_repaired,
    get_metric_dimension_ich_collision_repaired,
    get_metric_dimension_zoomed_square_collision_repaired,
)
from functions.global_collision_repair import repair_resolving_set_globally
from functions.resolving_functions import checkIfResolvingSet_igraph


class GlobalCollisionRepairTests(unittest.TestCase):
    def test_already_valid_set_is_returned_exactly_without_pruning(self):
        graph = ig.Graph(n=6, edges=[(node, node + 1) for node in range(5)])
        original = {0}

        with patch(
            "functions.global_collision_repair."
            "prune_resolving_set_zobrist_fast",
            side_effect=AssertionError("valid inputs must not be repruned"),
        ):
            run = repair_resolving_set_globally(graph, original)

        self.assertIs(run.resolving_set, original)
        self.assertEqual(run.original_size, 1)
        self.assertEqual(run.repaired_pre_prune_size, 1)
        self.assertEqual(run.repair_probes, ())
        self.assertEqual(run.collision_pairs_before, 0)
        self.assertEqual(run.collision_pairs_after, 0)
        self.assertEqual(run.pruned_after_repair, 0)

    def test_lowest_id_breaks_a_collision_score_tie(self):
        graph = ig.Graph.Ring(4)

        with patch(
            "functions.global_collision_repair."
            "prune_resolving_set_zobrist_fast",
            side_effect=lambda _, resolving_set, __: set(resolving_set),
        ):
            run = repair_resolving_set_globally(graph, set())

        self.assertEqual(run.repair_probes[0], 0)
        self.assertEqual(run.collision_pairs_before, 6)
        self.assertEqual(run.collision_pairs_after, 0)
        self.assertTrue(
            checkIfResolvingSet_igraph(
                graph,
                run.resolving_set,
                graph.distances(),
            )
        )

    def test_disconnected_distances_are_repaired(self):
        graph = ig.Graph(n=4, edges=[(0, 1), (2, 3)])
        distances_with_negative_infinity_code = [
            [0, 1, -1, -1],
            [1, 0, -1, -1],
            [-1, -1, 0, 1],
            [-1, -1, 1, 0],
        ]

        run = repair_resolving_set_globally(
            graph,
            set(),
            distances_with_negative_infinity_code,
        )

        self.assertEqual(run.collision_pairs_after, 0)
        self.assertTrue(run.resolving_set)

    def test_singleton_receives_the_required_landmark(self):
        graph = ig.Graph(n=1)
        run = repair_resolving_set_globally(graph, set())

        self.assertEqual(run.resolving_set, {0})
        self.assertEqual(run.repair_probes, (0,))
        self.assertEqual(run.collision_pairs_before, 0)
        self.assertEqual(run.collision_pairs_after, 0)

    def test_unsupported_graph_shapes_are_rejected(self):
        with self.assertRaises(ValueError):
            repair_resolving_set_globally(ig.Graph(n=0), set())
        with self.assertRaises(ValueError):
            repair_resolving_set_globally(
                ig.Graph(n=2, edges=[(0, 1)], directed=True),
                set(),
            )

    def test_unsafe_pruning_result_is_reverted(self):
        graph = ig.Graph.Ring(4)

        with patch(
            "functions.global_collision_repair."
            "prune_resolving_set_zobrist_fast",
            return_value=set(),
        ):
            run = repair_resolving_set_globally(graph, set())

        self.assertTrue(run.resolving_set)
        self.assertEqual(run.collision_pairs_after, 0)
        self.assertEqual(run.pruned_after_repair, 0)

    def test_repaired_wrappers_return_valid_common_records(self):
        graph = nx.random_geometric_graph(18, 0.45, seed=427)
        converted = ig.Graph.from_networkx(graph)
        distances = converted.distances()

        random.seed(31)
        np.random.seed(31)
        runs = (
            get_metric_dimension_grid_collision_repaired(
                graph,
                0.45,
                k_nearest=5,
            ),
            get_metric_dimension_circle_collision_repaired(
                graph,
                0.45,
                k_nearest=5,
            ),
            get_metric_dimension_zoomed_square_collision_repaired(
                graph,
                0.45,
                k_nearest=5,
            ),
            get_metric_dimension_ich_collision_repaired(graph),
        )

        for run in runs:
            self.assertEqual(run.collision_pairs_after, 0)
            self.assertGreaterEqual(
                run.original_method_pre_prune_size,
                run.original_size,
            )
            self.assertTrue(
                checkIfResolvingSet_igraph(
                    converted,
                    run.resolving_set,
                    distances,
                )
            )


if __name__ == "__main__":
    unittest.main()
