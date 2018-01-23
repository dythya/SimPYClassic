from SimPy.SimulationTrace import (Process, Resource, activate, initialize,
                                   hold, now, release, request, simulate)


class Car(Process):
    def __init__(self, name, cc):
        Process.__init__(self, name=name)
        self.cc = cc

    def go(self):
        print('%s %s %s' % (now(), self.name, 'Starting'))
        yield request, self, gasstation
        print('%s %s %s' % (now(), self.name, 'Got a pump'))
        yield hold, self, 100.0
        yield release, self, gasstation
        print('%s %s %s' % (now(), self.name, 'Leaving'))


gasstation = Resource(capacity=2, name='gasStation', unitName='pump')
initialize()
c1 = Car('Car1', 2000)
c2 = Car('Car2', 1600)
c3 = Car('Car3', 3000)
c4 = Car('Car4', 1600)
activate(c1, c1.go(), at=4.0)  # activate at time 4.0
activate(c2, c2.go())          # activate at time 0.0
activate(c3, c3.go(), at=3.0)  # activate at time 3.0
activate(c4, c4.go(), at=3.0)  # activate at time 2.0
simulate(until=300)
print('Current time is %s' % now())
