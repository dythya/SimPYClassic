# simstep_stepping1.py
import SimPy.SimulationStep as SimulationStep       # (1)


def callbackTimeTrace():                            # (2)
    """Prints event times
    """
    print("at time=%s" % SimulationStep.now())


class Man(SimulationStep.Process):
    def walk(self):
        print("got up")
        yield SimulationStep.hold, self, 1
        print("got to door")
        yield SimulationStep.hold, self, 10
        print("got to mail box")
        yield SimulationStep.hold, self, 10
        print("got home again")


# trace event times
SimulationStep.initialize()
otto = Man()
SimulationStep.activate(otto, otto.walk())
SimulationStep.startStepping()                      # (3)
SimulationStep.simulate(callback=callbackTimeTrace, until=100)  # (4)
