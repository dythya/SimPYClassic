# CarModelExtension.py

# Model components -------------------------------

import SimPy.Simulation as simulation
import CarModel


class Van(simulation.Process):
    def park(self):
        yield simulation.request, self, self.sim.parking
        yield simulation.hold, self, 5
        yield simulation.release, self, self.sim.parking
        print("%s done at %s" % (self.name, self.sim.now()))


# Model ------------------------------------------


class ModelExtension(CarModel.Model):
    def __init__(self, name, nrCars, spaces, nrTrucks):
        CarModel.Model.__init__(self, name=name, nrCars=nrCars, spaces=spaces)
        self.nrTrucks = nrTrucks

    def runModel(self):
        self.initialize()
        self.parking = simulation.Resource(name="Parking lot",
                                           capacity=self.spaces,
                                           sim=self)
        for i in range(self.nrCars):
            auto = CarModel.Car(name="Car%s" % i, sim=self)
            self.activate(auto, auto.park())
        for i in range(self.nrTrucks):
            truck = Van(name="Van%s" % i, sim=self)
            self.activate(truck, truck.park())
        self.simulate(until=100)


# Experiment ----------------------------------

myModel1 = ModelExtension(name="Experiment 2", nrCars=10, spaces=5, nrTrucks=3)
myModel1.runModel()
