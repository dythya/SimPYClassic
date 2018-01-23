__doc__ = """ GUIdemo.py
This is a very basic model, demonstrating the ease
of interfacing to SimGUI.
"""
from SimPy.Simulation import *
from random import *
from SimPy.SimGUI import *

# Model components ------------------------


class Launcher(Process):
    nrLaunched = 0

    def launch(self):
        while True:
            gui.writeConsole("Launch at {0:.1f}".format(now()))
            Launcher.nrLaunched += 1
            gui.launchmonitor.observe(Launcher.nrLaunched)
            yield hold, self, uniform(1, gui.params.maxFlightTime)
            gui.writeConsole("Boom!!! Aaaah!! at {0:.1f}".format(now()))


def model():
    gui.launchmonitor = Monitor(name="Rocket counter",
                                ylab="nr launched", tlab="time")
    initialize()
    Launcher.nrLaunched = 0
    for i in range(gui.params.nrLaunchers):
        lau = Launcher()
        activate(lau, lau.launch())
    simulate(until=gui.params.duration)
    gui.noRunYet = False
    gui.writeStatusLine("{0} rockets launched in {1:.1f} minutes"
                        .format(Launcher.nrLaunched, now()))


class MyGUI(SimGUI):
    def __init__(self, win, **par):
        SimGUI.__init__(self, win, **par)
        self.run.add_command(label="Start fireworks",
                             command=model, underline=0)
        self.params = Parameters(duration=duration,
                                 maxFlightTime=maxFlightTime,
                                 nrLaunchers=nrLaunchers)

# Experiment data ---------------------------------------


duration = 2000
maxFlightTime = 11.7
nrLaunchers = 3

# Model/Experiment/Display  ------------------------------

root = Tk()
gui = MyGUI(root, title="RocketGUI", doc=__doc__, consoleHeight=40)
gui.mainloop()
