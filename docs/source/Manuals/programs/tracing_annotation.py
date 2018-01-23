import SimPy.SimulationTrace as Simulation


class Bus(Simulation.Process):
    def __init__(self, name):
        Simulation.Process.__init__(self, name)

    def operate(self, repairduration=0):
        tripleft = 1000
        while tripleft > 0:
            Simulation.trace.ttext("Try to go for %s" % tripleft)
            yield Simulation.hold, self, tripleft
            if self.interrupted():
                tripleft = self.interruptLeft
                self.interruptReset()
                Simulation.trace.ttext("Start repair taking %s time units" %
                                       repairduration)
                yield Simulation.hold, self, repairduration
            else:
                break  # no breakdown,  ergo bus arrived
        Simulation.trace.ttext("<%s> has arrived" % self.name)


class Breakdown(Simulation.Process):
    def __init__(self, myBus):
        Simulation.Process.__init__(self, name="Breakdown " + myBus.name)
        self.bus = myBus

    def breakBus(self, interval):

        while True:
            Simulation.trace.ttext("Breakdown process waiting for %s" %
                                   interval)
            yield Simulation.hold, self, interval
            if self.bus.terminated():
                break
            Simulation.trace.ttext("Breakdown of %s" % self.bus.name)
            self.interrupt(self.bus)


print("\n\n+++test_interrupt")
Simulation.initialize()
b = Bus("Bus 1")
Simulation.trace.ttext("Start %s" % b.name)
Simulation.activate(b, b.operate(repairduration=20))
br = Breakdown(b)
Simulation.trace.ttext("Start the Breakdown process for %s" % b.name)
Simulation.activate(br, br.breakBus(200))
Simulation.trace.start = 100
print(Simulation.simulate(until=4000))
