""" bank01: The single non-random Customer """  # 1
from SimPy.Simulation import *  # 2

# Model components -----------------------------


class Customer(Process):  # 3
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank):  # 4
        print("%2.1f %s  Here I am" % (now(), self.name))  # 5
        yield hold, self, timeInBank  # 6
        print("%2.1f %s  I must leave" % (now(), self.name))  # 7

# Experiment data ------------------------------


maxTime = 100.0     # minutes #8
timeInBank = 10.0   # minutes

# Model/Experiment ------------------------------

initialize()  # 9
c = Customer(name="Klaus")  # 10
activate(c, c.visit(timeInBank), at=5.0)  # 11
simulate(until=maxTime)  # 12
