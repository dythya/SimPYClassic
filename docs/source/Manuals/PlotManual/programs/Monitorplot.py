# Monitorplot.py
from random import uniform
from SimPy.Simulation import *
from SimPy.Recording import *
from SimPy.SimPlot import *


class Source(Process):
    def __init__(self, monitor):
        Process.__init__(self)
        self.moni = monitor
        self.arrived = 0

    def arrivalGenerator(self):
        while True:
            yield hold, self, uniform(0, 20)
            self.arrived += 1
            self.moni.observe(self.arrived)


initialize()
moni = Monitor(name="Arrivals", ylab="nr arrived")
s = Source(moni)
activate(s, s.arrivalGenerator())
simulate(until=100)

plt = SimPlot()
plt.plotStep(moni, color='blue')
plt.mainloop()
