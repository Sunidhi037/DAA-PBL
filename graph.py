"""
graph.py - Adjacency-list graph for the campus network + dataset loader.

Buildings are vertices; possible network links are undirected weighted
edges (weight = cost / distance).

Agreed input format (JSON):

    {
      "buildings": ["Library", "Admin Block", ...],
      "connections": [
        ["Library", "Admin Block", 120],
        ...
      ]
    }

Representation:  adjacency list  ->  { building: [(neighbour, weight), ...] }

Space complexity: O(V + E)
"""

import json


class GraphError(ValueError):
    """Raised when the input data is invalid."""


class Graph:
    def __init__(self):
        self.adj = {}          # building -> list of (neighbour, weight)

    # ---- construction --------------------------------------------------
    def add_building(self, name):
        if not isinstance(name, str) or not name.strip():
            raise GraphError(f"Invalid building name: {name!r}")
        if name in self.adj:
            raise GraphError(f"Duplicate building: {name!r}")
        self.adj[name] = []

    def add_connection(self, a, b, weight):
        if a not in self.adj:
            raise GraphError(f"Unknown building in connection: {a!r}")
        if b not in self.adj:
            raise GraphError(f"Unknown building in connection: {b!r}")
        if a == b:
            raise GraphError(f"Self-loop not allowed: {a!r}")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise GraphError(f"Weight must be a number: {a} - {b} = {weight!r}")
        if weight < 0:
            raise GraphError(f"Negative weight not allowed: {a} - {b} = {weight}")
        # undirected -> store in both directions
        self.adj[a].append((b, weight))
        self.adj[b].append((a, weight))

    # ---- queries -------------------------------------------------------
    @property
    def buildings(self):
        return list(self.adj)

    def num_buildings(self):
        return len(self.adj)

    def num_connections(self):
        return sum(len(v) for v in self.adj.values()) // 2

    def neighbours(self, name):
        return self.adj[name]


def build_graph(buildings, connections):
    """Build a Graph from a list of names and (a, b, weight) triples."""
    g = Graph()
    for b in buildings:
        g.add_building(b)
    for conn in connections:
        if len(conn) != 3:
            raise GraphError(f"Each connection needs 3 values, got: {conn!r}")
        g.add_connection(conn[0], conn[1], conn[2])
    return g


def load_graph(path):
    """Load a campus dataset (JSON file) into a Graph."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise GraphError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise GraphError(f"File is not valid JSON ({path}): {e}")

    if not isinstance(data, dict) or "buildings" not in data or "connections" not in data:
        raise GraphError("Dataset must contain 'buildings' and 'connections'.")
    return build_graph(data["buildings"], data["connections"])
