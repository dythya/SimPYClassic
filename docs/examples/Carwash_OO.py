from SimPy.Simulation import *
import random
"""Carwash_OO.py
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
# Experiment data -------------------------
nrMachines = 2
tInter = 2  # minutes
washtime = 3.5  # minutes
initialSeed = 123456
simTime = 100  # minutes

# Model 1 components ----------------------


class Carwash(Process):
    """Carwash machine; master"""

    def __init__(self, name, sim):
        Process.__init__(self, name=name, sim=sim)
        self.carBeingWashed = None

    def lifecycle(self):
        while True:
            yield get, self, self.sim.waitingCars, 1
            self.carBeingWashed = self.got[0]
            yield hold, self, washtime
            self.carBeingWashed.doneSignal.signal(self.name)


class Car(Process):
    """Car; slave"""

    def __init__(self, name, sim):
        Process.__init__(self, name=name, sim=sim)
        self.doneSignal = SimEvent(sim=sim)

    def lifecycle(self):
        yield put, self, self.sim.waitingCars, [self]
        yield waitevent, self, self.doneSignal
        whichWash = self.doneSignal.signalparam
        print("{0}: {1} done by {2}".format(
            self.sim.now(), self.name, whichWash))


class CarGenerator(Process):
    """Car arrival generation"""

    def generate(self):
        i = 0
        while True:
            yield hold, self, self.sim.r.expovariate(1.0 / tInter)
            c = Car("car{0}".format(i), sim=self.sim)
            self.sim.activate(c, c.lifecycle())
            i += 1

# Model 1: Carwash is master, car is slave


class CarWashModel1(Simulation):
    def run(self):
        print("Model 1: carwash is master")
        print("--------------------------")
        self.initialize()
        self.r = random.Random()
        self.r.seed(initialSeed)
        waiting = []
        for j in range(1, 5):
            c = Car("car{0}".format(-j), sim=self)
            self.activate(c, c.lifecycle())
            waiting.append(c)
        self.waitingCars = Store(
            capacity=40, initialBuffered=waiting, sim=self)
        cw = []
        for i in range(nrMachines):
            c = Carwash("Carwash {0}".format(i), sim=self)
            cw.append(c)
            self.activate(c, c.lifecycle())
        cg = CarGenerator(sim=self)
        self.activate(cg, cg.generate())
        self.simulate(until=simTime)

        print("waiting cars: {0}".format(
            [x.name for x in self.waitingCars.theBuffer]))
        print("cars being washed: {0}".format(
            [y.carBeingWashed.name for y in cw]))


# Experiment 1 ----------------------------
CarWashModel1().run()

############################################

# Model 2 components ----------------------


class CarM(Process):
    """Car is master"""

    def lifecycle(self):
        yield get, self, self.sim.washers, 1
        whichWash = self.got[0]
        self.sim.carsBeingWashed.append(self)
        yield hold, self, washtime
        print("{0}: {1} done by {2}".format(
            self.sim.now(), self.name, whichWash.name))
        whichWash.doneSignal.signal()
        self.sim.carsBeingWashed.remove(self)


class CarwashS(Process):
    def __init__(self, name, sim):
        Process.__init__(self, name=name, sim=sim)
        self.doneSignal = SimEvent(sim=sim)

    def lifecycle(self):
        while True:
            yield put, self, self.sim.washers, [self]
            yield waitevent, self, self.doneSignal


class CarGenerator1(Process):
    def generate(self):
        i = 0
        while True:
            yield hold, self, self.sim.r.expovariate(1.0 / tInter)
            c = CarM("car{0}".format(i), sim=self.sim)
            self.sim.activate(c, c.lifecycle())
            i += 1

# Model 2: Car is master, carwash is slave


class CarWashModel2(Simulation):
    def run(self):
        print("\nModel 2: car is master")
        print("----------------------")
        self.initialize()
        self.r = random.Random()
        self.r.seed(initialSeed)
        self.washers = Store(capacity=nrMachines, sim=self)
        self.carsBeingWashed = []
        for j in range(1, 5):
            c = CarM("car{0}".format(-j), sim=self)
            self.activate(c, c.lifecycle())
        for i in range(2):
            cw = CarwashS("Carwash {0}".format(i), sim=self)
            self.activate(cw, cw.lifecycle())
        cg = CarGenerator1(sim=self)
        self.activate(cg, cg.generate())
        self.simulate(until=simTime)

        print("waiting cars: {0}".format([x.name for x in self.washers.getQ]))
        print("cars being washed: {0}".format(
            [x.name for x in self.carsBeingWashed]))


# Experiment 1 ----------------------------
CarWashModel2().run()
