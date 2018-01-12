# simstep_stepping2.py
import SimPy.SimulationStep as SimulationStep


def callbackUserControl():
    """Allows user to control stepping
    """
    # In python 2.7 you need to make this raw_input
    a = input("[Time=%s] Select one: End run (e), Continue stepping (s), "
              "Run to end (r)= " % SimulationStep.now())
    if a == "e":
        SimulationStep.stopSimulation()
    elif a == "s":
        return
    else:
        SimulationStep.stopStepping()


class Man(SimulationStep.Process):
    def walk(self):
        print("got up")
        yield SimulationStep.hold, self, 1
        print("got to door")
        yield SimulationStep.hold, self, 10
        print("got to mail box")
        yield SimulationStep.hold, self, 10
        print("got home again")


# allow user control
SimulationStep.initialize()
otto = Man()
SimulationStep.activate(otto, otto.walk())
SimulationStep.startStepping()
SimulationStep.simulate(callback=callbackUserControl, until=100)
