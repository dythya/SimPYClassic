""" bank08_OO

 A counter with a random service time
 and customers who renege. Based on the program bank08.py
 from TheBank tutorial. (KGM)
"""
from SimPy.Simulation import *
from random import expovariate, seed, uniform

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval, counter):
        for i in range(number):
            c = Customer(name="Customer{0:02d}".format(i), sim=self.sim)
            self.sim.activate(c, c.visit(counter, timeInBank=12.0))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, counter, timeInBank=0):
        arrive = self.sim.now()
        print("{0:7.4f} {1}: Here I am     ".format(self.sim.now(), self.name))

        yield (request, self, counter), (hold, self, next(Customer.patience))

        if self.acquired(counter):
            wait = self.sim.now() - arrive
            print("{0:7.4f} {1}: Waited {2:6.3f}".format(
                self.sim.now(), self.name, wait))
            tib = expovariate(1.0 / timeInBank)
            yield hold, self, tib
            yield release, self, counter
            print("{0:7.4f} {1}: Finished".format(self.sim.now(), self.name))
        else:
            wait = self.sim.now() - arrive
            print("{0:7.4f} {1}: RENEGED after {2:6.3f}".format(
                self.sim.now(), self.name, wait))

    def fpatience(minpatience=0, maxpatience=10000000000):
        while True:
            yield uniform(minpatience, maxpatience)
    fpatience = staticmethod(fpatience)

# Model ---------------------------------------------


class BankModel(Simulation):
    def run(self):
        self.initialize()
        counter = Resource(name="Karen", sim=self)
        Customer.patience = Customer.fpatience(minpatience=1, maxpatience=3)
        source = Source(name='Source', sim=self)
        self.activate(source, source.generate(NumCustomers,
                                              interval=IntervalCustomers,
                                              counter=counter))
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0
theseed = 1234
NumCustomers = 5
IntervalCustomers = 10.0
# Experiment ------------------------------

seed(theseed)
print('bank08renege')
BankModel().run()
