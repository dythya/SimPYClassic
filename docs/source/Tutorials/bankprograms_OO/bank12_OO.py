""" bank12_OO: Multiple runs of the bank with a Monitor"""
from SimPy.Simulation import Simulation, Process, \
    Resource, Monitor, hold, request, release  # 1
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval):  # 2
        for i in range(number):
            c = Customer(name="Customer%02d" % (i),
                         sim=self.sim)  # 3
            self.sim.activate(c, c.visit(b=self.sim.k))  # 4
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, b):
        arrive = self.sim.now()  # 5
        yield request, self, b
        wait = self.sim.now() - arrive  # 6
        self.sim.wM.observe(wait)
        tib = expovariate(1.0 / timeInBank)  # 7
        yield hold, self, tib
        yield release, self, b

# Simulation Model  ----------------------------------


class BankModel(Simulation):  # 8
    def run(self, aseed):
        self.initialize()  # 9
        seed(aseed)
        self.k = Resource(capacity=Nc, name="Clerk",
                          sim=self)  # 10
        self.wM = Monitor(sim=self)  # 11
        s = Source('Source', sim=self)  # 12
        self.activate(s, s.generate(number=maxNumber,
                                    interval=ARRint), at=0.0)
        self.simulate(until=maxTime)  # 13
        return (self.wM.count(), self.wM.mean())


# Experiment data -------------------------
maxNumber = 50
maxTime = 2000.0    # minutes
timeInBank = 12.0   # mean, minutes
ARRint = 10.0       # mean, minutes
Nc = 2              # number of counters
seedVals = [393939, 31555999, 777999555, 319999771]

# Experiment/Result  ----------------------------------

mymodel = BankModel()  # 14
for Sd in seedVals:  # 15
    mymodel.run(aseed=Sd)  # 16
    moni = mymodel.wM  # 17
    print("Avge wait for %3d completions was %6.2f min." %
          (moni.count(), moni.mean()))
