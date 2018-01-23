from SimPy.Simulation import (Process, activate, hold, initialize, now,
                              reactivate, simulate)


class Bus(Process):

    def operate(self, repairduration, triplength):  # PEM
        tripleft = triplength                   # time needed to finish trip
        while tripleft > 0:
            yield hold, self, tripleft         # try to finish the trip
            if self.interrupted():             # if another breakdown occurs
                print('%s at %s' % (self.interruptCause.name, now()))
                tripleft = self.interruptLeft   # time to finish the trip
                self.interruptReset()           # end interrupt state
                reactivate(br, delay=repairduration)  # restart breakdown br
                yield hold, self, repairduration      # delay for repairs
                print('Bus repaired at %s' % now())
            else:
                break  # no more breakdowns, bus finished trip
        print('Bus has arrived at %s' % now())


class Breakdown(Process):
    def __init__(self, myBus):
        Process.__init__(self, name='Breakdown ' + myBus.name)
        self.bus = myBus

    def breakBus(self, interval):       # process execution method
        while True:
            yield hold, self, interval  # breakdown interarrivals
            if self.bus.terminated():
                break
            self.interrupt(self.bus)    # breakdown to myBus


initialize()
b = Bus('Bus')      # create a bus object
activate(b, b.operate(repairduration=20, triplength=1000))
br = Breakdown(b)   # create breakdown br to bus b
activate(br, br.breakBus(300))
simulate(until=4000)
print('SimPy: No more events at time %s' % now())
