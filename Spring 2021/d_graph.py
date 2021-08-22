# Course: CS261 - Data Structures
# Author: Zach Gee
# Assignment: 6
# Description: Implement a directed graph class

import heapq
from collections import deque


class DirectedGraph:
    """
    Class to implement directed weighted graph
    - duplicate edges not allowed
    - loops not allowed
    - only positive edge weights
    - vertex names are integers
    """

    def __init__(self, start_edges=None):
        """
        Store graph info as adjacency matrix
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self.v_count = 0
        self.adj_matrix = []

        # populate graph with initial vertices and edges (if provided)
        # before using, implement add_vertex() and add_edge() methods
        if start_edges is not None:
            v_count = 0
            for u, v, _ in start_edges:
                v_count = max(v_count, u, v)
            for _ in range(v_count + 1):
                self.add_vertex()
            for u, v, weight in start_edges:
                self.add_edge(u, v, weight)

    def __str__(self):
        """
        Return content of the graph in human-readable form
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if self.v_count == 0:
            return 'EMPTY GRAPH\n'
        out = '   |'
        out += ' '.join(['{:2}'.format(i) for i in range(self.v_count)]) + '\n'
        out += '-' * (self.v_count * 3 + 3) + '\n'
        for i in range(self.v_count):
            row = self.adj_matrix[i]
            out += '{:2} |'.format(i)
            out += ' '.join(['{:2}'.format(w) for w in row]) + '\n'
        out = f"GRAPH ({self.v_count} vertices):\n{out}"
        return out

    # ------------------------------------------------------------------ #

    def add_vertex(self) -> int:
        """
        Adds vertex to graph and returns the number of vertices in graph after addition
        """
        new_vertex_list = []
        for i in range(self.v_count):
            new_vertex_list.append(0)
        self.adj_matrix.append(new_vertex_list)
        for v in self.adj_matrix:
            v.append(0)
        self.v_count += 1
        return self.v_count

    def add_edge(self, src: int, dst: int, weight=1) -> None:
        """
        Adds an edge between the provided vertex indices
        """
        if 0 <= src < self.v_count and 0 <= dst < self.v_count and weight > 0 and src != dst:
            self.adj_matrix[src][dst] = weight

    def remove_edge(self, src: int, dst: int) -> None:
        """
        Removes edge between the provided vertex indices
        """
        if 0 <= src < self.v_count and 0 <= dst < self.v_count:
            self.adj_matrix[src][dst] = 0

    def get_vertices(self) -> []:
        """
        Returns list of graph's vertices
        """
        return [x for x in range(self.v_count)]

    def get_edges(self) -> []:
        """
        Returns list of graph's edges in the form of tuples: (source vertex, destination vertex, weight)
        """
        edge_list = []
        for i in range(self.v_count):
            for j in range(self.v_count):
                if self.adj_matrix[i][j] > 0:
                    edge_list.append((i,j,self.adj_matrix[i][j]))
        return edge_list

    def is_valid_path(self, path: []) -> bool:
        """
        Returns True if the sequences of vertices in the provided path has the necessary edges to be valid.
        """
        if len(path) > 0:
            prev_v = path[0]
        else:
            return True
        for j in range(1,len(path)):
            if self.adj_matrix[prev_v][path[j]] == 0:
                return False
            prev_v = path[j]
        return True

    def dfs(self, v_start, v_end=None) -> []:
        """
        Performs a depth-first search in the graph from v-start and returns a list of vertices visited during the
        search, in the order they were visited. When ambiguous, vertices are picked in ascending order.
        """
        visited = []
        if v_start >= self.v_count or v_start < 0:
            return visited
        dfs_deque = deque()
        dfs_deque.append(v_start)
        while len(dfs_deque) > 0:
            curr_v = dfs_deque.pop()
            if curr_v not in visited:
                visited.append(curr_v)
                if curr_v == v_end:
                    return visited
            for j in range(self.v_count-1,-1,-1):
                if self.adj_matrix[curr_v][j] > 0:
                    if j not in visited:
                        dfs_deque.append(j)
        return visited

    def bfs(self, v_start, v_end=None) -> []:
        """
        Performs a breadth-first search in the graph from v-start and returns a list of vertices visited during the
        search, in the order they were visited. When ambiguous, vertices are picked in ascending order.
        """
        visited = []
        if v_start >= self.v_count or v_start < 0:
            return visited
        bfs_deque = deque()
        bfs_deque.append(v_start)
        while len(bfs_deque) > 0:
            curr_v = bfs_deque.popleft()
            if curr_v not in visited:
                visited.append(curr_v)
                if curr_v == v_end:
                    return visited
            for j in range(self.v_count):
                if self.adj_matrix[curr_v][j] > 0:
                    if j not in visited:
                        bfs_deque.append(j)
        return visited

    def has_cycle(self):
        """
        Returns True if there is at least one cycle in the graph. If the graph is acyclic, returns False.
        """
        to_visit = [x for x in range(self.v_count)]   # important to keep track of in cases of disconnected subgraphs
        dfs_deque = deque()
        visited = []
        while len(to_visit) > 0:
            from_v = to_visit.pop()
            dfs_deque.append(from_v)
            loop_visited = [{'count': 1}]
            while len(dfs_deque) > 0:
                loop_visited[-1]['count'] -= 1
                while loop_visited[-1]['count'] < 0:
                    loop_visited.pop()
                    if len(loop_visited) == 0:
                        break
                    while type(loop_visited[-1]) is not dict:
                        loop_visited.pop()
                    loop_visited[-1]['count'] -= 1
                curr_v = dfs_deque.pop()
                visited.append(curr_v)
                if curr_v in loop_visited:
                    return True
                else:
                    loop_visited.append(curr_v)
                if curr_v not in visited:
                    visited.append(curr_v)
                    to_visit.remove(curr_v)
                # keep a count of vertices connected to curr_v that are now going to be added to dfs_deque.
                # this count is used to determine when we need to remove loop_visited vertices.
                subsequent_v_cnt = {'count': 0}
                for j in range(self.v_count):
                    if self.adj_matrix[curr_v][j] > 0:
                        if j not in dfs_deque:
                            dfs_deque.append(j)
                            subsequent_v_cnt['count'] += 1
                loop_visited.append(subsequent_v_cnt)
        return False

    def dijkstra(self, src: int) -> []:
        """
        Implements the Dijkstra algorithm to compute the length of the shortest path from a given vertex to all
        other vertices in the graph. Returns a list with one value per each vertex in the graph, where value at
        index 0 is the length of the shortest path from src to vertex 0, value at index 1 is the length of the
        shortest path from src to vertex 1 etc. If a certain vertex is not reachable from SRC, returns infinity.
        """
        dist_to_v = {}
        priority_queue = [(0, src)]      # vertex as a tuple (value, key) = (distance, vertex)
        while len(priority_queue) > 0:
            v = heapq.heappop(priority_queue)
            if v[1] not in dist_to_v:
                dist_to_v[v[1]] = v[0]
                for i, v_dist in enumerate(self.adj_matrix[v[1]]):
                    if v_dist > 0:
                        heapq.heappush(priority_queue, (v[0] + v_dist, i))
        return_list = []
        for i in range(self.v_count):
            if i in dist_to_v:
                return_list.append(dist_to_v[i])
            else:
                return_list.append(float('inf'))
        return return_list


