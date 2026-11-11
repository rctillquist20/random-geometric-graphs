import unittest

import igraph as ig
import networkx as nx
import numpy as np

from algorithms.ich_collision_method import (
    get_metric_dimension_ich_collision,
    get_metric_dimension_ich_entropy_experimental,
)
from algorithms.ich_multilateration import get_metric_dimension_of_graph_ich
from functions.resolving_functions import checkIfResolvingSet_igraph


class ICHCollisionMethodTests(unittest.TestCase):
    def test_both_selectors_return_resolving_sets(self):
        graph = nx.random_geometric_graph(30, 0.35, seed=427)
        converted = ig.Graph.from_networkx(graph)
        dist_matrix = converted.distances()

        for method in (
            get_metric_dimension_ich_entropy_experimental,
            get_metric_dimension_ich_collision,
        ):
            np.random.seed(31)
            run = method(graph)
            self.assertTrue(
                checkIfResolvingSet_igraph(
                    converted,
                    run.resolving_set,
                    dist_matrix,
                )
            )
            self.assertEqual(run.pre_prune_size, len(run.resolving_set))
            self.assertEqual(len(run.selection_order), len(run.resolving_set))

    def test_entropy_control_matches_existing_ich(self):
        graph = nx.random_geometric_graph(24, 0.4, seed=991)

        np.random.seed(73)
        original = get_metric_dimension_of_graph_ich(graph)
        np.random.seed(73)
        control = get_metric_dimension_ich_entropy_experimental(graph)

        self.assertEqual(original, list(control.selection_order))

    def test_deterministic_order_can_be_requested(self):
        graph = nx.path_graph(8)
        first = get_metric_dimension_ich_collision(graph, rand_order=False)
        second = get_metric_dimension_ich_collision(graph, rand_order=False)
        self.assertEqual(first.selection_order, second.selection_order)


if __name__ == "__main__":
    unittest.main()
