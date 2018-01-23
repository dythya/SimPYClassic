"""bank14_OO: *waituntil* the Bank door opens"""
from SimPy.Simulation import (Simulation, Process, Resource, hold, waituntil,
                              request, release)
from random import expovariate, seed

# Model components ------------------------


class Doorman(Process):
    """ Doorman opens the door"""

    def openthedoor(self):
        """ He will open the door when he arrives"""
        yield hold, self, expovariate(1.0 / 10.0)
        self.sim.door = 'Open'
        print("%7.4f Doorman: Ladies and "
              "Gentlemen! You may all enter." % (self.sim.now()))


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

        if self.sim.dooropen():
            msg = ' and the door is open.'
        else:
            msg = ' but the door is shut.'
        print("%7.4f %s: Here I am%s" % (self.sim.now(), self.name, msg))

        yield waituntil, self, self.sim.dooropen

        print("%7.4f %s: I can  go in!" % (self.sim.now(), self.name))
        wait = self.sim.now() - arrive
        print("%7.4f %s: Waited %6.3f" % (self.sim.now(), self.name, wait))

        yield request, self, self.sim.counter
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, self.sim.counter

        print("%7.4f %s: Finished    " % (self.sim.now(), self.name))

# Model  ----------------------------------


class BankModel(Simulation):
    def dooropen(self):
        return self.door == 'Open'

    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.counter = Resource(capacity=1, name="Clerk", sim=self)
        self.door = 'Shut'
        doorman = Doorman(sim=self)
        self.activate(doorman, doorman.openthedoor())
        source = Source(sim=self)
        self.activate(source,
                      source.generate(number=5, rate=0.1), at=0.0)
        self.simulate(until=400.0)

# Experiment data -------------------------


maxTime = 2000.0   # minutes
seedVal = 393939

# Experiment  ----------------------------------

mymodel = BankModel()
mymodel.run(aseed=seedVal)
