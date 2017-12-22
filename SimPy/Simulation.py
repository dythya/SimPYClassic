# coding=utf-8
"""
Simulation implements SimPy Processes, Resources, Buffers, and the backbone simulation
scheduling by coroutine calls. Provides data collection through classes
Monitor and Tally.
Based on generators

"""
from builtins import next
from builtins import object
import random
import sys
import types
from heapq import heappush, heappop

from SimPy.Lister import Lister
from SimPy.Recording import Monitor, Tally
from SimPy.Lib import Process, SimEvent, PriorityQ, Resource, Level, \
                      Store, Simerror, FatalSimerror, FIFO

# Required for backward compatibility
import SimPy
import SimPy.Globals as Globals
from SimPy.Globals import initialize, simulate, now, stopSimulation, \
        allEventNotices, allEventTimes, startCollection,\
        _startWUStepping, _stopWUStepping, activate, reactivate


# yield keywords
hold = 1
passivate = 2
request = 3
release = 4
waitevent = 5
queueevent = 6
waituntil = 7
get = 8
put = 9


class Infinity(object):
    def __cmp__(self, other):
        return 1

infinity = Infinity()

def holdfunc(a):
    a[0][1]._hold(a)

def requestfunc(a):
    """Handles 'yield request, self, res' and
    'yield (request, self, res),(<code>,self, par)'.
    <code > can be 'hold' or 'waitevent'.
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance
        b[2]._request(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,name,sim=None):
                Process.__init__(self,name=name,sim=sim)
            def trigger(self, delay):
                yield hold, self, delay
                if not proc in b[2].activeQ:
                    proc.sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,name,sim=None):
                Process.__init__(self,name=name,sim=sim)
            def trigger(self, event):
                yield waitevent, self, event
                if not proc in b[2].activeQ:
                    proc.eventsFired = self.eventsFired
                    proc.sim.reactivate(proc)

        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name = 'RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            proc.sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name = 'RENEGE - waitevent for %s'\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            proc.sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._request(a)

def releasefunc(a):
    a[0][2]._release(a)

def passivatefunc(a):
    a[0][1]._passivate(a)

def waitevfunc(a):
    #if waiting for one event only (not a tuple or list)
    evtpar = a[0][2]
    if isinstance(evtpar, SimEvent):
        a[0][2]._wait(a)
    # else, if waiting for an OR of events (list / tuple):
    else: #it should be a list / tuple of events
        # call _waitOR for first event
        evtpar[0]._waitOR(a)

def queueevfunc(a):
    #if queueing for one event only (not a tuple or list)
    evtpar = a[0][2]
    if isinstance(evtpar, SimEvent):
        a[0][2]._queue(a)
    #else, if queueing for an OR of events (list / tuple):
    else: #it should be a list / tuple of events
        # call _queueOR for first event
        evtpar[0]._queueOR(a)

def waituntilfunc(par):
    par[0][1].sim._waitUntilFunc(par[0][1], par[0][2])

def getfunc(a):
    """Handles 'yield get, self, buffer, what, priority' and
    'yield (get, self, buffer, what, priority),(<code>,self, par)'.
    <code > can be 'hold' or 'waitevent'.
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance
        b[2]._get(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, delay):
                yield hold, self, delay
                #if not proc in b[2].activeQ:
                if proc in b[2].getQ:
                    a[1].sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, event):
                yield waitevent, self, event
                if proc in b[2].getQ:
                    a[1].eventsFired = self.eventsFired
                    a[1].sim.reactivate(proc)

        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name='RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('waituntil: Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name="RENEGE - waitevent for%s"\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._get(a)


def putfunc(a):
    """Handles 'yield put' (simple and compound hold / waitevent)
    """
    if type(a[0][0]) == tuple:
        ## Compound yield request statement
        ## first tuple in ((request, self, res),(xx, self, yy))
        b = a[0][0]
        ## b[2] == res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance
        b[2]._put(arg = (b, a[1]))
        ##deal with add - on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, delay):
                yield hold, self, delay
                #if not proc in b[2].activeQ:
                if proc in b[2].putQ:
                    a[1].sim.reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def __init__(self,**par):
                Process.__init__(self,**par)
            def trigger(self, event):
                yield waitevent, self, event
                if proc in b[2].putQ:
                    a[1].eventsFired = self.eventsFired
                    a[1].sim.reactivate(proc)

        #activate it
        proc = a[0][0][1] # the process to be woken up
        actCode = a[0][1][0]
        if actCode == hold:
            proc._holder = _Holder(name='RENEGE - hold for %s'%proc.name,
                                   sim=proc.sim)
            ##                                          the timeout delay
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == waituntil:
            raise FatalSimerror('Illegal code for reneging: waituntil')
        elif actCode == waitevent:
            proc._holder = _EventWait(name='RENEGE - waitevent for %s'\
                                      %proc.name,sim=proc.sim)
            ##                                          the event
            a[1].sim.activate(proc._holder, proc._holder.trigger(a[0][1][2]))
        elif actCode == queueevent:
            raise FatalSimerror('Illegal code for reneging: queueevent')
        else:
            raise FatalSimerror('Illegal code for reneging %s'%actCode)
    else:
        ## Simple yield request command
        a[0][2]._put(a)


