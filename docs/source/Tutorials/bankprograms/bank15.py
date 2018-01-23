"""bank15: Monitoring a Resource"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


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
        arrive = now()
        print("%8.4f %s: Arrived     " % (now(), self.name))

        yield request, self, counter
        print("%8.4f %s: Got counter " % (now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter

        print("%8.4f %s: Finished    " % (now(), self.name))


# Experiment data -------------------------
maxTime = 400.0    # minutes
counter = Resource(1, name="Clerk", monitored=True)  # 1

# Model  ----------------------------------


def model(SEED=393939):
    seed(SEED)
    initialize()
    source = Source()
    activate(source,
             source.generate(number=5, rate=0.1), at=0.0)
    simulate(until=maxTime)

    return (counter.waitMon.timeAverage(),
            counter.actMon.timeAverage())  # 2
# Experiment  ----------------------------------


print('Avge waiting = %6.4f\nAvge active = %6.4f\n' % model())  # 3
