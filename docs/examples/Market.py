""" Market.py
Model of a supermarket.
"""
from SimPy.Simulation import *
import random
from math import sqrt


# Model components ------------------------

class Customer(Process):
    def __init__(self):
        Process.__init__(self)
        # Randomly pick how many items this customer is buying
        self.items = 1 + int(random.expovariate(1.0 / AVGITEMS))

    def checkout(self):
        start = now()           # Customer decides to check out
        yield request, self, checkout_aisle
        at_checkout = now()     # Customer gets to front of line
        waittime.tally(at_checkout - start)
        yield hold, self, self.items * ITEMTIME
        leaving = now()         # Customer completes purchase
        checkouttime.tally(leaving - at_checkout)
        yield release, self, checkout_aisle


class Customer_Factory(Process):
    def run(self):
        while 1:
            c = Customer()
            activate(c, c.checkout())
            arrival = random.expovariate(float(AVGCUST) / CLOSING)
            yield hold, self, arrival


class Monitor2(Monitor):
    def __init__(self):
        Monitor.__init__(self)
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


# Model/Experiment ------------------------------

random.seed(SEED)
print('Market')
for run in range(RUNS):
    waittime = Monitor2()
    checkouttime = Monitor2()
    checkout_aisle = Resource(AISLES)
    initialize()
    cf = Customer_Factory()
    activate(cf, cf.run(), 0.0)
    simulate(until=CLOSING)
    FMT = "Waiting time average: {0:.1f} (std dev {1:.1f}, maximum {2:.1f})"
    print(FMT.format(waittime.mean(), sqrt(waittime.var()), waittime.max))

# Analysis/output -------------------------

print('AISLES:', AISLES, '  ITEM TIME:', ITEMTIME)
