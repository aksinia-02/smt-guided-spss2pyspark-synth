
from typing import Dict


class UnionFind:
    def __init__(self):
        self.parent: Dict[int, int] = {}
        self.count = 0

    # finds a root of the set in which element i belongs
    # implemetation of path compression optimization
    def find(self, i: int) -> int:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    # unites the sets that include i and j
    def union(self, i: int, j: int) -> int:
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
        return root_j

    # creates a new set with a single element i
    def make_set(self) -> int:
        new_id = len(self.parent)
        self.parent[new_id] = new_id
        return new_id

    def __repr__(self):
        return f"UnionFind(parent={', '.join(f'{k}: {v}' for k, v in self.parent.items())})"