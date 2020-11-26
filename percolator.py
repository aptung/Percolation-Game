import random
import itertools
import copy
import sys
import traceback
import timeit
import functools

from util import Vertex
from util import Edge
from util import Graph

# Removes the given vertex v from the graph, as well as the edges attached to it.
# Removes all isolated vertices from the graph as well.
def Percolate(graph, v):
    # Get attached edges to this vertex, remove them.
    for e in graph.IncidentEdges(v):
        if e not in graph.E:
            print("oops")
        else:
            graph.E.remove(e)
    # Remove this vertex.
    if v not in graph.V:
        print(v)
        print(hash(v))
        for x in graph.V:
            if hash(x)==hash(v) and x==v:
                print("yay")
        print(graph.V)
        print(v in graph.V)
        print(any(v is e or v==e for e in graph.V))
    graph.V.remove(v)
    # Remove all isolated vertices.
    to_remove = {u for u in graph.V if len(graph.IncidentEdges(u)) == 0}
    graph.V.difference_update(to_remove)

# This is the main game loop.
def PlayGraph(s, t, graph):
    players = [s, t]
    active_player = 0

    # Phase 1: Coloring Phase
    while any(v.color == -1 for v in graph.V):
        # First, try to just *run* the player's code to get their vertex.
        try:
            chosen_vertex = players[active_player].ChooseVertexToColor(copy.copy(graph), active_player)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return 1 - active_player
        # Next, check that their output was reasonable.
        try:
            original_vertex = graph.GetVertex(chosen_vertex.index)
            if not original_vertex:
                return 1 - active_player
            if original_vertex.color != -1:
                return 1 - active_player
            # If output is reasonable, color this vertex.
            original_vertex.color = active_player
        # Only case when this should fire is if chosen_vertex.index does not exist or similar error.
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return 1 - active_player
        #print(graph) #FIX
        # Swap current player.
        active_player = 1 - active_player

    # Check that all vertices are colored now.
    assert all(v.color != -1 for v in graph.V)
    #FIX
    #print("Ok, finished coloring. The graph is")
    #print(graph)
    # Phase 2: Removal phase
    # Continue while both players have vertices left to remove.
    while len([v for v in graph.V if v.color == active_player]) > 0:
        # First, try to just *run* the removal code.
        try:
            chosen_vertex = players[active_player].ChooseVertexToRemove(copy.copy(graph), active_player)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return 1 - active_player
        # Next, check that their output was reasonable.
        try:
            original_vertex = graph.GetVertex(chosen_vertex.index)
            if not original_vertex:
                return 1 - active_player
            if original_vertex.color != active_player:
                return 1 - active_player
            # If output is reasonable, remove ("percolate") this vertex + edges attached to it, as well as isolated vertices.
            Percolate(graph, original_vertex)
        # Only case when this should fire is if chosen_vertex.index does not exist or similar error.
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return 1 - active_player
        #print(graph) #FIX
        # Swap current player
        active_player = 1 - active_player

    # Winner is the non-active player.
    return 1 - active_player


# This method generates a binomial random graph with 2k vertices
# having probability p of an edge between each pair of vertices.
def BinomialRandomGraph(k, p):
    v = {Vertex(i) for i in range(2 * k)}
    e = {Edge(a, b) for (a, b) in itertools.combinations(v, 2) if random.random() < p}
    return Graph(v, e)


# This method creates and plays a number of random graphs using both passed in players.
def PlayBenchmark(p1, p2, iters):
    graphs = (
    # range of number of vertices: 2-40 [FIX LATER]
        BinomialRandomGraph(random.randint(1, 20), random.random())
        for _ in range(iters)
    )
    wins = [0, 0]
    for graph in graphs:
        g1 = copy.deepcopy(graph)
        g2 = copy.deepcopy(graph)
        # Each player gets a chance to go first on each graph.
        winner_a = PlayGraph(p1, p2, g1)
        wins[winner_a] += 1
        print(wins) #FIX
        winner_b = PlayGraph(p2, p1, g2)
        wins[1-winner_b] += 1
        print(wins) #FIX
    return wins


# This is a player that plays a legal move at random.
class RandomPlayer:
    # These are "static methdods" - note there's no "self" parameter here.
    # These methods are defined on the blueprint/class definition rather than
    # any particular instance.
    def ChooseVertexToColor(graph, active_player):
        return random.choice([v for v in graph.V if v.color == -1])

    def ChooseVertexToRemove(graph, active_player):
        return random.choice([v for v in graph.V if v.color == active_player])

