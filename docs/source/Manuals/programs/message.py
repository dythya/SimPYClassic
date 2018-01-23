from SimPy.Simulation import Process, activate, initialize, hold, now, simulate


class Message(Process):
    """A simple Process"""

    def __init__(self, i, len):
        Process.__init__(self, name='Message' + str(i))
        self.i = i
        self.len = len

    def go(self):
        print('%s %s %s' % (now(), self.i, 'Starting'))
        yield hold, self, 100.0
        print('%s %s %s' % (now(), self.i, 'Arrived'))


initialize()
p1 = Message(1, 203)   # new message
activate(p1, p1.go())  # activate it
p2 = Message(2, 33)
activate(p2, p2.go(), at=6.0)
simulate(until=200)
print('Current time is %s' % now())  # will print 106.0
