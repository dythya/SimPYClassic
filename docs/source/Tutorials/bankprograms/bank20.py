""" bank20: One counter with a priority customer """
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval, resource):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=12.0,
                                res=resource, P=0))
            t = expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and  leaves """

    def visit(self, timeInBank=0, res=None, P=0):  # 1
        arrive = now()       # arrival time
        Nwaiting = len(res.waitQ)
        print("%8.3f %s: Queue is %d on arrival" %  # 2
              (now(), self.name, Nwaiting))

        yield request, self, res, P  # 3
        wait = now() - arrive  # waiting time
        print("%8.3f %s: Waited %6.3f" %
              (now(), self.name, wait))
        yield hold, self, timeInBank
        yield release, self, res

        print("%8.3f %s: Completed" %
              (now(), self.name))

# Experiment data -------------------------


maxTime = 400.0  # minutes
k = Resource(name="Counter", unitName="Karen",  # 4
             qType=PriorityQ)

# Model/Experiment ------------------------------
seed(787878)
initialize()
s = Source('Source')
activate(s, s.generate(number=5, interval=10.0,
                       resource=k), at=0.0)
guido = Customer(name="Guido     ")  # 5
activate(guido, guido.visit(timeInBank=12.0, res=k,  # 6
                            P=100), at=23.0)
simulate(until=maxTime)
