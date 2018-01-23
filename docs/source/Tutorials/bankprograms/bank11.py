""" bank11: The bank with a Monitor"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval, resource):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(b=resource))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, b):
        arrive = now()
        yield request, self, b
        wait = now() - arrive
        wM.observe(wait)  # 1
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, b

# Experiment data -------------------------


maxNumber = 50
maxTime = 1000.0    # minutes
timeInBank = 12.0   # mean, minutes
ARRint = 10.0    # mean, minutes
Nc = 2           # number of counters
theseed = 99999

# Model/Experiment   ----------------------

seed(theseed)
k = Resource(capacity=Nc, name="Clerk")
wM = Monitor()  # 2
initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber, interval=ARRint,
                       resource=k), at=0.0)  # 3
simulate(until=maxTime)

# Result  ----------------------------------

result = wM.count(), wM.mean()  # 4
print("Average wait for %3d completions was %5.3f minutes." % result)
