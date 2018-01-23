""" bank22: An interruption by a phone call """
from SimPy.Simulation import *

# Model components ------------------------


class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank, onphone):
        print("%7.4f %s: Here I am" % (now(), self.name))
        yield hold, self, timeInBank  # 1
        if self.interrupted():  # 2
            timeleft = self.interruptLeft  # 3
            self.interruptReset()
            print("%7.4f %s: Excuse me" % (now(), self.name))
            print("%7.4f %s: Hello! I'll call back" % (now(), self.name))
            yield hold, self, onphone
            print("%7.4f %s: Sorry, where were we?" % (now(), self.name))  # 4
            yield hold, self, timeleft  # 5
        print("%7.4f %s: I must leave" % (now(), self.name))  # 6


class Call(Process):
    """ Cellphone call arrives and interrupts """

    def ring(self, klaus, timeOfCall):  # 7
        yield hold, self, timeOfCall  # 8
        print("%7.4f Ringgg!" % (now()))
        self.interrupt(klaus)

# Experiment data -------------------------


timeInBank = 20.0
timeOfCall = 9.0
onphone = 3.0
maxTime = 100.0


# Model/Experiment  ----------------------------------

initialize()
klaus = Customer(name="Klaus")
activate(klaus, klaus.visit(timeInBank, onphone))
call = Call(name="klaus")
activate(call, call.ring(klaus, timeOfCall))
simulate(until=maxTime)
