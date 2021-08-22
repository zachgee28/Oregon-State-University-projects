# Course: CS261 - Data Structures
# Author: Zach Gee
# Assignment: 6
# Description: Implement an undirected graph class

from collections import deque

class UndirectedGraph:
    """
    Class to implement undirected graph
    - duplicate edges not allowed
    - loops not allowed
    - no edge weights
    - vertex names are strings
    """

    def __init__(self, start_edges=None):
        """
        Store graph info as adjacency list
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self.adj_list = dict()

        # populate graph with initial vertices and edges (if provided)
        # before using, implement add_vertex() and add_edge() methods
        if start_edges is not None:
            for u, v in start_edges:
                self.add_edge(u, v)

    def __str__(self):
        """
        Return content of the graph in human-readable form
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = [f'{v}: {self.adj_list[v]}' for v in self.adj_list]
        out = '\n  '.join(out)
        if len(out) < 70:
            out = out.replace('\n  ', ', ')
            return f'GRAPH: {{{out}}}'
        return f'GRAPH: {{\n  {out}}}'

    # ------------------------------------------------------------------ #

    def add_vertex(self, v: str) -> None:
        """
        Add new vertex to the graph
        """
        if v not in self.adj_list:
            self.adj_list[v] = []

    def add_edge(self, u: str, v: str) -> None:
        """
        Add edge to the graph
        """
        if u != v:
            self.add_vertex(u)
            self.add_vertex(v)
            if v not in self.adj_list[u]:
                self.adj_list[u].append(v)
            if u not in self.adj_list[v]:
                self.adj_list[v].append(u)

    def remove_edge(self, v: str, u: str) -> None:
        """
        Remove edge from the graph
        """
        if v in self.adj_list and u in self.adj_list:
            if v in self.adj_list[u]:
                self.adj_list[u].remove(v)
            if u in self.adj_list[v]:
                self.adj_list[v].remove(u)

    def remove_vertex(self, v: str) -> None:
        """
        Remove vertex and all connected edges
        """
        if v in self.adj_list:
            for vertex in self.adj_list:
                if v in self.adj_list[vertex]:
                    self.adj_list[vertex].remove(v)
            self.adj_list.pop(v)

    def get_vertices(self) -> []:
        """
        Return list of vertices in the graph (any order)
        """
        v_list = []
        for v in self.adj_list:
            v_list.append(v)
        return v_list

    def get_edges(self) -> []:
        """
        Return list of edges in the graph (any order)
        """
        edges = []
        for v in self.adj_list:
            for w in self.adj_list[v]:
                if (v, w) not in edges and (w, v) not in edges:
                    edges.append((v, w))
        return edges

    def is_valid_path(self, path: []) -> bool:
        """
        Return true if provided path is valid, False otherwise
        """
        if len(path) > 0:
            prev_v = path[0]
            if prev_v not in self.adj_list:
                return False
        else:
            return True
        for i in range(1,len(path)):
            if path[i] in self.adj_list[prev_v]:
                prev_v = path[i]
            else:
                return False
        return True

    def dfs(self, v_start, v_end=None) -> []:
        """
        Return list of vertices visited during DFS search
        Vertices are picked in alphabetical order
        """
        visited = []
        if v_start not in self.adj_list:
            return visited
        dfs_deque = deque()
        dfs_deque.append(v_start)
        while len(dfs_deque) > 0:
            curr_v = dfs_deque.pop()
            if curr_v not in visited:
                visited.append(curr_v)
                if curr_v == v_end:
                    return visited
            self.adj_list[curr_v].sort(reverse=True)   # sorts the vertices of curr_v in reverse alphabetical order
            for v in self.adj_list[curr_v]:
                if v not in visited:
                    dfs_deque.append(v)
        return visited

    def bfs(self, v_start, v_end=None) -> []:
        """
        Return list of vertices visited during BFS search
        Vertices are picked in alphabetical order
        """
        visited = []
        if v_start not in self.adj_list:
            return visited
        bfs_deque = deque()
        bfs_deque.append(v_start)
        while len(bfs_deque) > 0:
            curr_v = bfs_deque.popleft()
            if curr_v not in visited:
                visited.append(curr_v)
                if curr_v == v_end:
                    return visited
            self.adj_list[curr_v].sort()  # sorts the vertices of curr_v in alphabetical order
            for v in self.adj_list[curr_v]:
                if v not in visited:
                    bfs_deque.append(v)
        return visited

    def count_connected_components(self):
        """
        Return number of connected components in the graph
        """
        to_visit = []
        for key in self.adj_list:
            to_visit.append(key)
        bfs_deque = deque()
        visited = []
        count = 0
        while len(to_visit) > 0:
            from_v = to_visit.pop()
            visited.append(from_v)
            count += 1
            bfs_deque.append(from_v)
            while len(bfs_deque) > 0:
                curr_v = bfs_deque.popleft()
                if curr_v not in visited:
                    visited.append(curr_v)
                    to_visit.remove(curr_v)
                for v in self.adj_list[curr_v]:
                    if v not in visited:
                        bfs_deque.append(v)
        return count

    def has_cycle(self):
        """
        Return True if graph contains a cycle, False otherwise
        """
        to_visit = []
        for key in self.adj_list:
            to_visit.append(key)
        dfs_deque = deque()
        while len(to_visit) > 0:
            visited = []
            from_v = to_visit.pop()
            visited.append(from_v)
            dfs_deque.append(from_v)
            loop_visited = []
            while len(dfs_deque) > 0:
                curr_v = dfs_deque.pop()
                if curr_v in loop_visited:
                    return True
                else:
                    loop_visited.append(curr_v)
                if curr_v not in visited:
                    visited.append(curr_v)
                    to_visit.remove(curr_v)
                for v in self.adj_list[curr_v]:
                    if v not in visited:
                        dfs_deque.append(v)
        return False


