"""bank17_OO: Plotting a Histogram of Monitor results"""
from SimPy.Simulation import (Simulation, Process, Resource, Monitor, hold,
                              request, release)
from SimPy.SimPlot import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, rate):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=12.0))
            yield hold, self, expovariate(rate)


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def visit(self, timeInBank):
        arrive = self.sim.now()
        # print("%8.4f %s: Arrived     "%(now(), self.name))

        yield request, self, self.sim.counter
        # print("%8.4f %s: Got counter "%(now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, self.sim.counter

        # print("%8.4f %s: Finished    " % (now(), self.name))
        t = self.sim.now() - arrive
        self.sim.Mon.observe(t)

# Model  ----------------------------------


class BankModel(Simulation):
    def run(self, aseed):
        """ PEM """
        seed(aseed)
        self.counter = Resource(1, name="Clerk", sim=self)
        self.Mon = Monitor('Time in the Bank', sim=self)
        source = Source(sim=self)
        self.activate(source,
                      source.generate(number=20, rate=0.1), at=0.0)
        self.simulate(until=maxTime)

# Experiment data -------------------------


maxTime = 400.0   # minutes

N = 0
seedVal = 393939

# Experiment  -----------------------------

modl = BankModel()
modl.run(aseed=seedVal)

# Output ----------------------------------
Histo = modl.Mon.histogram(low=0.0, high=200.0, nbins=20)

plt = SimPlot()
plt.plotHistogram(Histo, xlab='Time (min)',
                  title="Time in the Bank",
                  color="red", width=2)
plt.mainloop()
