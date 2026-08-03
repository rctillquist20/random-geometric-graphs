import unittest

from functions.collision_functions import (
    collision_score_of_landmark_candidate,
    count_colliding_pairs,
    extend_signatures,
    select_collision_minimizing_candidate,
)


class CollisionFunctionTests(unittest.TestCase):
    def setUp(self):
        # Shortest-path distances for a four-node path.
        self.dist_matrix = [
            [0, 1, 2, 3],
            [1, 0, 1, 2],
            [2, 1, 0, 1],
            [3, 2, 1, 0],
        ]

    def test_count_colliding_pairs(self):
        signatures = {0: (0,), 1: (1,), 2: (1,), 3: (1,)}
        self.assertEqual(count_colliding_pairs(signatures), 3)

    def test_endpoint_candidate_resolves_path(self):
        nodes = range(4)
        signatures = {node: 0 for node in nodes}
        score = collision_score_of_landmark_candidate(
            nodes,
            0,
            signatures,
            self.dist_matrix,
        )
        self.assertEqual(score, 0)

    def test_selector_chooses_candidate_with_fewer_collisions(self):
        nodes = range(4)
        signatures = {node: 0 for node in nodes}
        selected = select_collision_minimizing_candidate(
            nodes,
            [1, 0],
            signatures,
            self.dist_matrix,
        )
        self.assertEqual(selected, 0)

    def test_extend_signatures_refines_equivalence_classes(self):
        signatures = {node: 0 for node in range(4)}
        updated = extend_signatures(
            range(4),
            1,
            signatures,
            self.dist_matrix,
        )
        self.assertEqual(updated[0], updated[2])
        self.assertNotEqual(updated[0], updated[1])
        self.assertNotEqual(updated[0], updated[3])


if __name__ == "__main__":
    unittest.main()
