import random
import itertools
import copy
import sys
import traceback
import time
import functools
import time
import signal
import errno

from util import Vertex
from util import Edge
from util import Graph

class TimeoutError(Exception):
    pass

class Timeout:
    def __init__(self, seconds=0.49, error_message="Timeout of {0} seconds hit"):
        self.seconds = seconds
        self.error_message = error_message.format(seconds)
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# TO DO
class PercolationPlayer:

    # COLORING FUNCTIONS

    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == -1
    def ChooseVertexToColor(graph, player):
        try:
            with Timeout():
                memoized_colorer = memoize(PercolationPlayer.ChooseVertexToColor_helper)
                result = memoized_colorer(PercolationPlayer.Graph_to_Hashable_Graph(graph), player)
                return result[0]
        except TimeoutError as e:
            undecideds = [[v,len(PercolationPlayer.IncidentEdges(graph, v))] for v in graph.V if v.color == -1]
            undecideds.sort(key = lambda x: -x[1])
            chosen_vertex = undecideds[0][0]
            return chosen_vertex

    # Recursive helper
    def ChooseVertexToColor_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == -1]
        p_wins = []
        for v in my_moves:
            new_graph = PercolationPlayer.Color_immutable(graph, v, player)
            # Then I really only had one option, since I must be second player
            if len(my_moves)==1:
                return (v, PercolationPlayer.ChooseVertexToColor_helper_2ndplayer(new_graph, 1))
            your_moves = [v for v in new_graph.V if v.color == -1]
            p_win = 0
            for u in your_moves:
                new_new_graph = PercolationPlayer.Color_immutable(new_graph, u, 1-player)
                if len([v for v in new_new_graph.V if v.color == -1]) == 0:
                    p_win = p_win + PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
                else:
                    p_win = p_win + PercolationPlayer.ChooseVertexToColor_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves)
            p_wins.append((v, p_win))
        p_wins.sort(key = lambda x: -x[1])
        return p_wins[0]

    # Helper method for ChooseVertexToColor_helper
    # Called to determine how good a colored graph is as a starting point, if we're second player (player 1)
    def ChooseVertexToColor_helper_2ndplayer(graph, player):
        your_moves = [v for v in graph.V if v.color==1-player]
        p = 0
        for v in your_moves:
            new_graph = PercolationPlayer.Percolate_immutable(graph, v)
            if new_graph == None:
                p+=0
            elif len([v for v in new_graph.V if v.color == player])==0:
                p+=0
            else:
                p += PercolationPlayer.ChooseVertexToRemove_helper(new_graph, player)[1]
        return p/len(your_moves)


    # REMOVING FUNCTIONS

    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == player
    def ChooseVertexToRemove(graph, player):
        try:
            with Timeout():
                memoized_remover = memoize(PercolationPlayer.ChooseVertexToRemove_helper)
                result = memoized_remover(PercolationPlayer.Graph_to_Hashable_Graph(graph), player)
                return result[0]
        except TimeoutError as e:
            offensive=1
            defensive=0
            choices = [[v,offensive * len(PercolationPlayer.IncidentDiffColorEdges(graph, v)) - defensive * len(PercolationPlayer.IncidentSameColorEdges(graph, v)) ] for v in graph.V if v.color == player]
            choices.sort(key = lambda x: -x[1])
            chosen_vertex = choices[0][0]
            return chosen_vertex

    # Recursive helper. Returns a tuple, composed of the vertex to be removed
    # followed by the probability that I win
    def ChooseVertexToRemove_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == player]
        p_wins = []
        # Consider each of my possible moves
        for v in my_moves:
            new_graph = PercolationPlayer.Percolate_immutable(graph, v)
            # Check if the game is over (if and elif statements). If it is, I win
            if new_graph == None:
                return (v, 1)
            elif len([v for v in new_graph.V if v.color == (player+1)%2])==0:
                return (v, 1)
            your_moves = [v for v in new_graph.V if v.color == ((player+1)%2)]
            # Probability that I win
            # Note that if p_win = 1, then it's a win for my player, so I win
            # Otherwise, it's technically a win for the other player, but he might mess up, so I might still be able to win
            p_win = 0
            # Consider each of the other player's moves in response
            for u in your_moves:
                new_new_graph = PercolationPlayer.Percolate_immutable(new_graph, u)
                # Check if the game is over (if and elif statements). If it is, I lose
                if new_new_graph == None:
                    p_win += 0
                elif len([v for v in new_new_graph.V if v.color == player])==0:
                    p_win += 0
                else:
                    p_win = p_win + PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves) # Average of the win probabilities for each move, since the other player chooses randomly
            p_wins.append((v, p_win))
        p_wins.sort(key = lambda x: -x[1])
        return p_wins[0]


    # MISCELLANEOUS/HELPER FUNCTIONS

    def GetNeighbors(graph, v):
        neighbors = []
        for edge in PercolationPlayer.IncidentEdges(graph, v):
            if edge.a == v:
                neighbors.append(edge.b)
            else:
                neighbors.append(edge.a)
        return neighbors

    def IncidentEdges(graph, v):
        return [e for e in graph.E if (e.a == v or e.b == v)]

    def IncidentSameColorEdges(graph, v):
        return [e for e in graph.E if ((e.a == v and e.b.color == v.color) or (e.b == v and e.a.color == v.color))]

    def IncidentDiffColorEdges(graph, v):
        return [e for e in graph.E if ((e.a == v and e.b.color != v.color) or (e.b == v and e.a.color != v.color))]


    # EVERYTHING BELOW USES HASHABLE GRAPH/EDGE/VERTEX (EXCEPT Graph_to_Hashable_Graph)

    # Removes the given vertex v from the graph, as well as the edges attached to it.
    # Removes all isolated vertices from the graph as well.
    # Takes in hashable graph, hashable vertex
    def Percolate_immutable(graph, v):
        new_edges = copy.deepcopy(graph.E)
        new_vertices = copy.deepcopy(graph.V)
        edges_to_delete = set(PercolationPlayer.Find_IncidentEdges(new_edges, v))
        new_edges.difference_update(edges_to_delete)
        vertex_to_delete = None
        for vertex in new_vertices:
            if vertex.index == v.index:
                vertex_to_delete = vertex
        new_vertices.remove(vertex_to_delete)
        to_remove = {u for u in new_vertices if len(PercolationPlayer.Find_IncidentEdges(new_edges, u)) == 0}
        new_vertices.difference_update(to_remove)
        return Hashable_Graph(new_vertices, new_edges)

    def Color_immutable(graph, v, color):
        new_vertices = set()
        for vertex in graph.V:
            if vertex.index!= v.index:
                new_vertices.add(Hashable_Vertex(vertex.index, vertex.color))
        new_vertex = Hashable_Vertex(v.index, color)
        new_vertices.add(new_vertex)
        new_edges = copy.deepcopy(graph.E)
        return Hashable_Graph(new_vertices, new_edges)

    def Find_IncidentEdges(edges, v):
        return [e for e in edges if e.a.index==v.index or e.b.index == v.index]

    def Graph_to_Hashable_Graph(graph):
        new_vertices = set()
        new_edges = set()
        for v in graph.V:
            new_vertices.add(Hashable_Vertex(v.index, v.color))
        for e in graph.E:
            new_edges.add(Hashable_Edge(e.a, e.b))
        return Hashable_Graph(new_vertices, new_edges)

