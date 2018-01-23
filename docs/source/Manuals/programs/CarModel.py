# CarModel.py
import SimPy.Simulation as simulation
"""Advanced Object Oriented SimPy API"""

# Model components -------------------------------


class Car(simulation.Process):
    def park(self):
        yield simulation.request, self, self.sim.parking
        yield simulation.hold, self, 10
        yield simulation.release, self, self.sim.parking
        print("%s done at %s" % (self.name, self.sim.now()))

# Model ------------------------------------------


class Model(simulation.Simulation):
    def __init__(self, name, nrCars, spaces):
        simulation.Simulation.__init__(self)
        self.name = name
        self.nrCars = nrCars
        self.spaces = spaces

    def runModel(self):
        # Initialize Simulation instance
        self.initialize()
        self.parking = simulation.Resource(name="Parking lot",
                                           unitName="spaces",
                                           capacity=self.spaces, sim=self)
        for i in range(self.nrCars):
            auto = Car(name="Car%s" % i, sim=self)
            self.activate(auto, auto.park())
        self.simulate(until=100)


if __name__ == "__main__":

    # Experiment ----------------------------------
    myModel = Model(name="Experiment 1", nrCars=10, spaces=5)
    myModel.runModel()
    print(myModel.now())
