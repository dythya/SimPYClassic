from SimPy.Simulation import *
import random
"""
   Demo of SimPy's event signalling synchronization constructs
"""

print('demoSimPyEvents')

# Pavlov's dogs
"""Scenario:
Dogs start to drool when Pavlov rings the bell.
"""


class BellMan(Process):
    def ring(self):
        while True:
            bell.signal()
            print("{0} {1} rings bell".format(now(), self.name))
            yield hold, self, 5


class PavlovDog(Process):
    def behave(self):
        while True:
            yield waitevent, self, bell
            print("{0} {1} drools".format(now(), self.name))


random.seed(111333555)
initialize()
bell = SimEvent("bell")
for i in range(4):
    p = PavlovDog("Dog {0}".format(i + 1))
    activate(p, p.behave())
b = BellMan("Pavlov")
activate(b, b.ring())
print("\n Pavlov's dogs")
simulate(until=10)

# PERT simulation
"""
Scenario:
A job (TotalJob) requires 10 parallel activities with random duration to be
completed.
"""


class Activity(Process):
    def __init__(self, name):
        Process.__init__(self, name)
        self.event = SimEvent("completion of {0}".format(self.name))
        allEvents.append(self.event)

    def perform(self):
        yield hold, self, random.randint(1, 100)
        self.event.signal()
        print("{0} Event '{1}' fired".format(now(), self.event.name))


class TotalJob(Process):
    def perform(self, allEvents):
        for e in allEvents:
            yield waitevent, self, e
        print(now(), "All done")


random.seed(111333555)
initialize()
allEvents = []
for i in range(10):
    a = Activity("Activity {0}".format(i + 1))
    activate(a, a.perform())
t = TotalJob()
activate(t, t.perform(allEvents))
print("\n PERT network simulation")
simulate(until=100)

# US-style4-way stop intersection
"""
Scenario:
At a US-style 4-way stop intersection, a car may only enter the intersection
when it is free.
Cars enter in FIFO manner.
"""


class Car(Process):
    def drive(self):
        print("{0:4.1f} {1} waiting to enter intersection".format(now(),
                                                                  self.name))
        yield queueevent, self, intersectionFree
        # Intersection free, enter  . .
        # Begin Critical Section
        yield hold, self, 1  # drive across
        print("{0:4.1f} {1} crossed intersection".format(now(), self.name))
        # End Critical Section
        intersectionFree.signal()


random.seed(111333555)
initialize()
intersectionFree = SimEvent("Intersection free")
intersectionFree.signal()
arrtime = 0.0
for i in range(20):
    c = Car("Car {0}".format(i + 1))
    activate(c, c.drive(), at=arrtime)
    arrtime += 0.2
print("\n 4-way stop intersection")
print(simulate(until=100))
