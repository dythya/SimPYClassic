"""variableTimeRatio.py
Shows the SimulationRT capability to change the ratio simulation
time to wallclock time during the run of a simulation.
"""
import SimPy.SimulationRT as SimulationRT


class Changer(SimulationRT.Process):
    def change(self, when, rat):
        global ratio
        yield SimulationRT.hold, self, when
        SimulationRT.rtset(rat)
        ratio = rat


class Series(SimulationRT.Process):
    def tick(self, nrTicks):
        oldratio = ratio
        for i in range(nrTicks):
            tLastSim = SimulationRT.now()
            tLastWallclock = SimulationRT.wallclock()
            yield SimulationRT.hold, self, 1
            diffSim = SimulationRT.now() - tLastSim
            diffWall = SimulationRT.wallclock() - tLastWallclock
            print("now(): %s, sim. time elapsed: %s, wall clock elapsed: "
                  "%6.3f, sim/wall time ratio: %6.3f" %
                  (SimulationRT.now(), diffSim, diffWall, diffSim / diffWall))
            if not ratio == oldratio:
                print("At simulation time %s: ratio simulation/wallclock "
                      "time now changed to %s" % (SimulationRT.now(), ratio))
                oldratio = ratio


SimulationRT.initialize()
ticks = 15
s = Series()
SimulationRT.activate(s, s.tick(nrTicks=ticks))
c = Changer()
SimulationRT.activate(c, c.change(5, 5))
c = Changer()
SimulationRT.activate(c, c.change(10, 10))
ratio = 1
print("At simulation time %s: set ratio simulation/wallclock time to %s" %
      (SimulationRT.now(), ratio))
SimulationRT.simulate(until=100, real_time=True, rel_speed=ratio)
