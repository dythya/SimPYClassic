""" bank09.py: Simulate customers arriving
    at random, using a Source requesting service
    from several clerks but a single queue
    with a random servicetime
"""
from __future__ import generators
from random import Random
import SimPy.SimulationTrace as Simulation


class Source(Simulation.Process):
    """ Source generates customers randomly"""

    def __init__(self, seed=333):
        Simulation.Process.__init__(self)
        self.SEED = seed

    def generate(self, number, interval):
        rv = Random(self.SEED)
        for i in range(number):
            c = Customer(name="Customer%02d" % (i,))
            Simulation.activate(c, c.visit(timeInBank=12.0))
            t = rv.expovariate(1.0 / interval)
            yield Simulation.hold, self, t


class Customer(Simulation.Process):
    """ Customer arrives, is served and leaves """

    def __init__(self, name):
        Simulation.Process.__init__(self)
        self.name = name

    def visit(self, timeInBank=0):
        arrive = Simulation.now()
        print("%7.4f %s: Here I am " % (Simulation.now(), self.name))
        yield Simulation.request, self, counter
        wait = Simulation.now() - arrive
        print("%7.4f %s: Waited %6.3f" % (Simulation.now(),
                                          self.name, wait))
        tib = counterRV.expovariate(1.0 / timeInBank)
        yield Simulation.hold, self, tib
        yield Simulation.release, self, counter
        print("%7.4f %s: Finished" % (Simulation.now(), self.name))


def model(counterseed=3939393):
    global counter, counterRV
    counter = Simulation.Resource(name="Clerk", capacity=2)  # Lcapacity
    counterRV = Random(counterseed)
    Simulation.initialize()
    sourceseed = 1133
    source = Source(seed=sourceseed)
    Simulation.activate(source, source.generate(5, 10.0), 0.0)
    Simulation.simulate(until=400.0)


model()
