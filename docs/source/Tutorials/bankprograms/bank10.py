""" bank10: Several Counters with individual queues"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, interval, counters):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(counters))
            t = expovariate(1.0 / interval)
            yield hold, self, t


def NoInSystem(R):  # 1
    """ Total number of customers in the resource R"""
    return (len(R.waitQ) + len(R.activeQ))  # 2


class Customer(Process):
    """ Customer arrives, chooses the shortest queue
        is served and leaves
    """

    def visit(self, counters):
        arrive = now()
        Qlength = [NoInSystem(counters[i]) for i in range(Nc)]  # 3
        print("%7.4f %s: Here I am. %s" % (now(), self.name, Qlength))  # 4
        for i in range(Nc):  # 5
            if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                choice = i    # the index of the shortest line
                break  # 6

        yield request, self, counters[choice]
        wait = now() - arrive
        print("%7.4f %s: Waited %6.3f" % (now(), self.name, wait))
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counters[choice]

        print("%7.4f %s: Finished" % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5
maxTime = 400.0    # minutes
timeInBank = 12.0  # mean, minutes
ARRint = 10.0      # mean, minutes
Nc = 2             # number of counters
theseed = 787878

# Model/Experiment ------------------------------

seed(theseed)
kk = [Resource(name="Clerk0"), Resource(name="Clerk1")]  # 7
initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber, interval=ARRint,
                       counters=kk), at=0.0)
simulate(until=maxTime)
