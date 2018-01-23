"""bank18: A Resource with Priority to vary the number of units"""

from random import expovariate, seed

# Model components ------------------------

tracing = 0
if tracing:
    from SimPy.SimulationTrace import *
else:
    from SimPy.Simulation import *


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, rate):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=12.0))
            yield hold, self, expovariate(rate)


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, timeInBank):
        print("%8.4f %s: Arrived     " % (now(), self.name))

        yield request, self, counter
        print("%8.4f %s: Got counter " % (now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter

        print("%8.4f %s: Finished    " % (now(), self.name))


class ClerkProcess(Process):
    """ This process removes a clerk from the counter
    after an average of 20 minutes.
    The clerk returns after 5 minutes """

    def serverProc(self):
        while True:
            # The clerk starts working. Leave after an average of 10 minutes
            yield hold, self, expovariate(1.0 / 15.0)
            print("%8.4f %s: urgent.  Free:"
                  "%d, %d waiting" % (now(), self.name, counter.n,
                                      len(counter.waitQ)))

            # The first free clerk is removed
            yield request, self, counter, 100
            print("%8.4f %s: leaves.  Free:"
                  "%d, %d waiting" % (now(), self.name, counter.n,
                                      len(counter.waitQ)))

            # period away is 3 minutes
            yield hold, self, 3.0

            # clerk returns
            yield release, self, counter
            print("%8.4f %s: returns. Free:"
                  "%d, %d waiting" % (now(),
                                      self.name,
                                      counter.n,
                                      len(counter.waitQ)))


# Experiment data -------------------------

maxTime = 200.0    # minutes
counter = Resource(1, name="Clerk", qType=PriorityQ)

# Model  ----------------------------------


def model(SEED=393939):
    seed(SEED)

    initialize()
    clerk1 = ClerkProcess('Clerk')
    activate(clerk1, clerk1.serverProc())
    source = Source('Source')
    activate(source, source.generate(number=20, rate=0.1), at=0.0)
    simulate(until=maxTime)

# Experiment  ----------------------------------


model()
