""" bank20_OO: One counter with a priority customer """
from SimPy.Simulation import (Simulation, Process, Resource, PriorityQ, hold,
                              request, release)
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=12.0, P=0))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and  leaves """

    def visit(self, timeInBank=0, P=0):
        arrive = self.sim.now()       # arrival time
        Nwaiting = len(self.sim.k.waitQ)
        print("%8.3f %s: Queue is %d on arrival" %
              (self.sim.now(), self.name, Nwaiting))

        yield request, self, self.sim.k, P
        wait = self.sim.now() - arrive  # waiting time
        print("%8.3f %s: Waited %6.3f" % (self.sim.now(), self.name, wait))
        yield hold, self, timeInBank
        yield release, self, self.sim.k

        print("%8.3f %s: Completed" % (self.sim.now(), self.name))


# Model ------------------------------
class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.k = Resource(name="Counter", unitName="Karen",
                          qType=PriorityQ, sim=self)
        s = Source('Source', sim=self)
        self.activate(s, s.generate(number=5, interval=10.0), at=0.0)
        guido = Customer(name="Guido     ", sim=self)
        self.activate(guido, guido.visit(timeInBank=12.0, P=100), at=23.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0  # minutes
seedVal = 787878

# Experiment ---------------------------

mymodel = BankModel()
mymodel.run(aseed=seedVal)
