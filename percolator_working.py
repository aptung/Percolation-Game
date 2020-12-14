import random
import itertools
import copy
import sys
import traceback
import time

from util_working import Vertex
from util_working import Edge
from util_working import Graph

# Removes the given vertex v from the graph, as well as the edges attached to it.
# Removes all isolated vertices from the graph as well.
def Percolate(graph, v):
    # Get attached edges to this vertex, remove them.
    for e in graph.IncidentEdges(v):
        graph.E.remove(e)
    # Remove this vertex.
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

        # Swap current player.
        active_player = 1 - active_player

    # Check that all vertices are colored now.
    assert all(v.color != -1 for v in graph.V)

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
    # 84.33333% with non-random coloring
    # 80.66666% with random coloring
    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == -1
    def ChooseVertexToColor(graph, player):
        undecideds = [[v, len(graph.IncidentEdges(v))] for v in graph.V if v.color == -1]
        undecideds.sort(key = lambda x: -x[1])
        return undecideds[0][0]
        #return random.choice([v for v in graph.V if v.color == -1])

    # `graph` is an instance of a Graph, `player` is an integer (0 or 1).
    # Should return a vertex `v` from graph.V where v.color == player
    def ChooseVertexToRemove(graph, player):
        if len(graph.V)>=11:
            #print("Too hard!")
            return random.choice([v for v in graph.V if v.color == player])
        result = PercolationPlayer.ChooseVertexToRemove_helper(graph, player)
        print(result[1])
        print("Removing")
        return result[0]

    # Recursive helper. Returns a tuple, composed of the vertex to be removed
    # followed by the probability that I win
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

# Feel free to put any personal driver code here.
def main():
    pass

if __name__ == "__main__":
    # NOTE: we are not creating INSTANCES of these classes, we're defining the players
    # as the class itself. This lets us call the static methods.
    #p1 = RandomPlayer
    # Comment the above line and uncomment the next two if
    # you'd like to test the PercolationPlayer code in this repo.
    #from percolator import PercolationPlayer
    p1 = PercolationPlayer
    p2 = RandomPlayer
    start_time = time.time()
    # Used to be 200 [FIX LATER]
    iters = 50
    wins = PlayBenchmark(p1, p2, iters)
    print(
        "Player 1 (Me): {0} Player 2 (Random): {1}".format(
            1.0 * wins[0] / sum(wins), 1.0 * wins[1] / sum(wins)
        )
    )
    print(time.time()-start_time)
