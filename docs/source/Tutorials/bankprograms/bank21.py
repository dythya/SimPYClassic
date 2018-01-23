""" bank21: One counter with impatient customers """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=15.0))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and  leaves """

    def visit(self, timeInBank=0):
        arrive = now()       # arrival time
        print("%8.3f %s: Here I am     " % (now(), self.name))

        yield (request, self, counter), (hold, self, maxWaitTime)
        wait = now() - arrive  # waiting time
        if self.acquired(counter):  # 1
            print("%8.3f %s: Waited %6.3f" % (now(), self.name, wait))
            yield hold, self, timeInBank
            yield release, self, counter
            print("%8.3f %s: Completed" % (now(), self.name))
        else:
            print("%8.3f %s: Waited %6.3f. I am off" %
                  (now(), self.name, wait))

# Experiment data -------------------------


maxTime = 400.0  # minutes
maxWaitTime = 12.0  # minutes. maximum time to wait

# Model  ----------------------------------


def model():
    global counter
    seed(989898)
    counter = Resource(name="Karen")
    initialize()
    source = Source('Source')
    activate(source,
             source.generate(number=5, interval=10.0), at=0.0)
    simulate(until=maxTime)

# Experiment  ----------------------------------


model()
