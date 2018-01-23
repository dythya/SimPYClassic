from SimPy.Simulation import (Simulation, Process, Resource, request, hold,
                              release)
"""Object Oriented SimPy API"""

# Model components -------------------------------


class Car(Process):
    def run(self, res):
        yield request, self, res
        yield hold, self, 10
        yield release, self, res
        print("Time: %s" % self.sim.now())

# Model and Experiment ---------------------------


s = Simulation()
s.initialize()
r = Resource(capacity=5, sim=s)
auto = Car(sim=s)
s.activate(auto, auto.run(res=r))
s.simulate(until=100)
