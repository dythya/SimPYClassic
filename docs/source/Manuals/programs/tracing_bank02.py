import SimPy.SimulationTrace as Simulation  # <== changed for tracing
# import SimPy.Simulation as Simulation


""" Simulate a single customer """


class Customer(Simulation.Process):
    """ Customer arrives, looks around and leaves """

    def __init__(self, name):
        Simulation.Process.__init__(self)
        self.name = name

    def visit(self, timeInBank=0):
        print("%7.4f %s: Here I am" % (Simulation.now(), self.name))
        yield Simulation.hold, self, timeInBank
        print("%7.4f %s: I must leave" % (Simulation.now(), self.name))


def model():
    Simulation.initialize()
    c1 = Customer(name="Klaus")
    Simulation.activate(c1, c1.visit(timeInBank=10.0), delay=5.0)
    c2 = Customer(name="Tony")
    Simulation.activate(c2, c2.visit(timeInBank=8.0), delay=2.0)
    c3 = Customer(name="Evelyn")
    Simulation.activate(c3, c3.visit(timeInBank=20.0), delay=12.0)
    Simulation.simulate(until=400.0)


model()
