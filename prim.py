"""
prim.py - Prim's algorithm for the Minimum-Cost Campus Network project.

Member 2 module.

Idea
----
Grow the MST from one starting building.  At every step take the cheapest
edge that connects a building *inside* the tree to one *outside* it.  A
Min-Heap (priority queue) gives us that cheapest edge quickly.

We use the "lazy" version: when a building is added to the tree, every
edge leaving it is pushed on the heap.  When an edge is popped whose far
end is already visited, it is simply skipped (it would form a cycle).

Complexity  (V = buildings, E = connections)
    Time  : O(E log V)   - each edge is pushed/popped at most twice,
                           each heap operation costs O(log E) = O(log V)
    Space : O(V + E)     - adjacency list + visited set + heap

Usage
-----
    python prim.py datasets/campus_small.json
    python prim.py datasets/campus_small.json --start "Library"
"""

import argparse
import sys

from graph import Graph, GraphError, load_graph
from min_heap import MinHeap


class DisconnectedGraphError(Exception):
    """Raised when not every building can be reached (no spanning tree)."""

    def __init__(self, unreachable, reachable_count, total):
        self.unreachable = unreachable
        super().__init__(
            f"Graph is disconnected: only {reachable_count} of {total} buildings "
            f"are reachable. Unreachable: {', '.join(unreachable)}"
        )


def prim_mst(graph, start=None):
    """
    Compute the Minimum Spanning Tree of `graph` using Prim's algorithm.

    Returns (mst_edges, total_cost) where mst_edges is a list of
    (building_a, building_b, weight) in the order they were added.

    Raises:
        GraphError              - empty graph or unknown start building
        DisconnectedGraphError  - no spanning tree exists
    """
    if graph.num_buildings() == 0:
        raise GraphError("Graph has no buildings.")

    # 1. select a starting vertex
    if start is None:
        start = graph.buildings[0]
    elif start not in graph.adj:
        raise GraphError(f"Start building not found: {start!r}")

    visited = {start}                 # 2. track visited vertices
    mst_edges = []
    total_cost = 0
    heap = MinHeap()                  # entries: (weight, from, to)

    for neighbour, w in graph.neighbours(start):
        heap.push((w, start, neighbour))

    target = graph.num_buildings() - 1          # an MST has V-1 edges
    while not heap.is_empty() and len(mst_edges) < target:
        w, u, v = heap.pop()                    # cheapest crossing edge
        if v in visited:                        # would create a cycle -> skip
            continue
        visited.add(v)
        mst_edges.append((u, v, w))
        total_cost += w
        for neighbour, nw in graph.neighbours(v):
            if neighbour not in visited:
                heap.push((nw, v, neighbour))

    # disconnected check
    if len(visited) != graph.num_buildings():
        unreachable = [b for b in graph.buildings if b not in visited]
        raise DisconnectedGraphError(unreachable, len(visited), graph.num_buildings())

    return mst_edges, total_cost


def print_result(mst_edges, total_cost, start):
    print(f"Prim's MST (start building: {start})")
    print("-" * 56)
    print(f"{'#':<3} {'From':<22} {'To':<22} {'Cost':>6}")
    for i, (u, v, w) in enumerate(mst_edges, 1):
        print(f"{i:<3} {u:<22} {v:<22} {w:>6}")
    print("-" * 56)
    print(f"Edges selected     : {len(mst_edges)}")
    print(f"Total minimum cost : {total_cost}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prim's MST for the campus network.")
    parser.add_argument("dataset", help="path to dataset JSON file")
    parser.add_argument("--start", help="starting building (default: first in file)")
    args = parser.parse_args(argv)

    try:
        graph = load_graph(args.dataset)
        start = args.start if args.start else (graph.buildings[0] if graph.buildings else None)
        print(f"Dataset: {args.dataset}  "
              f"({graph.num_buildings()} buildings, {graph.num_connections()} connections)")
        edges, total = prim_mst(graph, start)
    except DisconnectedGraphError as e:
        print(f"ERROR: {e}")
        return 2
    except GraphError as e:
        print(f"ERROR: {e}")
        return 1

    print_result(edges, total, start)
    return 0


if __name__ == "__main__":
    sys.exit(main())
