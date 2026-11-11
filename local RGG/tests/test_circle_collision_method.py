import random
import unittest

import igraph as ig
import networkx as nx

from algorithms.circle_collision_method import (
    get_metric_dimension_circle_collision,
    get_metric_dimension_circle_entropy_experimental,
)
from algorithms.circle_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_circle,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


class CircleCollisionMethodTests(unittest.TestCase):
    def test_both_experimental_selectors_return_resolving_sets(self):
        graph = nx.random_geometric_graph(40, 0.35, seed=731)
        g = ig.Graph.from_networkx(graph)
        dist_matrix = g.distances()

        for method in (
            get_metric_dimension_circle_entropy_experimental,
            get_metric_dimension_circle_collision,
        ):
            random.seed(19)
            run = method(graph, 0.35, k_nearest=5)
            self.assertTrue(
                checkIfResolvingSet_igraph(g, run.resolving_set, dist_matrix)
            )
            self.assertGreaterEqual(run.pre_prune_size, len(run.resolving_set))

    def test_entropy_control_matches_existing_circle(self):
        graph = nx.random_geometric_graph(35, 0.4, seed=991)

        random.seed(73)
        original = get_metric_dimension_of_graph_with_pruning_igraph_circle(
            graph,
            0.4,
            k_nearest=5,
        )
        random.seed(73)
        control = get_metric_dimension_circle_entropy_experimental(
            graph,
            0.4,
            k_nearest=5,
        )

        self.assertEqual(original, control.resolving_set)

    def test_invalid_parameters_are_rejected(self):
        graph = nx.random_geometric_graph(5, 0.5, seed=2)
        with self.assertRaises(ValueError):
            get_metric_dimension_circle_collision(
                graph,
                0,
            )
        with self.assertRaises(ValueError):
            get_metric_dimension_circle_collision(
                graph,
                0.5,
                k_nearest=0,
            )
        with self.assertRaises(ValueError):
            get_metric_dimension_circle_collision(
                graph,
                0.5,
                max_iters=0,
            )


if __name__ == "__main__":
    unittest.main()
