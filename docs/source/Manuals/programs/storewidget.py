from SimPy.Simulation import (Lister, Process, Store, activate, get, hold,
                              initialize, now, put, simulate)


class ProducerD(Process):
    def __init__(self):
        Process.__init__(self)

    def produce(self):  # the ProducerD PEM
        while True:
            yield put, self, buf, [Widget(9), Widget(7)]
            yield hold, self, 10


class ConsumerD(Process):
    def __init__(self):
        Process.__init__(self)

    def consume(self):  # the ConsumerD PEM
        while True:
            toGet = 3
            yield get, self, buf, toGet
            assert len(self.got) == toGet
            print('%s Get widget weights %s' % (now(),
                                                [x.weight for x in self.got]))
            yield hold, self, 11


class Widget(Lister):
    def __init__(self, weight=0):
        self.weight = weight


widgbuf = []
for i in range(10):
    widgbuf.append(Widget(5))

initialize()

buf = Store(capacity=11, initialBuffered=widgbuf, monitored=True)

for i in range(3):  # define and activate 3 producer objects
    p = ProducerD()
    activate(p, p.produce())

for i in range(3):  # define and activate 3 consumer objects
    c = ConsumerD()
    activate(c, c.consume())

simulate(until=50)

print('LenBuffer: %s' % buf.bufferMon)  # length of buffer
print('getQ: %s' % buf.getQMon)         # length of getQ
print('putQ %s' % buf.putQMon)          # length of putQ