class Simulation(object):
    _dispatch = {
            hold: holdfunc, request: requestfunc, release: releasefunc,
            passivate: passivatefunc, waitevent: waitevfunc,
            queueevent: queueevfunc, waituntil: waituntilfunc, get: getfunc,
            put: putfunc,
    }
    _commandcodes = list(_dispatch.keys())
    _commandwords = {
            hold: 'hold', request: 'request', release: 'release',
            passivate: 'passivate', waitevent: 'waitevent',
            queueevent: 'queueevent', waituntil: 'waituntil', get: 'get',
            put: 'put'
    }

    def __init__(self):
        self.initialize()

    def initialize(self):
        self._t = 0
        self.next_time = 0

        # Eventqueue stuff.
        self._timestamps = []
        self._sortpr = 0

        self._start = False
        self._stop = False
        self.condQ = []
        self.allMonitors = []
        self.allTallies = []

    def now(self):
        return self._t

    def stopSimulation(self):
        """Application function to stop simulation run"""
        self._stop = True

    def _post(self, what, at, prior = False):
        """Post an event notice for process what for time at"""
        # event notices are Process instances
        if at < self._t:
            raise FatalSimerror('Attempt to schedule event in the past')
        what._nextTime = at
        self._sortpr -= 1
        if prior:
            # before all other event notices at this time
            # heappush with highest priority value so far (negative of
            # monotonely decreasing number)
            # store event notice in process instance
            what._rec = [at, self._sortpr, what, False]
            # make event list refer to it
            heappush(self._timestamps, what._rec)
        else:
            # heappush with lowest priority
            # store event notice in process instance
            what._rec = [at,-self._sortpr, what, False]
            # make event list refer to it
            heappush(self._timestamps, what._rec)

    def _unpost(self, whom):
        """
        Mark event notice for whom as cancelled if whom is a suspended process
        """
        if whom._nextTime is not None:  # check if whom was actually active
            whom._rec[3] = True ## Mark as cancelled
            whom._nextTime = None

    def allEventNotices(self):
        """Returns string with eventlist as;
                t1: processname, processname2
                t2: processname4, processname5, . . .
                . . .  .
        """
        ret = ''
        tempList = []
        tempList[:] = self._timestamps
        tempList.sort()
        # return only event notices which are not cancelled
        tempList = [[x[0],x[2].name] for x in tempList if not x[3]]
        tprev = -1
        for t in tempList:
            # if new time, new line
            if t[0] == tprev:
                # continue line
                ret += ', %s'%t[1]
            else:
                # new time
                if tprev == -1:
                    ret = '%s: %s' % (t[0],t[1])
                else:
                    ret += '\n%s: %s' % (t[0],t[1])
                tprev = t[0]
        return ret + '\n'

    def allEventTimes(self):
        """Returns list of all times for which events are scheduled.
        """
        r = []
        r[:] = self._timestamps
        r.sort()
        # return only event times of not cancelled event notices
        r1 = [x[0] for x in r if not x[3]]
        tprev = -1
        ret = []
        for t in r1:
            if t == tprev:
                #skip time, already in list
                pass
            else:
                ret.append(t)
                tprev = t
        return ret

    def activate(self, obj, process, at = 'undefined', delay = 'undefined',
                 prior = False):
        """Application function to activate passive process."""
        if __debug__:
            if not (obj.sim == self):
                raise FatalSimerror('activate: Process %s not in activating '
                        'Simulation instance' % obj.name)
            if not (type(process) == types.GeneratorType):
                raise FatalSimerror('Activating function which'+
                    ' is not a generator (contains no \'yield\')')
        if not obj._terminated and not obj._nextTime:
            #store generator reference in object; needed for reactivation
            obj._nextpoint = process
            if at == 'undefined':
                at = self._t
            if delay == 'undefined':
                zeit = max(self._t, at)
            else:
                zeit = max(self._t, self._t + delay)
            self._post(obj, at = zeit, prior = prior)

    def reactivate(self, obj, at = 'undefined', delay = 'undefined',
                   prior = False):
        """Application function to reactivate a process which is active,
        suspended or passive."""
        # Object may be active, suspended or passive
        if not obj._terminated:
            a = Process('SimPysystem',sim=self)
            a.cancel(obj)
            # object now passive
            if at == 'undefined':
                at = self._t
            if delay == 'undefined':
                zeit = max(self._t, at)
            else:
                zeit = max(self._t, self._t + delay)
            self._post(obj, at = zeit, prior = prior)

    def startCollection(self, when = 0.0, monitors = None, tallies = None):
        """Starts data collection of all designated Monitor and Tally objects
        (default = all) at time 'when'.
        """
        class Starter(Process):
            def collect(self, monitors, tallies):
                for m in monitors:
                    m.reset()
                for t in tallies:
                    t.reset()
                yield hold, self
        if monitors is None:
            monitors = self.allMonitors
        if tallies is None:
            tallies = self.allTallies
        if when == 0.0:
            for m in monitors:
                try:
                    ylast = m[-1][1]
                    empty = False
                except IndexError:
                    empty = True
                m.reset()
                if not empty:
                    m.observe(t = now(), y = ylast)
            for t in tallies:
                t.reset()
        else:
            s = Starter(sim = self)
            self.activate(s, s.collect(monitors = monitors, tallies = tallies),\
                      at = when, prior = True)


    def _waitUntilFunc(self, proc, cond):
        """
        Puts a process 'proc' waiting for a condition into a waiting queue.
        'cond' is a predicate function which returns True if the condition is
        satisfied.
        """
        if not cond():
            self.condQ.append(proc)
            proc.cond = cond
            # passivate calling process
            proc._nextTime = None
        else:
            #schedule continuation of calling process
            self._post(proc, at = self._t, prior = 1)

    def _terminate(self, process):
        """Marks a process as terminated."""
        process._nextpoint = None
        process._terminated = True
        process._nextTime = None

    def has_events(self):
        """
        Checks if there are events which can be processed. Returns ``True`` if
        there are events and the simulation has not been stopped.
        """
        return not self._stop and self._timestamps

    def peek(self):
        """
        Returns the time of the next event or infinity, if no
        more events are scheduled.
        """
        if not self._timestamps:
            return infinity
        else:
            return self._timestamps[0][0]

    def step(self):
        """
        Executes the next uncancelled event in the eventqueue.
        """

        # Fetch next process and advance its process execution method.
        noActiveNotice = True
        # Get an uncancelled event
        while noActiveNotice:
            if self._timestamps:
                _tnotice, p, proc, cancelled = heappop(self._timestamps)
                noActiveNotice = cancelled
            else:
                return None

        # Advance simulation time.
        proc._rec = None
        self._t = _tnotice

        # Execute the event. This will advance the process execution method.
        try:
            resultTuple = next(proc._nextpoint)

            # Process the command function which has been yielded by the
            # process.
            if type(resultTuple[0]) == tuple:
                # allowing for reneges, e.g.:
                # >>> yield (request, self, res),(waituntil, self, cond)
                command = resultTuple[0][0]
            else:
                command = resultTuple[0]
            if __debug__:
                if not command in self._commandcodes:
                    raise FatalSimerror('Illegal command: yield %s'%command)
            self._dispatch[command]((resultTuple, proc))
        except StopIteration:
            # Process execution method has terminated.
            self._terminate(proc)

        # Test the conditions for all waiting processes if there are any at
        # all. Where condition are satisfied, reactivate that process
        # immediately and remove it from queue.
        # Always test the wait conditions. They might be triggered by on a
        # terminating process execution method (e.g. the above next() call
        # raises the StopIteration exception)
        if self.condQ:
            i = 0
            while i < len(self.condQ):
                proc = self.condQ[i]
                if proc.cond():
                    self.condQ.pop(i)
                    self.reactivate(proc)
                else:
                    i += 1

        # Return time of the next scheduled event.
        #return self._timestamps[0][0] if self._timestamps else None
        if self._timestamps:
            return self._timestamps[0][0]
        else:
            return None

    def simulate(self, until=0):
        """
        Start the simulation and run its loop until the timeout ``until`` is
        reached, stopSimulation is called, or no more events are scheduled.
        """
        try:
            if not self._timestamps:
                return 'SimPy: No activities scheduled'

            # Some speedups. Storing these values in local variables prevents
            # the self-lookup. Note that this can't be done for _stop because
            # this variable will get overwritten, bools are immutable.
            step = self.step
            timestamps = self._timestamps
            while not self._stop and timestamps and timestamps[0][0] <= until:
                step()

            if not self._stop and timestamps:
                # Timestamps left, simulation not stopped
                self._t = until
                return 'SimPy: Normal exit at time %s' % self._t
            elif not timestamps:
                # No more timestamps
                return 'SimPy: No more events at time %s' % self._t
            else:
                # Stopped by call of stopSimulation
                return 'SimPy: Run stopped at time %s' % self._t
        # Delete the excepts?
        except FatalSimerror as error:
            raise FatalSimerror('SimPy: ' + error.value)
        except Simerror as error:
            return 'SimPy: ' + error.value
        finally:
            self._stop = True

# For backward compatibility
Globals.sim = Simulation()

peek = Globals.sim.peek

step = Globals.sim.step

allMonitors = Globals.sim.allMonitors

allTallies = Globals.sim.allTallies
# End backward compatibility
