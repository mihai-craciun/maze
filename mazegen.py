from typing import Tuple, List
from disjoint_set import DisjointSet
from collections import deque
import random

class Maze:
    # Avaliable directions
    LEFT = 1 << 0
    RIGHT = 1 << 1
    UP = 1 << 2
    DOWN = 1 << 3

    # Offsets
    OFF_LEFT = (0, -1)
    OFF_RIGHT = (0, 1)
    OFF_UP = (-1, 0)
    OFF_DOWN = (1, 0)
    # Special markers
    EMPTY = 0
    VISITED = 1
    SOLUTION = 2

    # Algorithms
    DFS = 'dfs'
    KRUSKAL = 'kruskal'
    DIVISION = 'division'

    @staticmethod
    def get_dir(i_offset: int, j_offset: int) -> int:
        pass

    @staticmethod
    def neg_mask(d: int) -> int:
        return (Maze.LEFT | Maze.RIGHT | Maze.UP | Maze.DOWN) - d

    @staticmethod
    def can_go(cell: int, d: int) -> bool:
        return True if cell == Maze.EMPTY else cell & d > 0

    def __init__(self, w: int=10, h: int=10
    ,start: Tuple[int ,int]=(0, 0), end: Tuple[int, int] = None, algorithm='kruskal'):
        # Inits
        self.w = w
        self.h = h
        self.start = start
        self.maze = None
        self.solution = None
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
    
    def populate_recursive(self, start: Tuple[int, int], end: Tuple[int, int]):
        i1, j1 = start
        i2, j2 = end
        # if grid is less than 2x2 return
        if i2 - i1 < 2 or j2 - j1 < 2:
            return
        # choose x, y in the middle
        y = (i1 + i2) // 2
        x = (j1 + j2) // 2
        # set walls
        for j in range(j1, j2):
            self.maze[y-1][j] &= self.neg_mask(self.DOWN)
            self.maze[y][j] &= self.neg_mask(self.UP)
        for i in range(i1, i2):
            self.maze[i][x-1] &= self.neg_mask(self.RIGHT)
            self.maze[i][x] &= self.neg_mask(self.LEFT)
        # select a random index from each one of the 4 smaller walls formed by the intersection 
        walls = [
            (y, random.randint(j1, x-1), -1, 0, self.UP, self.DOWN),
            (y, random.randint(x, j2-1), -1, 0, self.UP, self.DOWN),
            (random.randint(i1, y-1), x, 0, -1, self.LEFT, self.RIGHT),
            (random.randint(y, i2-1), x, 0, -1, self.LEFT, self.RIGHT),
        ]
        # keep only 3 of them
        toremove = random.choice(walls)
        walls.remove(toremove)
        # remove selected walls
        for wall in walls:
            i, j, o1, o2, d1, d2 = wall
            self.maze[i][j] |= d1
            self.maze[i+o1][j+o2] |= d2
        # populate the maze in all 4 sub mazes generated
        self.populate_recursive((i1, j1), (y, x))
        self.populate_recursive((i1, x), (y, j2))
        self.populate_recursive((y, j1), (i2, x))
        self.populate_recursive((y, x), (i2, j2))

    def populate(self):
        self.erase()
        if self.algorithm == self.DFS:
            self.populate_dfs()
        elif self.algorithm == self.KRUSKAL:
            self.populate_kruskal()
        elif self.algorithm == self.DIVISION:
            self.populate_recursive((0, 0), (self.h, self.w))
    
    def solve(self):
        self.solution = [[self.EMPTY for _ in range(self.w)] for _ in range(self.h)]
        prevs = {self.start: None}
        queue = deque()
        queue.append(self.start)
        while queue:
            x = queue.popleft()
            if x == self.end:
                break
            i, j = x
            self.solution[i][j] = self.VISITED
            # get available neighbors
            nbs = []
            for k in self.OFF_DIR:
                (oi, oj), d = k, self.OFF_DIR[k]
                # if valid neighbor (in offsets, dir not blocked and not visited)
                if ((0 <= i + oi < self.h and 0 <= j + oj < self.w )
                and self.maze[i+oi][j+oj] & self.OPOSITE[d] > 0 and self.solution[i+oi][j+oj] == self.EMPTY and (i+oi, j+oj) not in prevs):
                    nbs.append((i+oi, j+oj))
                    prevs[(i+oi, j+oj)] = x
                # add neighbors in queue
                queue.extend(nbs)
        # calculate paths
        p = self.end
        while p is not None:
            i, j = p
            self.solution[i][j] = self.SOLUTION
            p = prevs[p]
    
    def erase(self):
        if self.algorithm == self.DIVISION:
            self.maze = [[self.LEFT | self.RIGHT | self.UP | self.DOWN for _ in range(self.w)] for _ in range(self.h)]
            self.maze[0] = [x & self.neg_mask(self.UP) for x in self.maze[0]]
            self.maze[-1] = [x & self.neg_mask(self.DOWN) for x in self.maze[-1]]
            for i in range(self.h):
                self.maze[i][0] &= self.neg_mask(self.LEFT)
                self.maze[i][-1] &= self.neg_mask(self.RIGHT)
        else:
            self.maze = [[self.EMPTY for _ in range(self.w)] for _ in range(self.h)]
    
    def print(self):
        if self.maze is None:
            return
        for i, line in enumerate(self.maze):
            char_func = lambda j_v: self.CHARS_EMPTY[j_v[1]] if (self.solution is not None 
            and self.solution[i][j_v[0]] == self.SOLUTION) else self.CHARS[j_v[1]]
            line = list(map(char_func, enumerate(line)))
            print("".join(line))

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
            self.CHARS_EMPTY = {
                self.EMPTY: " ",
                self.LEFT: "\u2555",
                self.RIGHT: "\u2558",
                self.UP: "\u2559",
                self.DOWN: "\u2556",
                self.LEFT | self.RIGHT: "\u2550",
                self.LEFT | self.UP: "\u255d",
                self.LEFT | self.DOWN: "\u2557",
                self.RIGHT | self.UP: "\u255a",
                self.RIGHT | self.DOWN: "\u2554",
                self.UP | self.DOWN: "\u2551",
                self.LEFT | self.RIGHT | self.UP: "\u2569",
                self.LEFT | self.RIGHT | self.DOWN: "\u2566",
                self.LEFT | self.UP | self.DOWN: "\u2563",
                self.RIGHT | self.UP | self.DOWN: "\u2560",
                self.LEFT | self.RIGHT | self.UP | self.DOWN: "\u256c"
            }


if __name__ == "__main__":
    maze = Maze(20, 20, algorithm=Maze.DIVISION)
    maze.populate()
    maze.solve()
    maze.print()