if __name__ == '__main__':

    print("\nPDF - method add_vertex() / add_edge example 1")
    print("----------------------------------------------")
    g = DirectedGraph()
    print(g)
    for _ in range(5):
        g.add_vertex()
    print(g)

    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    for src, dst, weight in edges:
        g.add_edge(src, dst, weight)
    print(g)


    print("\nPDF - method get_edges() example 1")
    print("----------------------------------")
    g = DirectedGraph()
    print(g.get_edges(), g.get_vertices(), sep='\n')
    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    g = DirectedGraph(edges)
    print(g.get_edges(), g.get_vertices(), sep='\n')


    print("\nPDF - method is_valid_path() example 1")
    print("--------------------------------------")
    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    g = DirectedGraph(edges)
    test_cases = [[0, 1, 4, 3], [1, 3, 2, 1], [0, 4], [4, 0], [], [2]]
    for path in test_cases:
        print(path, g.is_valid_path(path))


    print("\nPDF - method dfs() and bfs() example 1")
    print("--------------------------------------")
    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    g = DirectedGraph(edges)
    for start in range(5):
        print(f'{start} DFS:{g.dfs(start)} BFS:{g.bfs(start)}')


    print("\nPDF - method has_cycle() example 1")
    print("----------------------------------")
    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    g = DirectedGraph(edges)

    edges_to_remove = [(3, 1), (4, 0), (3, 2)]
    for src, dst in edges_to_remove:
        g.remove_edge(src, dst)
        print(g.get_edges(), g.has_cycle(), sep='\n')

    edges_to_add = [(4, 3), (2, 3), (1, 3), (4, 0)]
    for src, dst in edges_to_add:
        g.add_edge(src, dst)
        print(g.get_edges(), g.has_cycle(), sep='\n')
    print('\n', g)

    print("\nPDF - method has_cycle() example A")
    print("----------------------------------")
    edges = [(0, 8, 10), (2, 3, 6), (2, 8, 14), (5, 2, 19),
             (5, 3, 14), (5, 11, 9), (6, 2, 1), (9, 3, 1),
             (9, 5, 4), (9, 12, 11), (11, 6, 7), (11, 10, 11)]
    g = DirectedGraph(edges)
    print(g.get_edges())
    print(g.has_cycle())
    print('\n', g)

    print("\nPDF - method has_cycle() example B")
    print("----------------------------------")
    edges = [(2,3,16), (4,8,7), (4,10,18), (5,8,6), (7,11,9),
             (8,0,18), (8,1,7), (8,9,4), (10,5,11), (11,10,18),
             (11,12,8), (12,3,16), (12,4,4)]
    g = DirectedGraph(edges)
    print(g.get_edges())
    print(g.has_cycle())
    print('\n', g)

    print("\nPDF - dijkstra() example 1")
    print("--------------------------")
    edges = [(0, 1, 10), (4, 0, 12), (1, 4, 15), (4, 3, 3),
             (3, 1, 5), (2, 1, 23), (3, 2, 7)]
    g = DirectedGraph(edges)
    for i in range(5):
        print(f'DIJKSTRA {i} {g.dijkstra(i)}')
    g.remove_edge(4, 3)
    print('\n', g)
    for i in range(5):
        print(f'DIJKSTRA {i} {g.dijkstra(i)}')