if __name__ == '__main__':

    print("\nPDF - method add_vertex() / add_edge example 1")
    print("----------------------------------------------")
    g = UndirectedGraph()
    print(g)

    for v in 'ABCDE':
        g.add_vertex(v)
    print(g)

    g.add_vertex('A')
    print(g)

    for u, v in ['AB', 'AC', 'BC', 'BD', 'CD', 'CE', 'DE', ('B', 'C')]:
        g.add_edge(u, v)
    print(g)


    print("\nPDF - method remove_edge() / remove_vertex example 1")
    print("----------------------------------------------------")
    g = UndirectedGraph(['AB', 'AC', 'BC', 'BD', 'CD', 'CE', 'DE'])
    g.remove_vertex('DOES NOT EXIST')
    g.remove_edge('A', 'B')
    g.remove_edge('X', 'B')
    print(g)
    g.remove_vertex('D')
    print(g)


    print("\nPDF - method get_vertices() / get_edges() example 1")
    print("---------------------------------------------------")
    g = UndirectedGraph()
    print(g.get_edges(), g.get_vertices(), sep='\n')
    g = UndirectedGraph(['AB', 'AC', 'BC', 'BD', 'CD', 'CE'])
    print(g.get_edges(), g.get_vertices(), sep='\n')


    print("\nPDF - method is_valid_path() example 1")
    print("--------------------------------------")
    g = UndirectedGraph(['AB', 'AC', 'BC', 'BD', 'CD', 'CE', 'DE'])
    test_cases = ['ABC', 'ADE', 'ECABDCBE', 'ACDECB', '', 'D', 'Z']
    for path in test_cases:
        print(list(path), g.is_valid_path(list(path)))


    print("\nPDF - method dfs() and bfs() example 1")
    print("--------------------------------------")
    edges = ['AE', 'AC', 'BE', 'CE', 'CD', 'CB', 'BD', 'ED', 'BH', 'QG', 'FG']
    g = UndirectedGraph(edges)
    test_cases = 'ABCDEGH'
    for case in test_cases:
        print(f'{case} DFS:{g.dfs(case)} BFS:{g.bfs(case)}')
    print('-----')
    for i in range(1, len(test_cases)):
        v1, v2 = test_cases[i], test_cases[-1 - i]
        print(f'{v1}-{v2} DFS:{g.dfs(v1, v2)} BFS:{g.bfs(v1, v2)}')


    print("\nPDF - method count_connected_components() example 1")
    print("---------------------------------------------------")
    edges = ['AE', 'AC', 'BE', 'CE', 'CD', 'CB', 'BD', 'ED', 'BH', 'QG', 'FG']
    g = UndirectedGraph(edges)
    test_cases = (
        'add QH', 'remove FG', 'remove GQ', 'remove HQ',
        'remove AE', 'remove CA', 'remove EB', 'remove CE', 'remove DE',
        'remove BC', 'add EA', 'add EF', 'add GQ', 'add AC', 'add DQ',
        'add EG', 'add QH', 'remove CD', 'remove BD', 'remove QG')
    for case in test_cases:
        command, edge = case.split()
        u, v = edge
        g.add_edge(u, v) if command == 'add' else g.remove_edge(u, v)
        print(g.count_connected_components(), end=' ')
    print()


    print("\nPDF - method has_cycle() example 1")
    print("----------------------------------")
    edges = ['AE', 'AC', 'BE', 'CE', 'CD', 'CB', 'BD', 'ED', 'BH', 'QG', 'FG']
    g = UndirectedGraph(edges)
    test_cases = (
        'add QH', 'remove FG', 'remove GQ', 'remove HQ',
        'remove AE', 'remove CA', 'remove EB', 'remove CE', 'remove DE',
        'remove BC', 'add EA', 'add EF', 'add GQ', 'add AC', 'add DQ',
        'add EG', 'add QH', 'remove CD', 'remove BD', 'remove QG',
        'add FG', 'remove GE')
    for case in test_cases:
        command, edge = case.split()
        u, v = edge
        g.add_edge(u, v) if command == 'add' else g.remove_edge(u, v)
        print('{:<10}'.format(case), g.has_cycle())
