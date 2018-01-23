"""bank14: *waituntil* the Bank door opens"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------
door = 'Shut'  # 1


def dooropen():  # 2
    return door == 'Open'


class Doorman(Process):  # 3
    """ Doorman opens the door"""

    def openthedoor(self):
        """ He will open the door when he arrives"""
        global door
        yield hold, self, expovariate(1.0 / 10.0)  # 4
        door = 'Open'
        print("%7.4f Doorman: Ladies and "
              "Gentlemen! You may all enter." % (now()))


class Source(Process):
    """ Source generates customers randomly"""

    def generate(self, number, rate):
        for i in range(number):
            c = Customer(name="Customer%02d" % (i))
            activate(c, c.visit(timeInBank=12.0))
            yield hold, self, expovariate(rate)


class Customer(Process):  # 5
    """ Customer arrives, is served and leaves """

    def visit(self, timeInBank=10):
        arrive = now()
        if dooropen():
            msg = ' and the door is open.'
        else:
            msg = ' but the door is shut.'
        print("%7.4f %s: Here I am%s" % (now(), self.name, msg))

        yield waituntil, self, dooropen  # 6

        print("%7.4f %s: I can  go in!" % (now(), self.name))
        wait = now() - arrive
        print("%7.4f %s: Waited %6.3f" % (now(), self.name, wait))

        yield request, self, counter
        tib = expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter

        print("%7.4f %s: Finished    " % (now(), self.name))

# Experiment data -------------------------


maxTime = 2000.0   # minutes
counter = Resource(1, name="Clerk")

# Model  ----------------------------------


def model(SEED=393939):
    seed(SEED)

    initialize()
    door = 'Shut'
    doorman = Doorman()  # 7
    activate(doorman, doorman.openthedoor())  # 8
    source = Source()
    activate(source,
             source.generate(number=5, rate=0.1), at=0.0)
    simulate(until=400.0)


# Experiment  ----------------------------------
model()
