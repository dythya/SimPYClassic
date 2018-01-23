""" bank11: The bank with a Monitor"""
from SimPy.Simulation import Simulation, Process, Resource, Monitor, hold,\
    request, release
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(b=self.sim.k))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, b):
        arrive = self.sim.now()
        yield request, self, b
        wait = self.sim.now() - arrive
        self.sim.wM.observe(wait)
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, b

# Model -----------------------------------


class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.k = Resource(capacity=Nc, name="Clerk", sim=self)
        self.wM = Monitor(sim=self)
        s = Source('Source', sim=self)
        self.activate(s, s.generate(number=maxNumber, interval=ARRint), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxNumber = 50
maxTime = 1000.0   # minutes
timeInBank = 12.0  # mean, minutes
ARRint = 10.0      # mean, minutes
Nc = 2             # number of counters
seedVal = 99999

# Experiment   -----------------------------

experi = BankModel()
experi.run(aseed=seedVal)

# Result  ----------------------------------

result = experi.wM.count(), experi.wM.mean()
print("Average wait for %3d completions was %5.3f minutes." % result)
