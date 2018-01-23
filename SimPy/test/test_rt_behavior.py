# coding=utf-8

import pytest
from SimPy.SimulationRT import *


class Ticker(Process):
    def tick(self):
        self.timing = []
        while True:
            yield hold,self,1
            tSim = self.sim.now()
            tRT = self.sim.rtnow()
            self.timing.append((tSim,tRT))

@pytest.mark.xfail(reason="No way of guaranteeing how fast a machine runs")
def test_ticker():
    """Tests SimulationRT for degree to which simulation time and wallclock
    time can be synchronized."""
    rel_speed = 10
    sim_slow=SimulationRT()
    t=Ticker(sim=sim_slow)
    sim_slow.activate(t,t.tick())
    sim_slow.simulate(until=10,real_time=True,rel_speed=rel_speed)

    for tSim, tRT in t.timing:
        assert tSim/tRT > rel_speed - 1

    rel_speed = 20
    sim_fast=SimulationRT()
    sim_fast.initialize()
    t=Ticker(sim=sim_fast)
    sim_fast.activate(t,t.tick())
    sim_fast.simulate(until=10,real_time=True,rel_speed=rel_speed)

    for tSim, tRT in t.timing:
        assert tSim/tRT > rel_speed - 1
