""" bank04: Simulate a single customer. random time in system """
from SimPy.Simulation import *
from random import Random

# Model components ------------------------


class Customer(Process):
    """ Customer arrives in the bank, looks around for
    a random time and then leaves """

    def __init__(self, name):
        Process.__init__(self)
        self.name = name

    def visit(self, rv, timeInBank=0):
        print("%7.4f %s: Here I am" % (now(), self.name))
        t = rv.expovariate(1.0 / timeInBank)
        yield hold, self, t
        print("%7.4f %s: I must leave" % (now(), self.name))

# Experiment data -------------------------


maxTime = 100.0    # minutes

# Model/Experiment ------------------------------


def model():
    rv = Random(1133)
    initialize()
    c = Customer(name="Klaus")
    activate(c, c.visit(rv, timeInBank=10.0), at=5.0)
    simulate(until=maxTime)


model()
