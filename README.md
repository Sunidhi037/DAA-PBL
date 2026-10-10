# Prim's Algorithm Module 

Minimum-Cost Network for Connecting Multiple Campus Buildings – **Prim's MST** implementation in Python.
This module runs independently; it does not need the Kruskal module.

## Files

| File | Purpose |
|------|---------|
| `min_heap.py` | Hand-written binary Min-Heap / Priority Queue (no `heapq`) |
| `graph.py` | Adjacency-list graph, input validation, JSON dataset loader |
| `prim.py` | Prim's algorithm + command-line runner |
| `datasets/` | 4 campus datasets (3 connected + 1 disconnected) |
| `tests/test_prim.py` | Unit tests (heap, graph, Prim, edge cases, random graphs) |

## Input format

```json
{
  "buildings": ["Library", "Admin Block", "CS Dept"],
  "connections": [
    ["Library", "Admin Block", 4],
    ["Library", "CS Dept", 2]
  ]
}
```

Connections are undirected; the third value is the cost/distance (non-negative number).
If the team's shared `data/` format differs, only `load_graph()` in `graph.py` needs changing.

## How to run

Requires Python 3.8+ (no external packages).

```bash
cd prim
python prim.py datasets/campus_small.json
python prim.py datasets/campus_large.json --start "Main Gate"
python prim.py datasets/campus_disconnected.json      # shows the error message
```

Sample output:

```
Dataset: datasets/campus_small.json  (6 buildings, 8 connections)
Prim's MST (start building: Library)
--------------------------------------------------------
#   From                   To                       Cost
1   Library                CS Dept                     2
2   CS Dept                Admin Block                 1
...
Total minimum cost : 17
```

## How to run the tests

```bash
cd prim
python -m unittest discover -s tests -v
```

Test coverage:

* **Min-Heap:** empty heap, ordering, duplicates/tuples, 500 random values vs `sorted()`.
* **Graph:** undirected adjacency list, unknown building, negative/non-numeric weight, duplicate building, self-loop, missing file.
* **Datasets:** small, medium, large (cost checked against an independent Kruskal reference; the small one is also solved by hand = 17; result is the same from every start vertex), disconnected.
* **Edge cases:** single building, two buildings, no link, empty graph, unknown start, parallel edges, equal weights, zero weights, float weights.
* **Random testing:** 200 random graphs compared with the reference (including disconnected ones).

No MST or final answer is hardcoded in the program – it is always computed from the dataset.

## Algorithm (Prim's, lazy version)

1. Select a starting building and mark it visited.
2. Push all its edges `(weight, from, to)` on the Min-Heap.
3. Pop the cheapest edge. If its `to` building is already visited, skip it (it would form a cycle).
4. Otherwise add the edge to the MST, mark the building visited, and push its edges to unvisited neighbours.
5. Repeat until the MST has `V − 1` edges or the heap is empty.
6. If fewer than `V` buildings were visited, the graph is **disconnected** and no MST exists → a clear error is reported.

## Complexity

Let **V** = number of buildings, **E** = number of connections.

| | Complexity | Reason |
|---|---|---|
| Time | **O(E log V)** | Each edge is pushed at most twice and popped at most twice; each heap operation is O(log E) = O(log V) since E ≤ V² |
| Space | **O(V + E)** | Adjacency list O(V + E), visited set O(V), heap holds up to O(E) entries |

Heap operations: `push` O(log n), `pop` O(log n), `peek` O(1).

(With a dense graph and an array instead of a heap, Prim's can be O(V²); the heap version is better for sparse campus graphs.)

## Error handling

| Case | Behaviour |
|------|-----------|
| Disconnected graph | `DisconnectedGraphError` – lists the unreachable buildings (CLI exit code 2) |
| Empty graph / unknown start building | `GraphError` (exit code 1) |
| Bad input (unknown building, negative or non-numeric cost, duplicates, self-loop, bad JSON, missing file) | `GraphError` with a clear message (exit code 1) |
