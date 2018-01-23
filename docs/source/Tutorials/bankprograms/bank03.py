""" bank03: Many non-random Customers """
from SimPy.Simulation import *

# Model components ------------------------


class Source(Process):  # 1
    """ Source generates customers regularly """

    def generate(self, number, TBA):  # 2
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))  # 3
            activate(c, c.visit(timeInBank=12.0))
            yield hold, self, TBA  # 4


class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank):
        print("%7.4f %s: Here I am" % (now(), self.name))
        yield hold, self, timeInBank
        print("%7.4f %s: I must leave" % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5
maxTime = 400.0  # minutes
ARRint = 10.0    # time between arrivals, minutes

# Model/Experiment ------------------------------

initialize()
s = Source()  # 5
activate(s, s.generate(number=maxNumber,  # 6
                       TBA=ARRint), at=0.0)
simulate(until=maxTime)
