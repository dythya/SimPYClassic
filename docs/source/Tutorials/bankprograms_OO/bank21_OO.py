""" bank21_OO: One counter with impatient customers """
from SimPy.Simulation import (Simulation, Process, Resource, hold, request,
                              release)
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=15.0))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and  leaves """

    def visit(self, timeInBank=0):
        arrive = self.sim.now()       # arrival time
        print("%8.3f %s: Here I am     " % (self.sim.now(), self.name))

        yield (request, self, self.sim.counter), (hold, self, maxWaitTime)
        wait = self.sim.now() - arrive  # waiting time
        if self.acquired(self.sim.counter):
            print("%8.3f %s: Waited %6.3f" % (self.sim.now(), self.name, wait))
            yield hold, self, timeInBank
            yield release, self, self.sim.counter
            print("%8.3f %s: Completed" % (self.sim.now(), self.name))
        else:
            print("%8.3f %s: Waited %6.3f. I am off" %
                  (self.sim.now(), self.name, wait))


# Model  ----------------------------------
class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.counter = Resource(name="Karen", sim=self)
        source = Source('Source', sim=self)
        self.activate(source,
                      source.generate(number=5, interval=10.0), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0     # minutes
maxWaitTime = 12.0  # minutes. maximum time to wait
seedVal = 989898

# Experiment  ----------------------------------

mymodel = BankModel()
mymodel.run(aseed=seedVal)
