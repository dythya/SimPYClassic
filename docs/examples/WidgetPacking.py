"""WidgetPacking.py
Scenario:
In a factory, nProd widget-making machines produce widgets with a weight
widgWeight (uniformly distributed [widgWeight-dWeight..widgWeight+dWeight])
on average every tMake minutes (uniform distribution
[tmake-deltaT..tMake+deltaT]).A widget-packing machine packs widgets in tPack
minutes into packages. Simulate for simTime minutes.

Model 1:
The widget-packer packs nWidgets into a package.

Model 2:
The widget-packer packs widgets into a package with package weight not
to exceed packMax.
"""
from SimPy.Simulation import *
import random

# Experiment data -------------------------
nProd = 2  # widget-making machines
widgWeight = 20  # kilogrammes
dWeight = 3  # kilogrammes
tMake = 2  # minutes
deltaT = 0.75  # minutes
tPack = 0.25  # minutes per idget
initialSeed = 1234567  # for random number stream
simTime = 100  # minutes

print('WidgetPacking')
################################################################
#
# Model 1
#
#################################################################
# Data
nWidgets = 6  # widgets per package


class Widget:
    def __init__(self, weight):
        self.weight = weight


class WidgetMakerN(Process):
    """Produces widgets"""

    def make(self, buffer):
        while True:
            yield hold, self, r.uniform(tMake - deltaT, tMake + deltaT)
            yield put, self, buffer, 1         # buffer 1 widget


class WidgetPackerN(Process):
    """Packs a number of widgets into a package"""

    def pack(self, buffer):
        while True:
            for i in range(nWidgets):
                yield get, self, buffer, 1  # get widget
                yield hold, self, tPack  # pack it
            print("{0}: package completed".format(now()))


print("Model 1: pack {0} widgets per package".format(nWidgets))
initialize()
r = random.Random()
r.seed(initialSeed)
wBuffer = Level(name="WidgetBuffer", capacity=500)
for i in range(nProd):
    wm = WidgetMakerN(name="WidgetMaker{0}".format(i))
    activate(wm, wm.make(wBuffer))
wp = WidgetPackerN(name="WidgetPacker")
activate(wp, wp.pack(wBuffer))
simulate(until=simTime)

################################################################
#
# Model 2
#
#################################################################
# Data
packMax = 120  # kilogrammes per package (max)


class WidgetMakerW(Process):
    """Produces widgets"""

    def make(self, buffer):
        while True:
            yield hold, self, r.uniform(tMake - deltaT, tMake + deltaT)
            widgetWeight = r.uniform(
                widgWeight - dWeight, widgWeight + dWeight)
            # buffer widget
            yield put, self, buffer, [Widget(weight=widgetWeight)]


class WidgetPackerW(Process):
    """Packs a number of widgets into a package"""

    def pack(self, buffer):
        weightLeft = 0
        while True:
            packWeight = weightLeft  # pack a widget which did not fit
            # into previous package
            weightLeft = 0
            while True:
                yield get, self, buffer, 1  # get widget
                weightReceived = self.got[0].weight
                if weightReceived + packWeight <= packMax:
                    yield hold, self, tPack  # pack it
                    packWeight += weightReceived
                else:
                    weightLeft = weightReceived  # for next package
                    break
                print("{0}: package completed. Weight= {1:6.2f} kg".format(
                    now(), packWeight))


print(
    "\nModel 2: pack widgets up to max package weight of {0}".format(packMax))
initialize()
r = random.Random()
r.seed(initialSeed)
wBuffer = Store(name="WidgetBuffer", capacity=500)
for i in range(nProd):
    wm = WidgetMakerW(name="WidgetMaker{0}".format(i))
    activate(wm, wm.make(wBuffer))
wp = WidgetPackerW(name="WidgetPacker")
activate(wp, wp.pack(wBuffer))
simulate(until=simTime)
