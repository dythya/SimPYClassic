# simstep_stepping2fast.py

if __debug__:
    import SimPy.SimulationStep as Simulation
else:
    import SimPy.Simulation as Simulation


def callbackUserControl():
    """Allows user to control stepping
    """
    if __debug__:
        # In python 2.7 you need to make this raw_input
        a = input("[Time=%s] Select one: End run (e), Continue stepping (s),"
                  "Run to end (r)= " % Simulation.now())
        if a == "e":
            Simulation.stopSimulation()
        elif a == "s":
            return
        else:
            Simulation.stopStepping()


class Man(Simulation.Process):
    def walk(self):
        print("got up")
        yield Simulation.hold, self, 1
        print("got to door")
        yield Simulation.hold, self, 10
        print("got to mail box")
        yield Simulation.hold, self, 10
        print("got home again")


# allow user control if debugging
Simulation.initialize()
otto = Man()
Simulation.activate(otto, otto.walk())
if __debug__:
    Simulation.startStepping()
    Simulation.simulate(callback=callbackUserControl, until=100)
else:
    Simulation.simulate(until=100)
