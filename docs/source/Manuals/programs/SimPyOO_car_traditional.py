from SimPy.Simulation import (activate, hold, initialize, now, request,
                              release, simulate, Process, Resource)
"""Traditional SimPy API"""

# Model components -------------------------------


class Car(Process):
    def run(self, res):
        yield request, self, res
        yield hold, self, 10
        yield release, self, res
        print("Time: %s" % now())

# Model and Experiment ---------------------------


initialize()
r = Resource(capacity=5)
auto = Car()
activate(auto, auto.run(res=r))
simulate(until=100)
