from SimPy.Simulation import (Process, SimEvent, Store, activate, get,
                              initialize, hold, now, put, simulate, waitevent)
"""Carwash is master"""


class Carwash(Process):
    """Carwash is master"""

    def __init__(self, name):
        Process.__init__(self, name=name)

    def lifecycle(self):
        while True:
            yield get, self, waitingCars, 1
            carBeingWashed = self.got[0]
            yield hold, self, washtime
            carBeingWashed.doneSignal.signal(self.name)


class Car(Process):
    """Car is slave"""

    def __init__(self, name):
        Process.__init__(self, name=name)
        self.doneSignal = SimEvent()

    def lifecycle(self):
        yield put, self, waitingCars, [self]
        yield waitevent, self, self.doneSignal
        whichWash = self.doneSignal.signalparam
        print('%s car %s done by %s' % (now(), self.name, whichWash))


class CarGenerator(Process):
    def generate(self):
        i = 0
        while True:
            yield hold, self, 2
            c = Car('%d' % i)
            activate(c, c.lifecycle())
            i += 1


washtime = 5
initialize()

# put four cars into the queue of waiting cars
for j in range(1, 5):
    c = Car(name='%d' % -j)
    activate(c, c.lifecycle())

waitingCars = Store(capacity=40)
for i in range(2):
    cw = Carwash('Carwash %s' % i)
    activate(cw, cw.lifecycle())

cg = CarGenerator()
activate(cg, cg.generate())
simulate(until=30)
print('waitingCars %s' % [x.name for x in waitingCars.theBuffer])
