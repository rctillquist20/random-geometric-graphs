import random
import unittest

import igraph as ig
import networkx as nx

from algorithms.reverse_elimination import reverse_eliminate
from functions.reverse_pruning_control import reverse_eliminate_existing_pruner


class ReversePruningControlTests(unittest.TestCase):
    def test_existing_pruner_matches_optimized_reverse_for_the_same_order(self):
        graphs = [ig.Graph.Full(12), ig.Graph.Ring(12), ig.Graph(n=12)]
        graphs += [ig.Graph.from_networkx(nx.random_geometric_graph(40, r, seed=9)) for r in (0.05, 0.15, 0.3, 0.6)]
        for graph in graphs:
            distances = graph.distances()
            for seed in range(3):
                with self.subTest(n=graph.vcount(), edges=graph.ecount(), seed=seed):
                    self.assertEqual(
                        reverse_eliminate_existing_pruner(graph, distances, seed=seed),
                        reverse_eliminate(graph, distances, seed=seed).resolving_set,
                    )

    def test_preserves_global_random_state(self):
        graph = ig.Graph.Ring(15)
        before = random.getstate()
        reverse_eliminate_existing_pruner(graph, graph.distances(), seed=18)
        self.assertEqual(random.getstate(), before)
