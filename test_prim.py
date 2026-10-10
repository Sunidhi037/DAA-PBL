"""
Tests for Member 2's module (Prim's algorithm + Min-Heap).

Run from the project root:      python -m unittest discover -s prim/tests -v
or from inside prim/:           python -m unittest discover -s tests -v

To avoid hardcoding answers, the MST cost is checked against an
INDEPENDENT reference (a tiny Kruskal + union-find written in this file),
plus one small case solved by hand.
"""

import os
import random
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PRIM_DIR = os.path.dirname(HERE)
sys.path.insert(0, PRIM_DIR)

from graph import Graph, GraphError, build_graph, load_graph      # noqa: E402
from min_heap import MinHeap                                       # noqa: E402
from prim import DisconnectedGraphError, prim_mst                  # noqa: E402

DATA = os.path.join(PRIM_DIR, "datasets")


# --------------------------------------------------------------------------
# Independent reference: Kruskal with union-find (used only to cross-check)
# --------------------------------------------------------------------------
def reference_mst_cost(buildings, connections):
    parent = {b: b for b in buildings}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total, used = 0, 0
    for a, b, w in sorted(connections, key=lambda e: e[2]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += w
            used += 1
    return total if used == len(buildings) - 1 else None


def is_spanning_tree(buildings, edges):
    """Check: V-1 edges, no cycle, touches every building."""
    if len(edges) != len(buildings) - 1:
        return False
    parent = {b: b for b in buildings}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for u, v, _ in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
    return len({find(b) for b in buildings}) == 1


# --------------------------------------------------------------------------
class TestMinHeap(unittest.TestCase):
    def test_empty(self):
        h = MinHeap()
        self.assertTrue(h.is_empty())
        self.assertEqual(len(h), 0)
        with self.assertRaises(IndexError):
            h.pop()
        with self.assertRaises(IndexError):
            h.peek()

    def test_pop_order_sorted(self):
        h = MinHeap()
        for x in [5, 3, 8, 1, 9, 2, 7]:
            h.push(x)
        self.assertEqual(h.peek(), 1)
        self.assertEqual([h.pop() for _ in range(len(h))], [1, 2, 3, 5, 7, 8, 9])

    def test_duplicates_and_tuples(self):
        h = MinHeap()
        for item in [(4, "a", "b"), (4, "a", "a"), (1, "z", "z"), (4, "a", "b")]:
            h.push(item)
        self.assertEqual(h.pop(), (1, "z", "z"))
        self.assertEqual(h.pop(), (4, "a", "a"))
        self.assertEqual(len(h), 2)

    def test_random_matches_sorted(self):
        rng = random.Random(1)
        values = [rng.randint(0, 1000) for _ in range(500)]
        h = MinHeap()
        for v in values:
            h.push(v)
        self.assertEqual([h.pop() for _ in range(len(values))], sorted(values))


# --------------------------------------------------------------------------
class TestGraph(unittest.TestCase):
    def test_adjacency_list_is_undirected(self):
        g = build_graph(["A", "B"], [["A", "B", 3]])
        self.assertIn(("B", 3), g.neighbours("A"))
        self.assertIn(("A", 3), g.neighbours("B"))
        self.assertEqual(g.num_connections(), 1)

    def test_invalid_input(self):
        with self.assertRaises(GraphError):
            build_graph(["A", "B"], [["A", "C", 1]])        # unknown building
        with self.assertRaises(GraphError):
            build_graph(["A", "B"], [["A", "B", -2]])       # negative weight
        with self.assertRaises(GraphError):
            build_graph(["A", "B"], [["A", "B", "x"]])      # non-numeric weight
        with self.assertRaises(GraphError):
            build_graph(["A", "A"], [])                     # duplicate building
        with self.assertRaises(GraphError):
            build_graph(["A"], [["A", "A", 1]])             # self loop

    def test_missing_file(self):
        with self.assertRaises(GraphError):
            load_graph(os.path.join(DATA, "does_not_exist.json"))


# --------------------------------------------------------------------------
class TestPrimDatasets(unittest.TestCase):
    def _check_dataset(self, filename):
        g = load_graph(os.path.join(DATA, filename))
        edges, total = prim_mst(g)
        buildings = g.buildings
        conns = [(u, v, w) for u in g.adj for v, w in g.adj[u] if u < v]
        self.assertTrue(is_spanning_tree(buildings, edges))
        self.assertEqual(total, sum(w for _, _, w in edges))
        self.assertEqual(total, reference_mst_cost(buildings, conns))
        # MST cost must not depend on the starting building
        for start in buildings:
            self.assertEqual(prim_mst(g, start)[1], total)
        return total

    def test_small_dataset(self):
        total = self._check_dataset("campus_small.json")
        # solved by hand: 1 + 2 + 3 + 5 + 6
        self.assertEqual(total, 17)

    def test_medium_dataset(self):
        self._check_dataset("campus_medium.json")

    def test_large_dataset(self):
        self._check_dataset("campus_large.json")

    def test_disconnected_dataset(self):
        g = load_graph(os.path.join(DATA, "campus_disconnected.json"))
        with self.assertRaises(DisconnectedGraphError) as ctx:
            prim_mst(g)
        self.assertIn("Remote Farm House", ctx.exception.unreachable)
        # starting from the other component must also fail
        with self.assertRaises(DisconnectedGraphError):
            prim_mst(g, "Hostel")


# --------------------------------------------------------------------------
class TestPrimEdgeCases(unittest.TestCase):
    def test_single_building(self):
        g = build_graph(["Only"], [])
        self.assertEqual(prim_mst(g), ([], 0))

    def test_two_buildings(self):
        g = build_graph(["A", "B"], [["A", "B", 9]])
        self.assertEqual(prim_mst(g), ([("A", "B", 9)], 9))

    def test_two_buildings_no_link(self):
        with self.assertRaises(DisconnectedGraphError):
            prim_mst(build_graph(["A", "B"], []))

    def test_empty_graph(self):
        with self.assertRaises(GraphError):
            prim_mst(Graph())

    def test_unknown_start(self):
        g = build_graph(["A", "B"], [["A", "B", 1]])
        with self.assertRaises(GraphError):
            prim_mst(g, "Z")

    def test_parallel_edges_choose_cheapest(self):
        g = build_graph(["A", "B"], [["A", "B", 10], ["A", "B", 4]])
        self.assertEqual(prim_mst(g)[1], 4)

    def test_equal_weights(self):
        g = build_graph(["A", "B", "C", "D"],
                        [["A", "B", 1], ["B", "C", 1], ["C", "D", 1], ["A", "D", 1], ["A", "C", 1]])
        edges, total = prim_mst(g)
        self.assertEqual(total, 3)
        self.assertTrue(is_spanning_tree(g.buildings, edges))

    def test_zero_weight(self):
        g = build_graph(["A", "B", "C"], [["A", "B", 0], ["B", "C", 5], ["A", "C", 2]])
        self.assertEqual(prim_mst(g)[1], 2)

    def test_float_weights(self):
        g = build_graph(["A", "B", "C"], [["A", "B", 1.5], ["B", "C", 2.25], ["A", "C", 9.0]])
        self.assertAlmostEqual(prim_mst(g)[1], 3.75)

    def test_random_graphs_match_reference(self):
        rng = random.Random(2024)
        for _ in range(200):
            n = rng.randint(2, 12)
            names = [f"B{i}" for i in range(n)]
            conns = []
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.45:
                        conns.append([names[i], names[j], rng.randint(1, 50)])
            g = build_graph(names, conns)
            expected = reference_mst_cost(names, conns)
            if expected is None:
                with self.assertRaises(DisconnectedGraphError):
                    prim_mst(g)
            else:
                edges, total = prim_mst(g)
                self.assertEqual(total, expected)
                self.assertTrue(is_spanning_tree(names, edges))


if __name__ == "__main__":
    unittest.main(verbosity=2)
