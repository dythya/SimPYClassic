# Example.py - Example for SimulationGUIDebug
from SimPy.SimulationGUIDebug import *  # import SimulationGUIDebug

# Creates man


class SuperBeing(Process):
    def __init__(self, earth):
        Process.__init__(self)
        self.earth = earth

    def Create(self):
        while True:
            yield hold, self, 1.20
            man = Man(self.earth)
            activate(man, man.Walk())
            register(man, man.Status)  # register the man instance with hook

# Man waits for earth resource, then becomes, baby, adult, and leaves earth


class Man(Process):
    ID = 0

    def __init__(self, earth):
        # set name to ensure window title is set
        Process.__init__(self, name="Man{0}".format(Man.ID))
        self.earth = earth
        self.status = "in heaven"
        Man.ID += 1

    def Walk(self):
        self.status = "waiting for earth "
        yield request, self, self.earth
        self.status = "baby"
        yield hold, self, 1
        self.status = "adult"
        yield hold, self, 2
        self.status = "good bye earth"
        yield release, self, self.earth

    def Status(self):
        return self.status


# set up
initialize()
register(SuperBeing, name="SuperBeing")  # register SuperBeing class with name

Earth = Resource(2, name="Earth")  # set name to ensure window title is set
register(Earth)  # register Earth Resource

SB = SuperBeing(Earth)
activate(SB, SB.Create())  # when activated SB will be registered

# simulate
simulate(until=1000)
