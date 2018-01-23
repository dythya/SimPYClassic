""" bank08: A counter with a random service time """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, meanTBA, resource):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i,))
            activate(c, c.visit(b=resource))
            t = expovariate(1.0 / meanTBA)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, b):
        arrive = now()
        print("%8.4f %s: Here I am     " % (now(), self.name))
        yield request, self, b
        wait = now() - arrive
        print("%8.4f %s: Waited %6.3f" % (now(), self.name, wait))
        tib = expovariate(1.0 / timeInBank)  # 1
        yield hold, self, tib  # 2
        yield release, self, b
        print("%8.4f %s: Finished      " % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5  # 3
maxTime = 400.0    # minutes
timeInBank = 12.0  # mean, minutes
ARRint = 10.0      # mean, minutes
theseed = 99999  # 4

# Model/Experiment ------------------------------

seed(theseed)
k = Resource(name="Counter", unitName="Clerk")

initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber, meanTBA=ARRint,
                       resource=k), at=0.0)
simulate(until=maxTime)
