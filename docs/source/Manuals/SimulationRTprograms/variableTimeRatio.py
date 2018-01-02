"""variableTimeRatio.py
Shows the SimulationRT capability to change the ratio simulation
time to wallclock time during the run of a simulation.
"""
from SimPy.SimulationRT import *

class Changer(Process):
    def change(self,when,rat):
        global ratio
        yield hold,self,when
        rtset(rat)
        ratio=rat
class Series(Process):
    def tick(self,nrTicks):
        oldratio=ratio
        for i in range(nrTicks):
            tLastSim=now()
            tLastWallclock=wallclock()
            yield hold,self,1
            diffSim=now()-tLastSim
            diffWall=wallclock()-tLastWallclock
            print("now(): %s, sim. time elapsed: %s, wall clock elapsed: "\
                  "%6.3f, sim/wall time ratio: %6.3f"\
                  %(now(),diffSim,diffWall,diffSim/diffWall))
            if not ratio==oldratio:
                print("At simulation time %s: ratio simulation/wallclock "\
                    "time now changed to %s"%(now(),ratio))
                oldratio=ratio

initialize()
ticks=15
s=Series()
activate(s,s.tick(nrTicks=ticks))
c=Changer()
activate(c,c.change(5,5))
c=Changer()
activate(c,c.change(10,10))
ratio=1
print("At simulation time %s: set ratio simulation/wallclock time to %s"\
      %(now(),ratio))
simulate(until=100,real_time=True,rel_speed=ratio)
