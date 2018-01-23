""" cellphone_OO.py

Simulate the operation of a BCC cellphone system.

Calls arrive at random to a cellphone hub with a fixed number of
channels. Service times are assumed exponential. The objective
is to determine the statistics of busy periods in the operation of a
BCC cellphone system.

The required measurements are
(1) the total busy time (all channels full) in each 1-hour period and
(2) the total number of busy times in a 1-hour period.

The simulation is continuous but the observing Process, a
Statistician, breaks the time into 1-hour observation periods
separated by 15-minute gaps to reduce autocorrelation. The total busy
time and number of busy times in each interval is printed.

   """
from SimPy.Simulation import *
import random as ran


# Model components ------------------------

class CallSource(Process):
    """ generates a sequence of calls """

    def execute(self, maxN, lam, cell):
        for i in range(maxN):
            j = Call("Call{0:03d}".format(i), sim=self.sim)
            self.sim.activate(j, j.execute(cell))
            yield hold, self, ran.expovariate(lam)


class Call(Process):
    """ Calls arrive at random at the cellphone hub"""

    def execute(self, cell):
        self.trace("arrived")
        if cell.Nfree == 0:
            self.trace("blocked and left")
        else:
            self.trace("got a channel")
            cell.Nfree -= 1
            if cell.Nfree == 0:
                self.trace("start busy period======")
                cell.busyStartTime = self.sim.now()
                cell.totalBusyVisits += 1
            yield hold, self, ran.expovariate(mu)
            self.trace("finished")
            if cell.Nfree == 0:
                self.trace("end   busy period++++++")
                cell.busyEndTime = self.sim.now()
                busy = self.sim.now() - cell.busyStartTime
                self.trace("         busy  = {0:9.4f}".format(busy))
                cell.totalBusyTime += busy
            cell.Nfree += 1

    def trace(self, message):
        if TRACING:
            print("{0:7.4f} {1:13s} {2}".format(
                self.sim.now(), message, self.name))


class Cell:
    """ Holds global measurements"""
    Nfree = 0
    totalBusyTime = 0.0
    totalBusyVisits = 0
    result = ()


class Statistician(Process):
    """ observes the system at intervals """

    def execute(self, Nperiods, obsPeriod, obsGap, cell):
        cell.busyEndTime = self.sim.now()  # simulation start time
        if STRACING:
            print("Busy time Number")
        for i in range(Nperiods):
            yield hold, self, obsGap
            cell.totalBusyTime = 0.0
            cell.totalBusyVisits = 0
            if cell.Nfree == 0:
                cell.busyStartTime = self.sim.now()
            yield hold, self, obsPeriod
            if cell.Nfree == 0:
                cell.totalBusyTime += self.sim.now() - cell.busyStartTime
            if STRACING:
                print("{0:7.3f} {1:5d}".format(
                    cell.totalBusyTime, cell.totalBusyVisits))
            self.sim.m.tally(cell.totalBusyTime)
            self.sim.bn.tally(cell.totalBusyVisits)
        self.sim.stopSimulation()
        cell.result = (self.sim.m.mean(), self.sim.m.var(),
                       self.sim.bn.mean(), self.sim.bn.var())

# Experiment data -------------------------


NChannels = 4         # number of channels in the cell
maxN = 10000
ranSeed = 3333333
lam = 1.0              # per minute
mu = 0.6667            # per minute
Nperiods = 10
obsPeriod = 60.0       # minutes
obsGap = 15.0       # gap between observation periods

TRACING = False
STRACING = True

# Model -----------------------------------


class CellphoneModel(Simulation):
    def run(self):
        self.initialize()
        self.m = Monitor(sim=self)
        self.bn = Monitor(sim=self)
        ran.seed(ranSeed)
        self.cell = Cell()           # the cellphone tower
        self.cell.Nfree = NChannels
        s = Statistician('Statistician', sim=self)
        self.activate(s, s.execute(Nperiods, obsPeriod, obsGap, self.cell))
        g = CallSource('CallSource', sim=self)
        self.activate(g, g.execute(maxN, lam, self.cell))
        self.simulate(until=10000.0)


# Experiment ------------------------------
modl = CellphoneModel()
modl.run()

# Output ----------------------------------
print('cellphone')
# input data:
print("lambda    mu      s  Nperiods obsPeriod  obsGap")
FMT = "{0:7.4f} {1:6.4f} {2:4d}   {3:4d}      {4:6.2f}   {5:6.2f}"
print(FMT.format(lam, mu, NChannels, Nperiods, obsPeriod, obsGap))

sr = modl.cell.result
print("Busy Time:   mean = {0:6.3f} var= {1:6.3f}".format(sr[0], sr[1]))
print("Busy Number: mean = {0:6.3f} var= {1:6.3f}".format(sr[2], sr[3]))
