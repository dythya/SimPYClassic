import SimPy.SimulationTrace as Simulation


class Client(Simulation.Process):
    def __init__(self, name):
        Simulation.Process.__init__(self, name)

    def getServed(self, tank):
        yield (Simulation.get, self, tank, 10), (Simulation.hold, self, 1.5)
        if self.acquired(tank):
            print("%s got 10 %s" % (self.name, tank.unitName))
        else:
            print("%s reneged" % self.name)


class Filler(Simulation.Process):
    def __init__(self, name):
        Simulation.Process.__init__(self, name)

    def fill(self, tank):
        for i in range(3):
            yield Simulation.hold, self, 1
            yield Simulation.put, self, tank, 10


Simulation.initialize()
tank = Simulation.Level(name="Tank", unitName="gallons")
for i in range(2):
    c = Client("Client %s" % i)
    Simulation.activate(c, c.getServed(tank))
f = Filler("Tanker")
Simulation.activate(f, f.fill(tank))
Simulation.simulate(until=10)
