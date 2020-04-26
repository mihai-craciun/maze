from typing import List

class TreeNode:
    def __init__(self, value, parent: "TreeNode" = None):
        self.value = value
        if parent is None:
            self.parent = self
        self.children = []

    def get_root(self):
        n = self
        while n.parent != n:
            n = n.parent
        return n
    
    def add_child(self, n: "TreeNode"):
        self.children.append(n)
        n.parent = self
    
    def size(self):
        return sum([c.size() for c in self.children])

class DisjointSet:
    def __init__(self, elements: List):
        self.elements = {e: TreeNode(e) for e in elements}

    def find(self, e):
        return self.elements[e].get_root()
    
    def union(self, e, f):
        r1 = self.elements[e].get_root()
        r2 = self.elements[f].get_root()
        if r1.value == r2.value:
            return False
        if r1.size() < r2.size():
            aux = r1
            r1 = r2
            r2 = aux
        r1.add_child(r2)
        return True