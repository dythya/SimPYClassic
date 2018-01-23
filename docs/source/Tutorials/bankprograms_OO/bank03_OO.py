""" bank03_OO: Many non-random Customers """
from SimPy.Simulation import Simulation, Process, hold


# Model components ------------------------
class Source(Process):
    """ Source generates customers regularly """

    def generate(self, number, TBA):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=12.0))
            yield hold, self, TBA


class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank):
        print("%7.4f %s: Here I am" % (self.sim.now(), self.name))
        yield hold, self, timeInBank
        print("%7.4f %s: I must leave" % (self.sim.now(), self.name))


# Model -----------------------------------
class BankModel(Simulation):
    def run(self):
        """ PEM """
        s = Source(sim=self)
        self.activate(s, s.generate(number=maxNumber,
                                    TBA=ARRint), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxNumber = 5
maxTime = 400.0  # minutes
ARRint = 10.0    # time between arrivals, minutes

# Experiment ------------------------------

mymodel = BankModel()
mymodel.run()
