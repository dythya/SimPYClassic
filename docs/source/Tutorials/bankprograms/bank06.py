""" bank06: Many Random Customers """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers at random """

    def generate(self, number, meanTBA):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=12.0))
            t = expovariate(1.0 / meanTBA)  # 1
            yield hold, self, t  # 2


class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank=0):
        print("%7.4f %s: Here I am" % (now(), self.name))
        yield hold, self, timeInBank
        print("%7.4f %s: I must leave" % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5
maxTime = 400.0  # minutes
ARRint = 10.0    # mean arrival interval, minutes

# Model/Experiment ------------------------------

seed(99999)  # 3
initialize()
s = Source(name='Source')
activate(s, s.generate(number=maxNumber,
                       meanTBA=ARRint), at=0.0)
simulate(until=maxTime)
