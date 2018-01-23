""" bank24_OO. BCC system with several counters """
from SimPy.Simulation import (Simulation, Process, Resource, hold, request,
                              release)
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, meanTBA):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit())
            t = expovariate(1.0 / meanTBA)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives,  is served and leaves """

    def visit(self):
        arrive = self.sim.now()
        print("%8.4f %s: Here I am " % (self.sim.now(), self.name))
        if len(self.sim.k.waitQ) < maxInQueue:     # the test
            yield request, self, self.sim.k
            wait = self.sim.now() - arrive
            print("%8.4f %s: Wait %6.3f" % (self.sim.now(), self.name, wait))
            tib = expovariate(1.0 / timeInBank)
            yield hold, self, tib
            yield release, self, self.sim.k
            print("%8.4f %s: Finished  " % (self.sim.now(), self.name))
        else:
            Customer.numBalking += 1
            print("%8.4f %s: BALKING   " % (self.sim.now(), self.name))


# Model
class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        Customer.numBalking = 0
        self.k = Resource(capacity=numServers,
                          name="Counter", unitName="Clerk", sim=self)
        s = Source('Source', sim=self)
        self.activate(s, s.generate(number=maxNumber, meanTBA=ARRint), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------------


timeInBank = 12.0  # mean, minutes
ARRint = 10.0      # mean interarrival time, minutes
numServers = 1     # servers
maxInSystem = 2    # customers
maxInQueue = maxInSystem - numServers

maxNumber = 8
maxTime = 4000.0  # minutes
theseed = 212121

# Experiment --------------------------------------

mymodel = BankModel()
mymodel.run(aseed=theseed)
# Results -----------------------------------------

nb = float(Customer.numBalking)
print("balking rate is %8.4f per minute" % (nb / mymodel.now()))
