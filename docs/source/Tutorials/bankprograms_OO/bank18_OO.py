"""bank18: A Resource with Priority to vary the number of units"""

# Model components ------------------------
from SimPy.SimulationTrace import *
from random import expovariate, seed


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, rate):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=12.0))
            yield hold, self, expovariate(rate)


class Customer(Process):
    """ Customer arrives,  is served and leaves """

    def visit(self, timeInBank):
        print("%8.4f %s: Arrived     " % (self.sim.now(), self.name))

        yield request, self, self.sim.counter
        print("%8.4f %s: Got counter " % (self.sim.now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, self.sim.counter

        print("%8.4f %s: Finished    " % (self.sim.now(), self.name))


class ClerkProcess(Process):
    """ This process removes a clerk from the counter
    after an average of 20 minutes.
    The clerk returns after 5 minutes """

    def serverProc(self):
        while True:
            # The clerk starts working. Leave after an average of 10 minutes
            yield hold, self, expovariate(1.0 / 15.0)
            print("%8.4f %s: urgent.  Free:"
                  "%d, %d waiting" % (self.sim.now(),
                                      self.name,
                                      self.sim.counter.n,
                                      len(self.sim.counter.waitQ)))

            # The first free clerk is removed
            yield request, self, self.sim.counter, 100
            print("%8.4f %s: leaves.  Free:"
                  "%d, %d waiting" % (self.sim.now(),
                                      self.name,
                                      self.sim.counter.n,
                                      len(self.sim.counter.waitQ)))

            # period away is 3 minutes
            yield hold, self, 3.0

            # clerk returns
            yield release, self, self.sim.counter
            print("%8.4f %s: returns. Free:"
                  "%d, %d waiting" % (self.sim.now(),
                                      self.name,
                                      self.sim.counter.n,
                                      len(self.sim.counter.waitQ)))


# Experiment data -------------------------

maxTime = 200.0    # minutes

tracing = 0

# Model  ----------------------------------
if tracing:
    library = SimulationTrace
else:
    library = Simulation


class BankModel(library):
    def run(self):
        """ PEM """
        self.counter = Resource(1, name="Clerk", qType=PriorityQ, sim=self)
        clerk1 = ClerkProcess('Clerk', sim=self)
        self.activate(clerk1, clerk1.serverProc())
        source = Source('Source', sim=self)
        self.activate(source, source.generate(number=20, rate=0.1), at=0.0)
        self.simulate(until=maxTime)


# Experiment  ----------------------------------
seed(393939)
mymodel = BankModel()
mymodel.run()
