from SimPy.Simulation import *
import random

"""
needResources.py

Demo of waitUntil capability.

Scenario:
Three workers require sets of tools to do their jobs. Tools are shared, scarce
resources for which they compete.
"""

# Model components ------------------------


class Worker(Process):
    def work(self, heNeeds=[]):
        def workerNeeds():
            for item in heNeeds:
                if item.n == 0:
                    return False
            return True

        while self.sim.now() < 8 * 60:
            yield waituntil, self, workerNeeds
            for item in heNeeds:
                yield request, self, item
            print("{0} {1} has {2} and starts job"
                  .format(self.sim.now(),
                          self.name,
                          [x.name for x in heNeeds]))
            yield hold, self, random.uniform(10, 30)
            for item in heNeeds:
                yield release, self, item
            yield hold, self, 2  # rest


# Model -----------------------------------
class NeedResourcesModel(Simulation):
    def run(self):
        print('needResources')
        self.initialize()
        brush = Resource(capacity=1, name="brush", sim=self)
        ladder = Resource(capacity=2, name="ladder", sim=self)
        hammer = Resource(capacity=1, name="hammer", sim=self)
        saw = Resource(capacity=1, name="saw", sim=self)
        painter = Worker("painter", sim=self)
        self.activate(painter, painter.work([brush, ladder]))
        roofer = Worker("roofer", sim=self)
        self.activate(roofer, roofer.work([hammer, ladder, ladder]))
        treeguy = Worker("treeguy", sim=self)
        self.activate(treeguy, treeguy.work([saw, ladder]))
        print(self.simulate(until=9 * 60))


# Experiment data -------------------------
SEED = 111333555

# Experiment ------------------------------
random.seed(SEED)
NeedResourcesModel().run()
