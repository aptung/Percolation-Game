class Vertex:
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
        return hash((self.index, self.color))

class Edge:
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
        return hash(repr(self))


class Graph:
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
        return hash(repr(self))

    # Gets a vertex with given index if it exists, else return None.
    def GetVertex(self, i):
        for v in self.V:
            if v.index == i:
                return v
        return None

    # Returns the incident edges on a vertex.
    def IncidentEdges(self, v):
        return [e for e in self.E if (e.a == v or e.b == v)]