class Hashable_Vertex:
    def __init__(self, index, color=-1):
        self.index = index
        self.color = color

    def __repr__(self):
        if self.color == -1:
            return "Vertex({0})".format(self.index)
        else:
            return "Vertex({0}, {1})".format(self.index, self.color)

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.index==other.index) and (self.color==other.color)
        else:
            return False

    def __hash__(self):
        return hash(self.index) ^ hash(self.color)

class Hashable_Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "Edge({0}, {1})".format(self.a, self.b)

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.a==other.a and self.b==other.b) or (self.a==other.b and self.b==other.a)
        else:
            return False

    def __hash__(self):
        return hash(self.a) ^ hash(self.b)

class Hashable_Graph:
    def __init__(self, v, e):
        self.V = set(v)
        self.E = set(e)

    def __repr__(self):
        return "Graph({0}, {1})".format(self.V, self.E)

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.V==other.V) and (self.E==other.E)
        else:
            return False

    def __hash__(self):
        vertices = list(self.V)
        vertices.sort(key = lambda x: x.index)
        vertex_hash = 0
        for vertex in vertices:
            vertex_hash = 3*vertex_hash + vertex.color+1
        edges = list(self.E)
        for edge in edges:
            if edge.a.index > edge.b.index:
                edge.a, edge.b = edge.b, edge.a
        edges.sort(key = lambda x: (x.a.index, x.b.index))
        edge_hash = 0
        for edge in edges:
            edge_hash = edge_hash + 2**(edge.a.index + len(vertices)*edge.b.index)
        return vertex_hash + edge_hash*(3**(len(vertices)+1))

    # Gets a vertex with given index if it exists, else return None.
    def GetVertex(self, i):
        for v in self.V:
            if v.index == i:
                return v
        return None

    # Returns the incident edges on a vertex.
    def IncidentEdges(self, v):
        return [e for e in self.E if (e.a == v or e.b == v)]

def memoize (f):
    cache = dict()
    def memoized_f(*args):
        if args in cache:
            return cache[args]
        result = f(*args)
        cache[args] = result
        return result
    return memoized_f
