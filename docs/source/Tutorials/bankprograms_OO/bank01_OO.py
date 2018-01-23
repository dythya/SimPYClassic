""" bank01_OO: The single non-random Customer """
from SimPy.Simulation import Simulation, Process, hold  # 1
# Model components -----------------------------


class Customer(Process):  # 2
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank):
        print("%2.1f %s  Here I am" %
              (self.sim.now(), self.name))
        yield hold, self, timeInBank
        print("%2.1f %s  I must leave" %
              (self.sim.now(), self.name))

# Model ----------------------------------------


class BankModel(Simulation):  # 3
    def run(self):
        """ An independent simulation object """
        c = Customer(name="Klaus", sim=self)  # 4
        self.activate(c, c.visit(timeInBank), at=tArrival)
        self.simulate(until=maxTime)  # 5


# Experiment data ------------------------------
maxTime = 100.0     # minutes                            #6
timeInBank = 10.0   # minutes
tArrival = 5.0      # minutes

# Experiment -----------------------------------
mymodel = BankModel()  # 7
mymodel.run()  # 8
