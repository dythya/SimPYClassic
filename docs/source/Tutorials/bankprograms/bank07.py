""" bank07: One Counter,random arrivals """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, meanTBA, resource):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=12.0,
                                res=resource))  # 1
            t = expovariate(1.0 / meanTBA)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and  leaves """

    def visit(self, timeInBank, res):
        arrive = now()  # 2  arrival time
        print("%8.3f %s: Here I am" % (now(), self.name))

        yield request, self, res  # 3
        wait = now() - arrive  # 4  waiting time
        print("%8.3f %s: Waited %6.3f" % (now(), self.name, wait))
        yield hold, self, timeInBank  # 5
        yield release, self, res  # 6

        print("%8.3f %s: Finished" % (now(), self.name))

# Experiment data -------------------------


maxNumber = 5  # 7
maxTime = 400.0   # minutes
ARRint = 10.0     # mean, minutes
k = Resource(name="Counter", unitName="Clerk")  # 8

# Model/Experiment ------------------------------
seed(99999)
initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber,
                       meanTBA=ARRint, resource=k), at=0.0)  # 9
simulate(until=maxTime)
