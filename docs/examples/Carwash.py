from SimPy.Simulation import *
import random
"""carwash.py
Scenario:
A carwash installation has nrMachines washing machines which wash a car in
washTime minutes.
Cars arrive with a negative exponential interarrival time with a mean of tInter
minutes.

Model the carwash operation as cooperation between two processes, the car being
washed and the machine doing the washing.

Build two implementations:
Model 1: the machine is master, the car slave;
Model 2: the car is master, the machine is slave.

"""
# Data:
nrMachines = 2
tInter = 2  # minutes
washtime = 3.5  # minutes
initialSeed = 123456
simTime = 100

#####################################################
# Model 1: Carwash is master, car is slave
#####################################################


class Carwash(Process):
    """Carwash machine; master"""

    def __init__(self, name):
        Process.__init__(self, name)
        self.carBeingWashed = None

    def lifecycle(self):
        while True:
            yield get, self, waitingCars, 1
            self.carBeingWashed = self.got[0]
            yield hold, self, washtime
            self.carBeingWashed.doneSignal.signal(self.name)


class Car(Process):
    """Car; slave"""

    def __init__(self, name):
        Process.__init__(self, name)
        self.doneSignal = SimEvent()

    def lifecycle(self):
        yield put, self, waitingCars, [self]
        yield waitevent, self, self.doneSignal
        whichWash = self.doneSignal.signalparam
        print("{0}: {1} done by {2}".format(now(), self.name, whichWash))


class CarGenerator(Process):
    """Car arrival generation"""

    def generate(self):
        i = 0
        while True:
            yield hold, self, r.expovariate(1.0 / tInter)
            c = Car("car{0}".format(i))
            activate(c, c.lifecycle())
            i += 1


print("Model 1: carwash is master")
print("--------------------------")
initialize()
r = random.Random()
r.seed(initialSeed)
waiting = []
for j in range(1, 5):
    c = Car("car-{0}".format(j))
    activate(c, c.lifecycle())
    waiting.append(c)
waitingCars = Store(capacity=40, initialBuffered=waiting)
cw = []
for i in range(2):
    c = Carwash("Carwash {0}".format(i))
    cw.append(c)
    activate(c, c.lifecycle())
cg = CarGenerator()
activate(cg, cg.generate())
simulate(until=simTime)
print("waiting cars: {0}".format([x.name for x in waitingCars.theBuffer]))
print("cars being washed: {0}".format([y.carBeingWashed.name for y in cw]))

#####################################################
# Model 2: Car is master, carwash is slave
#####################################################


class CarM(Process):
    """Car is master"""

    def __init__(self, name):
        Process.__init__(self, name)

    def lifecycle(self):
        yield get, self, washers, 1
        whichWash = self.got[0]
        carsBeingWashed.append(self)
        yield hold, self, washtime
        print("{0}: {1} done by {2}".format(now(), self.name, whichWash.name))
        whichWash.doneSignal.signal()
        carsBeingWashed.remove(self)


class CarwashS(Process):
    def __init__(self, name):
        Process.__init__(self, name)
        self.doneSignal = SimEvent()

    def lifecycle(self):
        while True:
            yield put, self, washers, [self]
            yield waitevent, self, self.doneSignal


class CarGenerator1(Process):
    def generate(self):
        i = 0
        while True:
            yield hold, self, r.expovariate(1.0 / tInter)
            c = CarM("car{0}".format(i))
            activate(c, c.lifecycle())
            i += 1


print("\nModel 2: car is master")
print("----------------------")
initialize()
r = random.Random()
r.seed(initialSeed)
washers = Store(capacity=nrMachines)
carsBeingWashed = []
for j in range(1, 5):
    c = CarM("car-{0}".format(j))
    activate(c, c.lifecycle())
for i in range(2):
    cw = CarwashS("Carwash {0}".format(i))
    activate(cw, cw.lifecycle())
cg = CarGenerator1()
activate(cg, cg.generate())
simulate(until=simTime)
print("waiting cars: {0}".format([x.name for x in washers.getQ]))
print("cars being washed: {0}".format([x.name for x in carsBeingWashed]))
