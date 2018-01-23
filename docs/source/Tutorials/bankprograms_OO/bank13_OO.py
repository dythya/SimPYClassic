""" bank13_OO: Wait for the doorman to give a signal: *waitevent*"""
from SimPy.Simulation import (Simulation, Process, Resource, SimEvent, hold,
                              request, release, waitevent)
from random import *

# Model components ------------------------


class Doorman(Process):
    """ Doorman opens the door"""

    def openthedoor(self):
        """ He will opens the door at fixed intervals"""
        for i in range(5):
            yield hold, self, 30.0
            self.sim.dooropen.signal()
            print("%7.4f You may enter" % (self.sim.now()))


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, rate):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=12.0))
            yield hold, self, expovariate(rate)


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, timeInBank=10):
        arrive = self.sim.now()

        if self.sim.dooropen.occurred:
            msg = '.'
        else:
            msg = ' but the door is shut.'
        print("%7.4f %s: Here I am%s" % (self.sim.now(), self.name, msg))
        yield waitevent, self, self.sim.dooropen

        print("%7.4f %s: The door is open!" % (self.sim.now(), self.name))

        wait = self.sim.now() - arrive
        print("%7.4f %s: Waited %6.3f" % (self.sim.now(), self.name, wait))

        yield request, self, self.sim.counter
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, self.sim.counter

        print("%7.4f %s: Finished    " % (self.sim.now(), self.name))

# Model  ----------------------------------


class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.dooropen = SimEvent("Door Open", sim=self)
        self.counter = Resource(1, name="Clerk", sim=self)
        doorman = Doorman(sim=self)
        self.activate(doorman, doorman.openthedoor())
        source = Source(sim=self)
        self.activate(source,
                      source.generate(number=5, rate=0.1), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0  # minutes
seedVal = 232323

# Experiment  ----------------------------------

mymodel = BankModel()
mymodel.run(aseed=seedVal)
