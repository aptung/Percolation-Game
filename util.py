class Vertex:
    def __init__(self, index, color=-1):
        self.index = index
        self.color = color

    def __repr__(self):
        if self.color == -1:
            return "Vertex({0})".format(self.index)
        else:
            return "Vertex({0}, {1})".format(self.index, self.color)


class Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "Edge({0}, {1})".format(self.a, self.b)


class Graph:
    def __init__(self, v, e):
        self.V = set(v)
        self.E = set(e)

    def __repr__(self):
        return "Graph({0}, {1})".format(self.V, self.E)

    def __deepcopy__(self, memo):
        V = {v.index: Vertex(v.index, v.color) for v in self.V}
        E = [Edge(V[e.a.index], V[e.b.index]) for e in self.E]
        return Graph(V.values(), E)

### DO NOT RELY ON THESE METHODS IN YOUR CODE! THEY WILL NOT NECESSARILY EXIST! ###
### THESE ARE BEING USED FOR DRIVER CODE ONLY ###

# Gets a vertex with given index if it exists, else return None.
def GetVertex(graph, i):
    for v in graph.V:
        if v.index == i:
            return v
    return None

# Returns the incident edges on a vertex.
def IncidentEdges(graph, v):
    return [e for e in graph.E if (e.a == v or e.b == v)]
