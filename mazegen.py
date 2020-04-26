from typing import Tuple, List
from disjoint_set import DisjointSet
import random

class Maze:
    # Avaliable directions
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8
    # Offsets
    OFF_LEFT = (0, -1)
    OFF_RIGHT = (0, 1)
    OFF_UP = (-1, 0)
    OFF_DOWN = (1, 0)
    # Special markers
    EMPTY = -1

    @staticmethod
    def get_dir(i_offset: int, j_offset: int) -> int:
        pass

    @staticmethod
    def can_go(cell: int, d: int) -> bool:
        return True if cell == Maze.EMPTY else cell & d > 0

    def __init__(self, w: int=10, h: int=10
    ,start: Tuple[int ,int]=(0, 0), end: Tuple[int, int] = None, algorithm='kruskal'):
        # Inits
        self.maze = [[self.EMPTY for _ in range(w)] for _ in range(h)]
        self.w = w
        self.h = h
        self.start = start
        self.algorithm = algorithm
        if end is None:
            end = (h-1, w-1)
        self.end = end
        self.compute_aux_maps()
    
    def get_avail_neighbour_offset(self, y: int, x: int) -> List[Tuple[int, int]]:
        nbs = []
        for (i, j) in self.OFF_DIR.keys():
            if y + i < 0 or y + i >= self.h or x + j < 0 or x + j >= self.w:
                continue
            if self.maze[y + i][x + j] == self.EMPTY:
                nbs.append((i, j))
        return nbs

    def set_dir(self, y: int, x: int, d: int):
        self.maze[y][x] = max(self.maze[y][x], 0) | d
    
    def populate_dfs(self):
        stack = []
        # Run DFS, create a stack of nodes
        stack.append((self.start))
        while stack:
            i, j = stack.pop()
            # Select a new neighbor
            nbs = self.get_avail_neighbour_offset(i, j)
            if not nbs:
                continue
            random.shuffle(nbs)
            # pair the cells
            for nb in nbs:
                nd = self.OFF_DIR[nb]
                self.set_dir(i, j, nd)
                self.set_dir(i+nb[0], j+nb[1], self.OPOSITE[nd])
                stack.append((i+nb[0], j+nb[1]))

    def populate_kruskal(self):
        cells = []
        edges = []
        for i in range(self.h):
            for j in range(self.w):
                cells.append((i, j))
                if i + 1 < self.h:
                    edges.append(((i, j), (i + 1, j)))
                if j + 1 < self.w:
                    edges.append(((i, j), (i, j + 1)))
        ds = DisjointSet(cells)
        random.shuffle(edges)
        for edge in edges:
            (a, b), (c, d) = edge
            if ds.union((a, b),  (c, d)):
                nb = (c-a, d-b)
                nd = self.OFF_DIR[nb]
                self.set_dir(a, b, nd)
                self.set_dir(c, d, self.OPOSITE[nd])

    def populate(self):
        if self.algorithm == 'dfs':
            self.populate_dfs()
        elif self.algorithm == 'kruskal':
            self.populate_kruskal()
    
    def print(self):
        for line in self.maze:
            print("".join(list(map(lambda c: self.CHARS[c], line))))

    def compute_aux_maps(self):
            self.OFF_DIR = {
                self.OFF_LEFT: self.LEFT,
                self.OFF_RIGHT: self.RIGHT,
                self.OFF_UP: self.UP,
                self.OFF_DOWN: self.DOWN
            }
            # opposite
            self.OPOSITE = {
                self.LEFT: self.RIGHT,
                self.RIGHT: self.LEFT,
                self.UP: self.DOWN,
                self.DOWN: self.UP
            }
            # drawing chars
            self.CHARS = {
                self.EMPTY: " ",
                self.LEFT: "\u2578",
                self.RIGHT: "\u257a",
                self.UP: "\u2579",
                self.DOWN: "\u257b",
                self.LEFT | self.RIGHT: "\u2501",
                self.LEFT | self.UP: "\u251b",
                self.LEFT | self.DOWN: "\u2513",
                self.RIGHT | self.UP: "\u2517",
                self.RIGHT | self.DOWN: "\u250f",
                self.UP | self.DOWN: "\u2503",
                self.LEFT | self.RIGHT | self.UP: "\u253b",
                self.LEFT | self.RIGHT | self.DOWN: "\u2533",
                self.LEFT | self.UP | self.DOWN: "\u252b",
                self.RIGHT | self.UP | self.DOWN: "\u2523",
                self.LEFT | self.RIGHT | self.UP | self.DOWN: "\u254b"
            }


if __name__ == "__main__":
    maze = Maze(40, 10, algorithm='kruskal')
    maze.populate()
    maze.print()



