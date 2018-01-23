from SimPy.Simulation import *
import random

"""
needResources.py

Demo of waitUntil capability.

Scenario:
Three workers require sets of tools to do their jobs. Tools are shared, scarce
resources for which they compete.
"""


class Worker(Process):
    def work(self, heNeeds=[]):
        def workerNeeds():
            for item in heNeeds:
                if item.n == 0:
                    return False
            return True

        while now() < 8 * 60:
            yield waituntil, self, workerNeeds
            for item in heNeeds:
                yield request, self, item
            print("{0} {1} has {2} and starts job"
                  .format(now(),
                          self.name,
                          [x.name for x in heNeeds]))
            yield hold, self, random.uniform(10, 30)
            for item in heNeeds:
                yield release, self, item
            yield hold, self, 2  # rest


random.seed(111333555)
print('needResources')
initialize()
brush = Resource(capacity=1, name="brush")
ladder = Resource(capacity=2, name="ladder")
hammer = Resource(capacity=1, name="hammer")
saw = Resource(capacity=1, name="saw")
painter = Worker("painter")
activate(painter, painter.work([brush, ladder]))
roofer = Worker("roofer")
activate(roofer, roofer.work([hammer, ladder, ladder]))
treeguy = Worker("treeguy")
activate(treeguy, treeguy.work([saw, ladder]))
print(simulate(until=9 * 60))
