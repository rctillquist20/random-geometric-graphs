import random
import unittest

import igraph as ig
import networkx as nx

from algorithms.grid_collision_method import (
    get_metric_dimension_grid_collision,
    get_metric_dimension_grid_entropy_experimental,
)
from functions.resolving_functions import checkIfResolvingSet_igraph


class GridCollisionMethodTests(unittest.TestCase):
    def test_both_experimental_selectors_return_resolving_sets(self):
        graph = nx.random_geometric_graph(40, 0.35, seed=731)
        g = ig.Graph.from_networkx(graph)
        dist_matrix = g.distances()

        for method in (
            get_metric_dimension_grid_entropy_experimental,
            get_metric_dimension_grid_collision,
        ):
            random.seed(19)
            run = method(graph, 0.35, k_nearest=5)
            self.assertTrue(
                checkIfResolvingSet_igraph(g, run.resolving_set, dist_matrix)
            )
            self.assertGreaterEqual(run.pre_prune_size, len(run.resolving_set))

    def test_k_nearest_must_be_positive(self):
        graph = nx.random_geometric_graph(5, 0.5, seed=2)
        with self.assertRaises(ValueError):
            get_metric_dimension_grid_collision(graph, 0.5, k_nearest=0)


if __name__ == "__main__":
    unittest.main()
