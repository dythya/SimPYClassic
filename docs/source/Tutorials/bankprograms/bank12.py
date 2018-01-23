""" bank12: Multiple runs of the bank with a Monitor"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval, resource, mon):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(b=resource, M=mon))  # 1
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, b, M):
        arrive = now()
        yield request, self, b
        wait = now() - arrive
        M.observe(wait)
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, b

# Experiment data -------------------------


maxNumber = 50
maxTime = 2000.0  # minutes
timeInBank = 12.0   # mean, minutes
ARRint = 10.0     # mean, minutes
Nc = 2            # number of counters
theSeed = 393939

# Model  ----------------------------------


def model(runSeed=theSeed):  # 2
    seed(runSeed)
    k = Resource(capacity=Nc, name="Clerk")
    wM = Monitor()  # 3

    initialize()
    s = Source('Source')
    activate(s, s.generate(number=maxNumber, interval=ARRint,
                           resource=k, mon=wM), at=0.0)  # 4
    simulate(until=maxTime)
    return (wM.count(), wM.mean())  # 5

# Experiment/Result  ----------------------------------


theseeds = [393939, 31555999, 777999555, 319999771]  # 6
for Sd in theseeds:
    result = model(Sd)
    print("Avge wait for %3d completions was %6.2f min." %
          result)  # 7
