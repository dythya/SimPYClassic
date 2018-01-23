""" bank02_OO: More Customers """
from SimPy.Simulation import Simulation, Process, hold


# Model components ------------------------
class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank=0):
        print("%7.4f %s: Here I am" % (self.sim.now(), self.name))
        yield hold, self, timeInBank
        print("%7.4f %s: I must leave" % (self.sim.now(), self.name))


# Model -----------------------------------
class BankModel(Simulation):
    def run(self):
        """ PEM """
        c1 = Customer(name="Klaus", sim=self)
        self.activate(c1, c1.visit(timeInBank=10.0), at=5.0)
        c2 = Customer(name="Tony", sim=self)
        self.activate(c2, c2.visit(timeInBank=7.0), at=2.0)
        c3 = Customer(name="Evelyn", sim=self)
        self.activate(c3, c3.visit(timeInBank=20.0), at=12.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0  # minutes

# Experiment ------------------------------

mymodel = BankModel()
mymodel.run()
