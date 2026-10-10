# Minimum-Cost Network for Connecting Multiple Campus Buildings

### Module: Kruskal's Algorithm + Disjoint Set Union (DSU) + Campus Dataset

**Role:** Member 1 — Sunidhi Singh
**Course:** Design & Analysis of Algorithms (DAA)

## Problem Statement

Given the buildings of a university campus and the possible cable connections
between them (each with an installation cost), connect **all** buildings with the
**minimum total cost** and **no unnecessary cycles**.

## Real-World Interpretation

- Building -> vertex
- Possible cable/network link -> undirected edge
- Weight = installation cost in ₹ = `distance_m × cost_per_m`
  (₹150/m for normal conduit, ₹200/m where the route crosses a road or needs trenching)
- Result: the Minimum Spanning Tree (MST) = cheapest set of links that connects every building

## Graph Representation

Edge list of `(source, destination, weight)` tuples, e.g. `("CSE Block", "Library", 6000)`.
Datasets are CSV files loaded by `src/graph.py`, which validates every row
(unknown building, self-loop, non-positive values).

- `data/buildings.csv` — 10 buildings
- `data/connections.csv` — 18 possible connections (`source,destination,distance_m,cost_per_m`)
- `data/extra/` — a small 4-building dataset and a deliberately disconnected one for testing

## Disjoint Set Union (DSU)

Tracks which buildings are already in the same connected group.

- `find(x)` — returns the group's root, with **path compression**
- `union(a, b)` — merges two groups using **union by rank**; returns `False` if they were already joined (a cycle would form)

## Kruskal's Algorithm

Greedy: always take the cheapest edge that does not create a cycle.

**Steps**

1. Put every building in its own DSU set.
2. Sort all edges by weight.
3. Take edges from cheapest to most expensive.
4. If the edge's endpoints are in different sets, add it to the MST and union them; otherwise skip it (cycle).
5. Stop when `V - 1` edges are chosen.
6. If fewer than `V - 1` edges could be chosen, the graph is **disconnected** — an error is reported (only a partial forest is shown, clearly labelled).

`kruskal_mst()` returns `{"edges", "total_cost", "is_connected", "components", "message"}`.

## Complexity

| Part | Time |
| --- | --- |
| Sorting edges | O(E log E) |
| DSU find/union | ≈ O(α(V)) amortized each (α = inverse Ackermann, practically constant) |
| **Overall Kruskal** | **O(E log E)** (equivalently O(E log V)) |

**Space:** O(V + E) — edge list O(E), DSU parent/rank arrays O(V), MST output O(V).

## Folder Structure

```
sunidhi_kruskal/
├── data/ (buildings.csv, connections.csv, extra/)
├── src/  (dsu.py, graph.py, kruskal.py)
├── tests/ (test_kruskal.py)
├── main.py
├── README.md
└── requirements.txt
```

## How to Run

```bash
python main.py                                   # main campus dataset
python main.py data/extra/disconnected_buildings.csv data/extra/disconnected_connections.csv
python -m unittest discover -s tests -v          # run tests
```

## Sample Output

```
========================================
MINIMUM-COST CAMPUS NETWORK
Kruskal's Algorithm
========================================

Buildings: 10
Possible Connections: 18

Selected MST Connections:
CSE Block -> ECE Block : ₹5,250
Library -> CSE Block : ₹6,000
Administrative Block -> Library : ₹6,750
ECE Block -> Mechanical Block : ₹7,500
Library -> Auditorium : ₹8,250
Main Gate -> Administrative Block : ₹9,000
CSE Block -> Cafeteria : ₹9,750
Hostel -> Sports Complex : ₹12,750
Cafeteria -> Hostel : ₹13,500
----------------------------------------
Total Minimum Cost: ₹78,750
----------------------------------------
Graph Connected: Yes
MST completed successfully.
```

## Test Cases (`tests/test_kruskal.py`)

1. Normal connected campus graph (9 edges, ₹78,750, all buildings covered)
2. Small hand-verifiable graph (+ small CSV dataset)
3. Disconnected graph (in memory and from CSV) -> `is_connected = False` and error message
4. Multiple edges with equal weights (V-1 edges, no cycle, correct cost)
5. Cycle where the expensive edge must be rejected
6. Extras: DSU behaviour, single/empty graph, unknown vertex
# Prim's Algorithm Module 

Minimum-Cost Network for Connecting Multiple Campus Buildings – **Prim's MST** implementation in Python.
**Role:** Member 2 — Niharika Jha

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
