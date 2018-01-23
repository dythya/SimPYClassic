""" Market_OO.py
Model of a supermarket.
"""
from SimPy.Simulation import *
import random
from math import sqrt


# Model components ------------------------

class Customer(Process):
    def __init__(self, sim):
        Process.__init__(self, sim=sim)
        # Randomly pick how many items this customer is buying
        self.items = 1 + int(random.expovariate(1.0 / AVGITEMS))

    def checkout(self):
        start = self.sim.now()           # Customer decides to check out
        yield request, self, self.sim.checkout_aisle
        at_checkout = self.sim.now()     # Customer gets to front of line
        self.sim.waittime.tally(at_checkout - start)
        yield hold, self, self.items * ITEMTIME
        leaving = self.sim.now()         # Customer completes purchase
        self.sim.checkouttime.tally(leaving - at_checkout)
        yield release, self, self.sim.checkout_aisle


class Customer_Factory(Process):
    def run(self):
        while 1:
            c = Customer(sim=self.sim)
            self.sim.activate(c, c.checkout())
            arrival = random.expovariate(float(AVGCUST) / CLOSING)
            yield hold, self, arrival


class Monitor2(Monitor):
    def __init__(self, sim):
        Monitor.__init__(self, sim=sim)
        self.min, self.max = (sys.maxsize, 0)

    def tally(self, x):
        self.observe(x)
        self.min = min(self.min, x)
        self.max = max(self.max, x)

# Experiment data -------------------------


AISLES = 6         # Number of open aisles
ITEMTIME = 0.1     # Time to ring up one item
AVGITEMS = 20      # Average number of items purchased
CLOSING = 60 * 12    # Minutes from store open to store close
AVGCUST = 1500     # Average number of daily customers
RUNS = 8           # Number of times to run the simulation
SEED = 111333555   # seed value for random numbers


# Model
class MarketModel(Simulation):
    def runs(self):

        random.seed(SEED)
        print('Market')
        for run in range(RUNS):
            self.initialize()
            self.waittime = Monitor2(sim=self)
            self.checkouttime = Monitor2(sim=self)
            self.checkout_aisle = Resource(capacity=AISLES, sim=self)

            cf = Customer_Factory(sim=self)
            self.activate(cf, cf.run(), 0.0)
            self.simulate(until=CLOSING)
            # Analysis/output -------------
            FMT = ("Waiting time average: {0:.1f} "
                   "(std dev {1:.1f}, maximum {2:.1f})")
            print(FMT.format(self.waittime.mean(),
                             sqrt(self.waittime.var()),
                             self.waittime.max))


# Experiment ------------------------------
MarketModel().runs()
print('AISLES:', AISLES, '  ITEM TIME:', ITEMTIME)