# TO DO
class PercolationPlayer:
    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == -1
    def ChooseVertexToColor(graph, player):
        #if len(graph.V)>=6:
            #print("Too hard!")
            return random.choice([v for v in graph.V if v.color == -1])
        #print(PercolationPlayer.ChooseVertexToColor_helper(graph, player)[1])
        #print("Coloring")
        #return PercolationPlayer.ChooseVertexToColor_helper(graph, player)[0]

    def ChooseVertexToColor_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == -1]
        p_wins = []
        for v in my_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = new_graph.GetVertex(v.index)
            original_vertex.color = player
            # Then I really only had one option, since I must be second player
            if len(my_moves)==1:
                return (v, PercolationPlayer.ChooseVertexToColor_helper_2ndplayer(new_graph, 1))
            your_moves = [v for v in new_graph.V if v.color == -1]
            p_win = 0
            for u in your_moves:
                new_new_graph = copy.deepcopy(new_graph)
                original_vertex_new = new_new_graph.GetVertex(u.index)
                original_vertex_new.color = 1-player
                if len([v for v in new_new_graph.V if v.color == -1]) == 0:
                    p_win = p_win + PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
                else:
                    p_win = p_win + PercolationPlayer.ChooseVertexToColor_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves)
            p_wins.append(p_win)
        max_p = 0
        max_p_index = 0
        for i in range(len(p_wins)):
            if p_wins[i]>=max_p:
                max_p = p_wins[i]
                max_p_index = i
        return (my_moves[max_p_index], max_p)

    # Helper method for ChooseVertexToColor_helper
    # Called to determine how good a colored graph is as a starting point, if we're second player (player 1)
    def ChooseVertexToColor_helper_2ndplayer(graph, player):
        your_moves = [v for v in graph.V if v.color==1-player]
        p = 0
        for v in your_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = new_graph.GetVertex(v.index)
            Percolate(new_graph, original_vertex)
            if new_graph == None:
                p+=0
            elif len([v for v in new_graph.V if v.color == player])==0:
                p+=0
            else:
                #print(new_graph)
                p += PercolationPlayer.ChooseVertexToRemove_helper(new_graph, player)[1]
        return p/len(your_moves)

    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == player
    def ChooseVertexToRemove(graph, player):
        #if len(graph.V)>=10:
            #print("Too hard!")
            return random.choice([v for v in graph.V if v.color == player])
        #print(PercolationPlayer.ChooseVertexToRemove_helper(graph, player)[1])
        #print("Removing")
        #return PercolationPlayer.ChooseVertexToRemove_helper(graph, player)[0]

    # Recursive helper. Returns a tuple, composed of the vertex to be removed
    # followed by the probability that I win
    @functools.lru_cache(maxsize=10000)
    def ChooseVertexToRemove_helper(graph, player):
        my_moves = [v for v in graph.V if v.color == player]
        p_wins = []
        # Consider each of my possible moves
        for v in my_moves:
            new_graph = copy.deepcopy(graph)
            original_vertex = new_graph.GetVertex(v.index)
            Percolate(new_graph, original_vertex)
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
                new_new_graph = copy.deepcopy(new_graph)
                original_vertex_new = new_new_graph.GetVertex(u.index)
                Percolate(new_new_graph, original_vertex_new)
                # Check if the game is over (if and elif statements). If it is, I lose
                if new_new_graph == None:
                    p_win += 0
                elif len([v for v in new_new_graph.V if v.color == player])==0:
                    p_win += 0
                else:
                    p_win = p_win + PercolationPlayer.ChooseVertexToRemove_helper(new_new_graph, player)[1]
            p_win = p_win/len(your_moves) # Average of the win probabilities for each move, since the other player chooses randomly
            p_wins.append(p_win)

        # Find the best move (highest win probability)
        max_p = 0
        max_p_index = 0
        for i in range(len(p_wins)):
            if p_wins[i]>=max_p:
                max_p = p_wins[i]
                max_p_index = i
        return (my_moves[max_p_index], max_p)

@functools.lru_cache(maxsize=1000)
def fibbonaci(n):
    if n==0:
        return 0
    elif n==1:
        return 1
    return fibbonaci(n-1) + fibbonaci(n-2)

def memoize (f):
    cache = dict()
    def memoized_f(*args):
        if args in cache:
            return cache[args]
        result = f(*args)
        cache[args] = result
        return result
    return memoized_f

# Feel free to put any personal driver code here.
def main():
    pass

if __name__ == "__main__":
    '''graph = BinomialRandomGraph(random.randint(1, 5), random.random())
    cache = dict()
    cache[(graph, 0)] = "result"
    new_graph = copy.deepcopy(graph)
    print(graph.E==new_graph.E)
    if (new_graph, 0) in cache:
        print("yay")
    active_player = 0
    while any(v.color == -1 for v in graph.V):
        chosen_vertex = RandomPlayer.ChooseVertexToColor(copy.copy(graph), active_player)
        original_vertex = graph.GetVertex(chosen_vertex.index)
        original_vertex.color = active_player
        active_player = 1 - active_player
    print(PercolationPlayer.ChooseVertexToRemove_helper(graph, 0))
    print(PercolationPlayer.ChooseVertexToRemove_helper.cache_info())'''
    '''fibbonaci(35)
    print(fibbonaci.cache_info())'''
    # NOTE: we are not creating INSTANCES of these classes, we're defining the players
    # as the class itself. This lets us call the static methods.
    #p1 = RandomPlayer
    # Comment the above line and uncomment the next two if
    # you'd like to test the PercolationPlayer code in this repo.
    from percolator import PercolationPlayer
    p1 = PercolationPlayer
    p2 = RandomPlayer
    # Used to be 200 [FIX LATER]
    iters = 20
    wins = PlayBenchmark(p1, p2, iters)
    print(
        "Player 1 (Me): {0} Player 2 (Random): {1}".format(
            1.0 * wins[0] / sum(wins), 1.0 * wins[1] / sum(wins)
        )
    )
    print(PercolationPlayer.ChooseVertexToRemove_helper.cache_info())
