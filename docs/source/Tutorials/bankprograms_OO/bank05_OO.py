""" bank05_OO: The single Random Customer """
from SimPy.Simulation import Simulation, Process, hold
from random import expovariate, seed

# Model components ------------------------


class Customer(Process):
    """ Customer arrives at a random time,
        looks around  and then leaves """

    def visit(self, timeInBank):
        print("%f %s Here I am" % (self.sim.now(), self.name))
        yield hold, self, timeInBank
        print("%f %s I must leave" % (self.sim.now(), self.name))

# Model -----------------------------------


class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        c = Customer(name="Klaus", sim=self)
        t = expovariate(1.0 / tMeanArrival)
        self.activate(c, c.visit(timeInBank), at=t)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 100.0     # minutes
timeInBank = 10.0   # minutes
tMeanArrival = 5.0  # minutes
seedVal = 99999

# Experiment ------------------------------

mymodel = BankModel()
mymodel.run(aseed=seedVal)
