""" bank22_OO: An interruption by a phone call """
from SimPy.Simulation import Simulation, Process, hold

# Model components ------------------------


class Customer(Process):
    """ Customer arrives, looks around and leaves """

    def visit(self, timeInBank, onphone):
        print("%7.4f %s: Here I am" % (self.sim.now(), self.name))
        yield hold, self, timeInBank
        if self.interrupted():
            timeleft = self.interruptLeft
            self.interruptReset()
            print("%7.4f %s: Excuse me" % (self.sim.now(), self.name))
            print("%7.4f %s: Hello! I'll call back" %
                  (self.sim.now(), self.name))
            yield hold, self, onphone
            print("%7.4f %s: Sorry, where were we?" %
                  (self.sim.now(), self.name))
            yield hold, self, timeleft
        print("%7.4f %s: I must leave" % (self.sim.now(), self.name))


class Call(Process):
    """ Cellphone call arrives and interrupts """

    def ring(self, klaus, timeOfCall):
        yield hold, self, timeOfCall
        print("%7.4f Ringgg!" % (self.sim.now()))
        self.interrupt(klaus)

# Model -----------------------------------


class BankModel(Simulation):
    def run(self):
        """ PEM """
        klaus = Customer(name="Klaus", sim=self)
        self.activate(klaus, klaus.visit(timeInBank, onphone))
        call = Call(sim=self)
        self.activate(call, call.ring(klaus, timeOfCall))
        self.simulate(until=maxTime)

# Experiment data -------------------------


timeInBank = 20.0
timeOfCall = 9.0
onphone = 3.0
maxTime = 100.0

# Experiment  -----------------------------
mymodel = BankModel()
mymodel.run()
