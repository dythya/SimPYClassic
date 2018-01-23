""" bank04_OO: Simulate a single customer. random time in system """
from SimPy.Simulation import Simulation, Process, hold
from random import Random


# Model components ------------------------
class Customer(Process):
    """ Customer arrives in the bank, looks around for
    a random time and then leaves """

    def visit(self, timeInBank=0):
        print("%7.4f %s: Here I am" % (self.sim.now(), self.name))
        t = self.sim.rv.expovariate(1.0 / timeInBank)
        yield hold, self, t
        print("%7.4f %s: I must leave" % (self.sim.now(), self.name))

# Experiment data -------------------------


maxTime = 100.0    # minutes


# Model -----------------------------------
class BankModel(Simulation):
    def __init__(self, seed):
        Simulation.__init__(self)
        self.rv = Random(seed)

    def run(self):
        """ PEM """
        c = Customer(name="Klaus", sim=self)
        self.activate(c, c.visit(timeInBank=10.0), at=5.0)
        self.simulate(until=maxTime)


# Experiment ------------------------------
mymodel = BankModel(seed=1133)
mymodel.run()
