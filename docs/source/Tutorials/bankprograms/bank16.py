"""bank16: Plotting from  Resource Monitors"""
from SimPy.Simulation import *
from SimPy.SimPlot import *  # 1
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
        # print("%8.4f %s: Arrived     " % (now(), self.name))

        yield request, self, counter
        # print("%8.4f %s: Got counter " % (now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter

        # print("%8.4f %s: Finished    " % (now(), self.name))

# Experiment data -------------------------


maxTime = 400.0   # minutes
counter = Resource(1, name="Clerk", monitored=True)

# Model -----------------------------------


def model(SEED=393939):  # 3
    seed(SEED)
    initialize()
    source = Source()
    activate(source,  # 4
             source.generate(number=20, rate=0.1), at=0.0)
    simulate(until=maxTime)  # 5

# Experiment -----------------------------------


model()

plt = SimPlot()  # 6
plt.plotStep(counter.waitMon,  # 7
             color="red", width=2)  # 8
plt.mainloop()  # 9
