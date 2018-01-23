from SimPy.Simulation import *
""" shortestPath_SimPy_OO.py

    Finds the shortest path in a network.
    Author: Klaus Muller
"""
# Model components ------------------------


class node:
    def __init__(self):
        self.reached = 0


class searcher(Process):
    def __init__(self, graph, path, length, from_node,
                 to_node, distance, goal_node, sim):
        Process.__init__(self, sim=sim)
        self.path = path[:]
        self.length = length
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance
        self.graph = graph
        self.goal_node = goal_node

    def run(self, to_node):
        if DEMO:
            print("Path so far: {0} (length {1}). "
                  "Search from {2} to {3}".format(self.path,
                                                  self.length,
                                                  self.from_node,
                                                  to_node))
        yield hold, self, self.distance
        if not self.sim.nodes[to_node].reached:
            self.path.append(to_node)
            self.length += self.distance
            self.sim.nodes[to_node].reached = 1
            if to_node == self.goal_node:
                print("SHORTEST PATH", self.path, "Length:", self.length)
                self.sim.stopSimulation()
            else:
                for i in self.graph[to_node]:
                    s = searcher(graph=self.graph, path=self.path,
                                 length=self.length, from_node=i[0],
                                 to_node=i[1], distance=i[2],
                                 goal_node=self.goal_node, sim=self.sim)
                    self.sim.activate(s, s.run(i[1]))

# Model -----------------------------------


class ShortestPathModel(Simulation):
    def search(self):
        print('shortestPath_SimPy')
        self.initialize()
        self.nodes = {}
        for i in ("Atown", "Btown", "Ccity", "Dpueblo", "Evillage", "Fstadt"):
            self.nodes[i] = node()
        """ Format graph definition:
        a_graph={node_id:[(from,to,distance),
                          (from,to,distance)],
                          node_id:[ . . . ])
        """
        net = {"Atown": (("Atown", "Btown", 3.5), ("Atown", "Ccity", 1),
                         ("Atown", "Atown", 9), ("Atown", "Evillage", 0.5)),
               "Btown": (("Btown", "Ccity", 5),),
               "Ccity": (("Ccity", "Ccity", 1), ("Ccity", "Fstadt", 9),
                         ("Ccity", "Dpueblo", 3), ("Ccity", "Atown", 3)),
               "Dpueblo": (("Dpueblo", "Ccity", 2), ("Dpueblo", "Fstadt", 10)),
               "Evillage": (("Evillage", "Btown", 1),),
               "Fstadt": (("Fstadt", "Ccity", 3),)}
        if DEMO:
            print("Search for shortest path from {0} to {1} \n"
                  "in graph {2}".format("Atown",
                                        "Fstadt",
                                        sorted(net.items())))
        startup = searcher(graph=net, path=[], length=0, from_node="Atown",
                           to_node="Atown", distance=0, goal_node="Fstadt",
                           sim=self)
        self.activate(startup, startup.run("Atown"))
        self.simulate(until=10000)


# Experiment ------------------------------
DEMO = 1
ShortestPathModel().search()
