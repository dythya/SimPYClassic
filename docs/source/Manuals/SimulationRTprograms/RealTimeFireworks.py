""" RealTimeFireworks.py """
import SimPy.SimulationRT as SimulationRT
from random import seed, uniform
import time


# Model components -----------------------------------------------------------
class Launcher(SimulationRT.Process):
    def launch(self):
        while True:
            print("Launch at %2.4f; wallclock: %2.4f" %
                  (SimulationRT.now(),
                   time.clock() - startTime))
            yield SimulationRT.hold, self, uniform(1, maxFlightTime)
            print("Boom!!! Aaaah!! at %2.4f; wallclock: %2.4f" %
                  (SimulationRT.now(), time.clock() - startTime))


def model():
    SimulationRT.initialize()
    for i in range(nrLaunchers):
        lau = Launcher()
        SimulationRT.activate(lau, lau.launch())
    SimulationRT.simulate(
        real_time=True, rel_speed=1, until=20)  # unit sim time = 1 sec clock


# Experiment data  -----------------------------------------------------------
nrLaunchers = 2
maxFlightTime = 5.0
startTime = time.clock()
seed(1234567)
# Experiment -----------------------------------------------------------------
model()
