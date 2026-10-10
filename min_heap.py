"""
min_heap.py - A hand-written binary Min-Heap (Priority Queue).

Used by Prim's algorithm to always pick the cheapest edge leaving the
current tree.  Implemented from scratch (no `heapq`) as required by the
project specification.

The heap is stored in a Python list:
    parent(i) = (i - 1) // 2
    left(i)   = 2 * i + 1
    right(i)  = 2 * i + 2

Entries are tuples.  Python compares tuples element by element, so the
first element (the edge weight) is the priority; the rest break ties.

Time complexity : push O(log n), pop O(log n), peek O(1)
Space complexity: O(n)
"""


class MinHeap:
    """Binary min-heap priority queue."""

    def __init__(self):
        self._data = []

    # ---- basic helpers -------------------------------------------------
    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0

    def peek(self):
        """Return (without removing) the smallest entry."""
        if not self._data:
            raise IndexError("peek from an empty heap")
        return self._data[0]

    # ---- insert --------------------------------------------------------
    def push(self, item):
        """Insert an item and restore the heap property (sift-up)."""
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def _sift_up(self, i):
        data = self._data
        while i > 0:
            parent = (i - 1) // 2
            if data[i] < data[parent]:
                data[i], data[parent] = data[parent], data[i]
                i = parent
            else:
                break

    # ---- remove-min ----------------------------------------------------
    def pop(self):
        """Remove and return the smallest entry (sift-down)."""
        data = self._data
        if not data:
            raise IndexError("pop from an empty heap")
        smallest = data[0]
        last = data.pop()          # remove last leaf
        if data:                   # heap not empty -> move leaf to root
            data[0] = last
            self._sift_down(0)
        return smallest

    def _sift_down(self, i):
        data = self._data
        n = len(data)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i
            if left < n and data[left] < data[smallest]:
                smallest = left
            if right < n and data[right] < data[smallest]:
                smallest = right
            if smallest == i:
                break
            data[i], data[smallest] = data[smallest], data[i]
            i = smallest
