from SimPy.Simulation import (PriorityQ, Process, Resource, activate,
                              initialize, hold, now, release, request,
                              simulate)


class Client(Process):
    def __init__(self, name):
        Process.__init__(self, name)

    def getserved(self, servtime, priority, myServer):
        print('%s requests 1 unit at t=%s' % (self.name, now()))
        yield request, self, myServer, priority
        yield hold, self, servtime
        yield release, self, myServer
        print('%s done at t=%s' % (self.name, now()))


initialize()
# create the *server* Resource object
server = Resource(capacity=1, qType=PriorityQ, preemptable=1)
# create some Client process objects
c1 = Client(name='c1')
c2 = Client(name='c2')
activate(c1, c1.getserved(servtime=100, priority=1, myServer=server), at=0)
activate(c2, c2.getserved(servtime=100, priority=9, myServer=server), at=50)
simulate(until=500)
