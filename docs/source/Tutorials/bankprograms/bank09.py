""" bank09: Several Counters but a Single Queue """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, meanTBA, resource):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
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
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, b
        print("%8.4f %s: Finished      " % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5
maxTime = 400.0    # minutes
timeInBank = 12.0  # mean, minutes
ARRint = 10.0      # mean, minutes
theseed = 99999

# Model/Experiment ------------------------------

seed(theseed)
k = Resource(capacity=2, name="Counter", unitName="Clerk")  # 1

initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber, meanTBA=ARRint,
                       resource=k), at=0.0)
simulate(until=maxTime)
