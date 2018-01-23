"""bank17: Plotting a Histogram of Monitor results"""
from SimPy.Simulation import *
from SimPy.SimPlot import *
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
        arrive = now()  # 1
        # print("%8.4f %s: Arrived     " % (now(), self.name))

        yield request, self, counter
        # print("%8.4f %s: Got counter " % (now(), self.name))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter

        # print("%8.4f %s: Finished    " % (now(), self.name))
        t = now() - arrive  # 2
        Mon.observe(t)  # 3

# Experiment data -------------------------


maxTime = 400.0   # minutes
counter = Resource(1, name="Clerk")
Mon = Monitor('Time in the Bank')  # 4
N = 0

# Model  ----------------------------------


def model(SEED=393939):
    seed(SEED)

    initialize()
    source = Source()
    activate(source,
             source.generate(number=20, rate=0.1), at=0.0)
    simulate(until=maxTime)


# Experiment  ----------------------------------
model()
Histo = Mon.histogram(low=0.0, high=200.0, nbins=20)  # 5

plt = SimPlot()  # 6
plt.plotHistogram(Histo, xlab='Time (min)',  # 7
                  title="Time in the Bank",
                  color="red", width=2)
plt.mainloop()  # 8
