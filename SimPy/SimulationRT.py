# coding=utf-8
"""
SimulationRT provides synchronization of real time and SimPy simulation time.
Implements SimPy Processes, resources, and the backbone simulation scheduling
by coroutine calls.
Based on generators.

"""
from __future__ import division
from past.utils import old_div
import time

from SimPy.Simulation import *
import SimPy


class SimulationRT(Simulation):
    def __init__(self):
        if sys.platform == 'win32':  #take care of differences in clock accuracy
            self.wallclock = time.clock
        else:
            self.wallclock = time.time
        Simulation.__init__(self)

    def rtnow(self):
        return self.wallclock() - self.rtstart

    def rtset(self, rel_speed=1):
        """
        Resets the ratio simulation time over clock time(seconds).
        """
        # Ensure relative speed is a float.
        self.rel_speed = float(rel_speed)

    def simulate(self, until=0, real_time=False, rel_speed=1):
        """
        Simulates until simulation time reaches ``until``. If ``real_time`` is
        ``True`` a simulation time unit is matched with real time by the factor
        1 / ``rel_speed``.
        """
        try:
            self.rtstart = self.wallclock()
            self.rtset(rel_speed)

            while self._timestamps and not self._stop:
                next_event_time = self.peek()
                if next_event_time > until: break

                if real_time:
                    delay = (
                            old_div(next_event_time, self.rel_speed) -
                            (self.wallclock() - self.rtstart)
                    )
                    if delay > 0: time.sleep(delay)

                self.step()

            # There are still events in the timestamps list and the simulation
            # has not been manually stopped. This means we have reached the stop
            # time.
            if not self._stop and self._timestamps:
                self._t = until
                return 'SimPy: Normal exit'
            else:
                return 'SimPy: No activities scheduled'
        except Simerror as error:
            return 'SimPy: ' + error.value
        finally:
            self._stop = True



# For backward compatibility
Globals.sim = SimulationRT()

def rtnow():
    return Globals.sim.rtnow()

rtset =  Globals.sim.rtset

def simulate(until = 0, real_time = False, rel_speed = 1):
    return Globals.sim.simulate(until = until, real_time = real_time, rel_speed = rel_speed)

wallclock = Globals.sim.wallclock

allMonitors = Globals.sim.allMonitors

allTallies = Globals.sim.allTallies
# End backward compatibility
