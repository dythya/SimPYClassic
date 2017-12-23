# coding=utf-8
"""
This file contains Simerror, FatalSimerror, Process, SimEvent, the resources
Resource, Level and Storage as well as their dependencies Buffer, Queue, FIFO
and PriorityQ.

"""
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.builtins import basestring
import inspect
import sys
import types

from SimPy.Lister import Lister
from SimPy.Recording import Monitor, Tally

# Required for backward compatiblity
import SimPy.Globals as Globals


class Simerror(Exception):
    """ SimPy error which terminates "simulate" with an error message"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class FatalSimerror(Simerror):
    """ SimPy error which terminates script execution with an exception"""
    def __init__(self, value):
        Simerror.__init__(self, value)
        self.value = value

class Process(Lister):
    """Superclass of classes which may use generator functions"""
    def __init__(self, name = 'a_process', sim = None):
        if sim is None: sim = Globals.sim # Use global simulation object if sim is None
        self.sim = sim
        #the reference to this Process instances single process (==generator)
        self._nextpoint = None
        if isinstance(name, str) or (sys.version_info.major == 2 and
                isinstance(name, basestring)):
            self.name = name
        else:
            raise FatalSimerror("Process name parameter '%s' is not a string"%name)
        self._nextTime = None #next activation time
        self._remainService = 0
        self._preempted = 0
        self._priority={}
        self._getpriority={}
        self._putpriority={}
        self._terminated = False
        self._inInterrupt = False
        self.eventsFired = [] #which events process waited / queued for occurred
        if hasattr(sim, 'trace'):
            self._doTracing = True
        else:
            self._doTracing = False

    def active(self):
        return self._nextTime != None and not self._inInterrupt

    def passive(self):
        return self._nextTime is None and not self._terminated

    def terminated(self):
        return self._terminated

    def interrupted(self):
        return self._inInterrupt and not self._terminated

    def queuing(self, resource):
        return self in resource.waitQ

    def cancel(self, victim):
        """Application function to cancel all event notices for this Process
        instance;(should be all event notices for the _generator_)."""
        self.sim._unpost(whom = victim)

    def start(self, pem = None, at = 'undefined', delay = 'undefined', prior = False):
        """Activates PEM of this Process.
        p.start(p.pemname([args])[,{at = t | delay = period}][, prior = False]) or
        p.start([p.ACTIONS()][,{at = t | delay = period}][, prior = False]) (ACTIONS
                parameter optional)
        """
        if pem is None:
            try:
                pem = self.ACTIONS()
            except AttributeError:
                raise FatalSimerror\
                       ('no generator function to activate')
        else:
            pass
        if not (type(pem) == types.GeneratorType):
            raise FatalSimerror('activating function which'+
                           ' is not a generator (contains no \'yield\')')
        if not self._terminated and not self._nextTime:
            #store generator reference in object; needed for reactivation
            self._nextpoint = pem
            if at == 'undefined':
                at = self.sim._t
            if delay == 'undefined':
                zeit = max(self.sim._t, at)
            else:
                zeit = max(self.sim._t, self.sim._t + delay)
            if self._doTracing:
                self.sim.trace.recordActivate(who = self, when = zeit,
                                               prior = prior)
            self.sim._post(what = self, at = zeit, prior = prior)

    def _hold(self, a):
        if len(a[0]) == 3: ## yield hold,self,delay
            delay = a[0][2]
            if delay < 0:
                raise FatalSimerror('hold: delay time negative: %s, in %s' % (
                                     delay, str(a[0][1])))
        else:              ## yield hold,self
            delay = 0
        who = a[1]
        self.interruptLeft = delay
        self._inInterrupt = False
        self.interruptCause = None
        self.sim._post(what = who, at = self.sim._t + delay)

    def _passivate(self, a):
        a[0][1]._nextTime = None

    def interrupt(self, victim):
        """Application function to interrupt active processes"""
        # can't interrupt terminated / passive / interrupted process
        if victim.active():
            if self._doTracing:
                save = self.sim.trace._comment
                self.sim.trace._comment = None
            victim.interruptCause = self  # self causes interrupt
            left = victim._nextTime - self.sim._t
            victim.interruptLeft = left   # time left in current 'hold'
            victim._inInterrupt = True
            self.sim.reactivate(victim)
            if self._doTracing:
                self.sim.trace._comment = save
                self.sim.trace.recordInterrupt(self, victim)
            return left
        else: #victim not active -- can't interrupt
            return None

    def interruptReset(self):
        """
        Application function for an interrupt victim to get out of
        'interrupted' state.
        """
        self._inInterrupt = False

    def acquired(self, res):
        """Multi - functional test for reneging for 'request' and 'get':
        (1)If res of type Resource:
            Tests whether resource res was acquired when proces reactivated.
            If yes, the parallel wakeup process is killed.
            If not, process is removed from res.waitQ (reneging).
        (2)If res of type Store:
            Tests whether item(s) gotten from Store res.
            If yes, the parallel wakeup process is killed.
            If no, process is removed from res.getQ
        (3)If res of type Level:
            Tests whether units gotten from Level res.
            If yes, the parallel wakeup process is killed.
            If no, process is removed from res.getQ.
        """
        if isinstance(res, Resource):
            test = self in res.activeQ
            if test:
                self.cancel(self._holder)
            else:
                res.waitQ.remove(self)
                if res.monitored:
                    res.waitMon.observe(len(res.waitQ),t = self.sim.now())
            return test
        elif isinstance(res, Store):
            test = len(self.got)
            if test:
                self.cancel(self._holder)
            else:
                res.getQ.remove(self)
                if res.monitored:
                    res.getQMon.observe(len(res.getQ),t = self.sim.now())
            return test
        elif isinstance(res, Level):
            test = not (self.got is None)
            if test:
                self.cancel(self._holder)
            else:
                res.getQ.remove(self)
                if res.monitored:
                    res.getQMon.observe(len(res.getQ),t = self.sim.now())
            return test

    def stored(self, buffer):
        """Test for reneging for 'yield put . . .' compound statement (Level and
        Store. Returns True if not reneged.
        If self not in buffer.putQ, kill wakeup process, else take self out of
        buffer.putQ (reneged)"""
        test = self in buffer.putQ
        if test:    #reneged
            buffer.putQ.remove(self)
            if buffer.monitored:
                buffer.putQMon.observe(len(buffer.putQ),t = self.sim.now())
        else:
            self.cancel(self._holder)
        return not test


class SimEvent(Lister):
    """Supports one - shot signalling between processes. All processes waiting for an event to occur
    get activated when its occurrence is signalled. From the processes queuing for an event, only
    the first gets activated.
    """
    def __init__(self, name = 'a_SimEvent', sim = None):
        if sim is None: sim = Globals.sim # Use global simulation if sim is None
        self.sim = sim
        self.name = name
        self.waits = []
        self.queues = []
        self.occurred = False
        self.signalparam = None
        if hasattr(sim, 'trace'):
            self._doTracing = True
        else:
            self._doTracing = False

    def signal(self, param = None):
        """Produces a signal to self;
        Fires this event (makes it occur).
        Reactivates ALL processes waiting for this event. (Cleanup waits lists
        of other events if wait was for an event - group (OR).)
        Reactivates the first process for which event(s) it is queuing for
        have fired. (Cleanup queues of other events if wait was for an event - group (OR).)
        """
        self.signalparam = param
        if self._doTracing:
            self.sim.trace.recordSignal(self)
        if not self.waits and not self.queues:
            self.occurred = True
        else:
            #reactivate all waiting processes
            for p in self.waits:
                p[0].eventsFired.append(self)
                self.sim.reactivate(p[0], prior = True)
                #delete waits entries for this process in other events
                for ev in p[1]:
                    if ev != self:
                        if ev.occurred:
                            p[0].eventsFired.append(ev)
                        for iev in ev.waits:
                            if iev[0] == p[0]:
                                ev.waits.remove(iev)
                                break
            self.waits = []
            if self.queues:
                proc = self.queues.pop(0)[0]
                proc.eventsFired.append(self)
                self.sim.reactivate(proc)

    def _wait(self, par):
        """Consumes a signal if it has occurred, otherwise process 'proc'
        waits for this event.
        """
        proc = par[0][1] #the process issuing the yield waitevent command
        # test that process and SimEvent belong to same Simulation instance
        if __debug__:
            if not (proc.sim == self.sim):
                raise FatalSimerror("waitevent: Process %s, SimEvent %s not in "
                        "same Simulation instance" % (proc.name,self.name))
        proc.eventsFired = []
        if not self.occurred:
            self.waits.append([proc, [self]])
            proc._nextTime = None #passivate calling process
        else:
            proc.eventsFired.append(self)
            self.occurred = False
            self.sim._post(proc, at = self.sim._t, prior = 1)

    def _waitOR(self, par):
        """Handles waiting for an OR of events in a tuple / list.
        """
        proc = par[0][1]
        evlist = par[0][2]
        proc.eventsFired = []
        anyoccur = False
        for ev in evlist:
            # test that process and SimEvent belong to same Simulation instance
            if __debug__:
                if not (proc.sim == ev.sim):
                    raise FatalSimerror(
                                        "waitevent: Process %s, SimEvent %s not in "\
                                        "same Simulation instance"%(proc.name,ev.name))
            if ev.occurred:
                anyoccur = True
                proc.eventsFired.append(ev)
                ev.occurred = False
        if anyoccur: #at least one event has fired; continue process
            self.sim._post(proc, at = self.sim._t, prior = 1)

        else: #no event in list has fired, enter process in all 'waits' lists
            proc.eventsFired = []
            proc._nextTime = None #passivate calling process
            for ev in evlist:
                ev.waits.append([proc, evlist])

    def _queue(self, par):
        """Consumes a signal if it has occurred, otherwise process 'proc'
        queues for this event.
        """
        proc = par[0][1] #the process issuing the yield queueevent command
        proc.eventsFired = []
        # test that process and SimEvent belong to same Simulation instance
        if __debug__:
            if not (proc.sim == self.sim):
                raise FatalSimerror("queueevent: Process %s, SimEvent %s not in "
                        "same Simulation instance"%(proc.name,self.name))
        if not self.occurred:
            self.queues.append([proc, [self]])
            proc._nextTime = None #passivate calling process
        else:
            proc.eventsFired.append(self)
            self.occurred = False
            self.sim._post(proc, at = self.sim._t, prior = 1)

    def _queueOR(self, par):
        """Handles queueing for an OR of events in a tuple / list.
        """
        proc = par[0][1]
        evlist = par[0][2]
        proc.eventsFired = []
        anyoccur = False
        for ev in evlist:
        # test that process and SimEvent belong to same Simulation instance
            if __debug__:
                if not (proc.sim == ev.sim):
                    raise FatalSimerror("yield queueevent: Process %s, SimEvent %s not in "
                            "same Simulation instance"%(proc.name,ev.name))
            if ev.occurred:
                anyoccur = True
                proc.eventsFired.append(ev)
                ev.occurred = False
        if anyoccur: #at least one event has fired; continue process
            self.sim._post(proc, at = self.sim._t, prior = 1)

        else: #no event in list has fired, enter process in all 'waits' lists
            proc.eventsFired = []
            proc._nextTime = None #passivate calling process
            for ev in evlist:
                ev.queues.append([proc, evlist])


class Queue(list):
    def __init__(self, res, moni):
        if not moni is None: #moni == []:
            self.monit = True # True if a type of Monitor / Tally attached
        else:
            self.monit = False
        self.moni = moni # The Monitor / Tally
        self.resource = res # the resource / buffer this queue belongs to

    def enter(self, obj):
        pass

    def leave(self):
        pass

    def takeout(self, obj):
        self.remove(obj)
        if self.monit:
            self.moni.observe(len(self), t = self.moni.sim.now())

class FIFO(Queue):
    def __init__(self, res, moni):
        Queue.__init__(self, res, moni)

    def enter(self, obj):
        self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())

    def enterGet(self, obj):
        self.enter(obj)

    def enterPut(self, obj):
        self.enter(obj)

    def leave(self):
        a = self.pop(0)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
        return a

class PriorityQ(FIFO):
    """Queue is always ordered according to priority.
    Higher value of priority attribute == higher priority.
    """
    def __init__(self, res, moni):
        FIFO.__init__(self, res, moni)

    def enter(self, obj):
        """Handles request queue for Resource"""
        if len(self):
            ix = self.resource
            if self[-1]._priority[ix] >= obj._priority[ix]:
                self.append(obj)
            else:
                z = 0
                while self[z]._priority[ix] >= obj._priority[ix]:
                    z += 1
                self.insert(z, obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())

    def enterGet(self, obj):
        """Handles getQ in Buffer"""
        if len(self):
            ix = self.resource
            if self[-1]._getpriority[ix] >= obj._getpriority[ix]:
                self.append(obj)
            else:
                z = 0
                while self[z]._getpriority[ix] >= obj._getpriority[ix]:
                    z += 1
                self.insert(z, obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())

    def enterPut(self, obj):
        """Handles putQ in Buffer"""
        if len(self):
            ix = self.resource
            if self[-1]._putpriority[ix] >= obj._putpriority[ix]:
                self.append(obj)
            else:
                z = 0
                while self[z]._putpriority[ix] >= obj._putpriority[ix]:
                    z += 1
                self.insert(z, obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())

class Resource(Lister):
    """Models shared, limited capacity resources with queuing;
    FIFO is default queuing discipline.
    """

    def __init__(self, capacity = 1, name = 'a_resource', unitName = 'units',
                 qType = FIFO, preemptable = 0, monitored = False,
                 monitorType = Monitor,sim = None):
        """
        monitorType={Monitor(default) | Tally}
        """
        if capacity < 0:
            raise ValueError('capacity should be >= 0, but is: %s' % capacity)

        if sim is None: sim = Globals.sim # Use global simulation if sim is Non
        self.sim = sim
        self.name = name          # resource name
        self.capacity = capacity  # resource units in this resource
        self.unitName = unitName  # type name of resource units
        self.n = capacity         # uncommitted resource units
        self.monitored = monitored

        if self.monitored:           # Monitor waitQ, activeQ
            self.actMon = monitorType(name = 'Active Queue Monitor %s'%self.name,
                                 ylab = 'nr in queue', tlab = 'time',
                                 sim = self.sim)
            monact = self.actMon
            self.waitMon = monitorType(name = 'Wait Queue Monitor %s'%self.name,
                                 ylab = 'nr in queue', tlab = 'time',
                                 sim = self.sim)
            monwait = self.waitMon
        else:
            monwait = None
            monact = None
        self.waitQ = qType(self, monwait)
        self.preemptable = preemptable
        self.activeQ = qType(self, monact)
        self.priority_default = 0
        # Initialize monitors
        if self.monitored:
            monact.observe(t = self.sim.now(), y = len(self.activeQ))
            monwait.observe(t = self.sim.now(), y = len(self.waitQ))

    def _request(self, arg):
        """Process request event for this resource"""
        obj = arg[1]
        # test that process and Resource belong to same Simulation instance
        if __debug__:
            if not (obj.sim == self.sim):
                raise FatalSimerror("yield request: Process %s, Resource %s not in "\
                        "same Simulation instance"%(obj.name,self.name))
        if len(arg[0]) == 4:        # yield request, self, resource, priority
            obj._priority[self] = arg[0][3]
        else:                       # yield request, self, resource
            obj._priority[self] = self.priority_default
        if self.preemptable and self.n == 0: # No free resource
            # test for preemption condition
            preempt = obj._priority[self] > self.activeQ[-1]._priority[self]
            # If yes:
            if preempt:
                z = self.activeQ[-1]
                # Keep track of preempt level
                z._preempted += 1
                # suspend lowest priority process being served
                # record remaining service time at first preempt only
                if z._preempted == 1:
                    z._remainService = z._nextTime - self.sim._t
                    # cancel only at first preempt
                    Process(sim=self.sim).cancel(z)
                # remove from activeQ
                self.activeQ.remove(z)
                # put into front of waitQ
                self.waitQ.insert(0, z)
                # if self is monitored, update waitQ monitor
                if self.monitored:
                    self.waitMon.observe(len(self.waitQ), self.sim.now())
                # passivate re - queued process
                z._nextTime = None
                # assign resource unit to preemptor
                self.activeQ.enter(obj)
                # post event notice for preempting process
                self.sim._post(obj, at = self.sim._t, prior = 1)
            else:
                self.waitQ.enter(obj)
                # passivate queuing process
                obj._nextTime = None
        else: # treat non - preemption case
            if self.n == 0:
                self.waitQ.enter(obj)
                # passivate queuing process
                obj._nextTime = None
            else:
                self.n -= 1
                self.activeQ.enter(obj)
                self.sim._post(obj, at = self.sim._t, prior = 1)

    def _release(self, arg):
        """Process release request for this resource"""
        actor = arg[1]
        self.n += 1
        self.activeQ.remove(arg[1])
        if self.monitored:
            self.actMon.observe(len(self.activeQ),t = self.sim.now())
        #reactivate first waiting requestor if any; assign Resource to it
        if self.waitQ:
            obj = self.waitQ.leave()
            self.n -= 1             #assign 1 resource unit to object
            self.activeQ.enter(obj)
            # if resource preemptable:
            if self.preemptable:
                # if object had been preempted:
                if obj._preempted:
                    # keep track of preempt level
                    obj._preempted -= 1
                    # reactivate object delay = remaining service time
                    # but only, if all other preempts are over
                    if obj._preempted == 0:
                        self.sim.reactivate(obj, delay = obj._remainService,
                                            prior = 1)
                # else reactivate right away
                else:
                    self.sim.reactivate(obj, delay = 0, prior = 1)
            # else:
            else:
                self.sim.reactivate(obj, delay = 0, prior = 1)
        self.sim._post(arg[1], at = self.sim._t, prior = 1)

class Buffer(Lister):
    """Abstract class for buffers
    Blocks a process when a put would cause buffer overflow or a get would cause
    buffer underflow.
    Default queuing discipline for blocked processes is FIFO."""

    priorityDefault = 0
    def __init__(self, name = None, capacity = 'unbounded', unitName = 'units',
                putQType = FIFO, getQType = FIFO,
                monitored = False, monitorType = Monitor, initialBuffered = None,
                sim = None):
        if sim is None: sim = Globals.sim # Use global simulation if sim is None
        self.sim = sim
        if capacity == 'unbounded':
            capacity = sys.maxsize
        elif capacity < 0:
            raise ValueError('capacity should be >= 0, but is: %s' % capacity)
        self.capacity = capacity
        self.name = name
        self.putQType = putQType
        self.getQType = getQType
        self.monitored = monitored
        self.initialBuffered = initialBuffered
        self.unitName = unitName
        if self.monitored:
            ## monitor for Producer processes' queue
            self.putQMon = monitorType(name = 'Producer Queue Monitor %s'%self.name,
                                    ylab = 'nr in queue', tlab = 'time',
                                    sim=self.sim)
            ## monitor for Consumer processes' queue
            self.getQMon = monitorType(name = 'Consumer Queue Monitor %s'%self.name,
                                    ylab = 'nr in queue', tlab = 'time',
                                    sim=self.sim)
            ## monitor for nr items in buffer
            self.bufferMon = monitorType(name = 'Buffer Monitor %s'%self.name,
                                    ylab = 'nr in buffer', tlab = 'time',
                                    sim=self.sim)
        else:
            self.putQMon = None
            self.getQMon = None
            self.bufferMon = None
        self.putQ = self.putQType(res = self, moni = self.putQMon)
        self.getQ = self.getQType(res = self, moni = self.getQMon)
        if self.monitored:
            self.putQMon.observe(y = len(self.putQ),t = self.sim.now())
            self.getQMon.observe(y = len(self.getQ),t = self.sim.now())
        self._putpriority={}
        self._getpriority={}

        def _put(self):
            pass
        def _get(self):
            pass

class Level(Buffer):
    """Models buffers for processes putting / getting un - distinguishable items.
    """
    def getamount(self):
        return self.nrBuffered

    def gettheBuffer(self):
        return self.nrBuffered

    theBuffer = property(gettheBuffer)

    def __init__(self,**pars):
        Buffer.__init__(self,**pars)
        if self.name is None:
            self.name = 'a_level'   ## default name

        if (type(self.capacity) != type(1.0) and\
                type(self.capacity) != type(1)) or\
                self.capacity < 0:
                raise FatalSimerror('Level: capacity parameter not a positive number: %s'\
                    %self.initialBuffered)

        if type(self.initialBuffered) == type(1.0) or\
                type(self.initialBuffered) == type(1):
            if self.initialBuffered > self.capacity:
                raise FatalSimerror('initialBuffered exceeds capacity')
            if self.initialBuffered >= 0:
                self.nrBuffered = self.initialBuffered ## nr items initially in buffer
                                        ## buffer is just a counter (int type)
            else:
                raise FatalSimerror('initialBuffered param of Level negative: %s'\
                %self.initialBuffered)
        elif self.initialBuffered is None:
            self.initialBuffered = 0
            self.nrBuffered = 0
        else:
            raise FatalSimerror('Level: wrong type of initialBuffered (parameter=%s)'\
                %self.initialBuffered)
        if self.monitored:
            self.bufferMon.observe(y = self.amount, t = self.sim.now())
    amount = property(getamount)

    def _put(self, arg):
        """Handles put requests for Level instances"""
        obj = arg[1]
        whichSim=self.sim
        # test that process and Level belong to same Simulation instance
        if __debug__:
            if not (obj.sim == self.sim):
                raise FatalSimerror(
                        "put: Process %s, Level %s not in "\
                        "same Simulation instance"%(obj.name,self.name))
        if len(arg[0]) == 5:        # yield put, self, buff, whattoput, priority
            obj._putpriority[self] = arg[0][4]
            whatToPut = arg[0][3]
        elif len(arg[0]) == 4:      # yield get, self, buff, whattoput
            obj._putpriority[self] = Buffer.priorityDefault #default
            whatToPut = arg[0][3]
        else:                       # yield get, self, buff
            obj._putpriority[self] = Buffer.priorityDefault #default
            whatToPut = 1
        if type(whatToPut) != type(1) and type(whatToPut) != type(1.0):
            raise FatalSimerror('Level: put parameter not a number')
        if not whatToPut >= 0.0:
            raise FatalSimerror('Level: put parameter not positive number')
        whatToPutNr = whatToPut
        if whatToPutNr + self.amount > self.capacity:
            obj._nextTime = None      #passivate put requestor
            obj._whatToPut = whatToPutNr
            self.putQ.enterPut(obj)    #and queue, with size of put
        else:
            self.nrBuffered += whatToPutNr
            if self.monitored:
                self.bufferMon.observe(y = self.amount, t = self.sim.now())
            # service any getters waiting
            # service in queue - order; do not serve second in queue before first
            # has been served
            while len(self.getQ) and self.amount > 0:
                proc = self.getQ[0]
                if proc._nrToGet <= self.amount:
                    proc.got = proc._nrToGet
                    self.nrBuffered -= proc.got
                    if self.monitored:
                        self.bufferMon.observe(y = self.amount, t = self.sim.now())
                    self.getQ.takeout(proc) # get requestor's record out of queue
                    whichSim._post(proc, at = whichSim._t) # continue a blocked get requestor
                else:
                    break
            whichSim._post(obj, at = whichSim._t, prior = 1) # continue the put requestor

    def _get(self, arg):
        """Handles get requests for Level instances"""
        obj = arg[1]
        # test that process and Store belong to same Simulation instance
        if __debug__:
            if not (obj.sim == self.sim):
                raise FatalSimerror(
                        "get: Process %s, Level %s not in "\
                        "same Simulation instance"%(obj.name,self.name))
        obj.got = None
        if len(arg[0]) == 5:        # yield get, self, buff, whattoget, priority
            obj._getpriority[self] = arg[0][4]
            nrToGet = arg[0][3]
        elif len(arg[0]) == 4:      # yield get, self, buff, whattoget
            obj._getpriority[self] = Buffer.priorityDefault #default
            nrToGet = arg[0][3]
        else:                       # yield get, self, buff
            obj._getpriority[self] = Buffer.priorityDefault
            nrToGet = 1
        if type(nrToGet) != type(1.0) and type(nrToGet) != type(1):
            raise FatalSimerror('Level: get parameter not a number: %s'%nrToGet)
        if nrToGet < 0:
            raise FatalSimerror('Level: get parameter not positive number: %s'%nrToGet)
        if self.amount < nrToGet:
            obj._nrToGet = nrToGet
            self.getQ.enterGet(obj)
            # passivate queuing process
            obj._nextTime = None
        else:
            obj.got = nrToGet
            self.nrBuffered -= nrToGet
            if self.monitored:
                self.bufferMon.observe(y = self.amount, t = self.sim.now())
            self.sim._post(obj, at = self.sim._t, prior = 1)
            # reactivate any put requestors for which space is now available
            # service in queue - order; do not serve second in queue before first
            # has been served
            while len(self.putQ): #test for queued producers
                proc = self.putQ[0]
                if proc._whatToPut + self.amount <= self.capacity:
                    self.nrBuffered += proc._whatToPut
                    if self.monitored:
                        self.bufferMon.observe(y = self.amount, t = self.sim.now())
                    self.putQ.takeout(proc)#requestor's record out of queue
                    self.sim._post(proc, at = self.sim._t) # continue a blocked put requestor
                else:
                    break

class Store(Buffer):
    """Models buffers for processes coupled by putting / getting distinguishable
    items.
    Blocks a process when a put would cause buffer overflow or a get would cause
    buffer underflow.
    Default queuing discipline for blocked processes is priority FIFO.
    """
    def getnrBuffered(self):
        return len(self.theBuffer)
    nrBuffered = property(getnrBuffered)

    def getbuffered(self):
        return self.theBuffer
    buffered = property(getbuffered)

    def __init__(self,**pars):
        Buffer.__init__(self,**pars)
        self.theBuffer = []
        if self.name is None:
            self.name = 'a_store' ## default name
        if type(self.capacity) != type(1) or self.capacity <= 0:
            raise FatalSimerror\
                ('Store: capacity parameter not a positive integer: %s'\
                    %self.capacity)
        if type(self.initialBuffered) == type([]):
            if len(self.initialBuffered) > self.capacity:
                raise FatalSimerror\
                   ('Store: number initialBuffered exceeds capacity')
            else:
                ## buffer receives list of objects
                self.theBuffer[:] = self.initialBuffered
        elif self.initialBuffered is None:
            self.theBuffer = []
        else:
            raise FatalSimerror\
                ('Store: initialBuffered not a list')
        if self.monitored:
            self.bufferMon.observe(y = self.nrBuffered, t = self.sim.now())
        self._sort = None



    def addSort(self, sortFunc):
        """Adds buffer sorting to this instance of Store. It maintains
        theBuffer sorted by the sortAttr attribute of the objects in the
        buffer.
        The user - provided 'sortFunc' must look like this:

        def mySort(self, par):
            tmplist = [(x.sortAttr, x) for x in par]
            tmplist.sort()
            return [x for (key, x) in tmplist]

        """

        self._sort = sortFunc.__get__(self, self.__class__)
        self.theBuffer = self._sort(self.theBuffer)

    def _put(self, arg):
        """Handles put requests for Store instances"""
        obj = arg[1]
        # test that process and Store belong to same Simulation instance
        if __debug__:
            if not (obj.sim == self.sim):
                raise FatalSimerror(
                                "put: Process %s, Store %s not in "\
                                "same Simulation instance"%(obj.name,self.name))
        whichSim=self.sim
        if len(arg[0]) == 5:        # yield put, self, buff, whattoput, priority
            obj._putpriority[self] = arg[0][4]
            whatToPut = arg[0][3]
        elif len(arg[0]) == 4:      # yield put, self, buff, whattoput
            obj._putpriority[self] = Buffer.priorityDefault #default
            whatToPut = arg[0][3]
        else:                       # error, whattoput missing
            raise FatalSimerror('Item to put missing in yield put stmt')
        if type(whatToPut) != type([]):
            raise FatalSimerror('put parameter is not a list')
        whatToPutNr = len(whatToPut)
        if whatToPutNr + self.nrBuffered > self.capacity:
            obj._nextTime = None      #passivate put requestor
            obj._whatToPut = whatToPut
            self.putQ.enterPut(obj) #and queue, with items to put
        else:
            self.theBuffer.extend(whatToPut)
            if not(self._sort is None):
                self.theBuffer = self._sort(self.theBuffer)
            if self.monitored:
                self.bufferMon.observe(y = self.nrBuffered, t = whichSim.now())

            # service any waiting getters
            # service in queue order: do not serve second in queue before first
            # has been served
            #
            # [jkoomen@xeroxlabs.com / 2011-08-16]
            # Documentation says that
            # "yield get requests with a numerical parameter are honored in priority/FIFO order"
            # but
            # "yield get requests with a filter function parameter are not necessarily honored in priority/FIFO order, but rather according to the filter function."
#            while self.nrBuffered > 0 and len(self.getQ):
            idx = 0
            while self.nrBuffered > 0 and idx < len(self.getQ):
                proc = self.getQ[idx]
                if inspect.isfunction(proc._nrToGet):
                    movCand = proc._nrToGet(self.theBuffer) #predicate parameter
                    if movCand:
                        proc.got = movCand[:]
                        for i in movCand:
                            self.theBuffer.remove(i)
                        self.getQ.takeout(proc)
                        if self.monitored:
                            self.bufferMon.observe(
                                    y = self.nrBuffered, t = whichSim._t)
                        whichSim._post(what = proc, at = whichSim._t) # continue a blocked get requestor
                    else:
#                        break
                        idx += 1
                else: #numerical parameter
                    if proc._nrToGet <= self.nrBuffered:
                        nrToGet = proc._nrToGet
                        proc.got = []
                        proc.got[:] = self.theBuffer[0:nrToGet]
                        self.theBuffer[:] = self.theBuffer[nrToGet:]
                        if self.monitored:
                            self.bufferMon.observe(
                                       y = self.nrBuffered, t = whichSim._t)
                        # take this get requestor's record out of queue:
                        self.getQ.takeout(proc)
                        whichSim._post(what = proc, at = whichSim._t) # continue a blocked get requestor
                    else:
                        break

            whichSim._post(what = obj, at = whichSim._t, prior = 1) # continue the put requestor

    def _get(self, arg):
        """Handles get requests"""
        filtfunc = None
        obj = arg[1]
        # test that process and Store belong to same Simulation instance
        if __debug__:
            if not (obj.sim == self.sim):
                raise FatalSimerror(
                                "get: Process %s, Store %s not in "\
                                "same Simulation instance"%(obj.name,self.name))
        whichSim=obj.sim
        obj.got = []                  # the list of items retrieved by 'get'
        if len(arg[0]) == 5:        # yield get, self, buff, whattoget, priority
            obj._getpriority[self] = arg[0][4]
            if inspect.isfunction(arg[0][3]):
                filtfunc = arg[0][3]
            else:
                nrToGet = arg[0][3]
        elif len(arg[0]) == 4:      # yield get, self, buff, whattoget
            obj._getpriority[self] = Buffer.priorityDefault #default
            if inspect.isfunction(arg[0][3]):
                filtfunc = arg[0][3]
            else:
                nrToGet = arg[0][3]
        else:                       # yield get, self, buff
            obj._getpriority[self] = Buffer.priorityDefault
            nrToGet = 1
        if not filtfunc: #number specifies nr items to get
            if nrToGet < 0:
                raise FatalSimerror\
                    ('Store: get parameter not positive number: %s'%nrToGet)
            if self.nrBuffered < nrToGet:
                obj._nrToGet = nrToGet
                self.getQ.enterGet(obj)
                # passivate / block queuing 'get' process
                obj._nextTime = None
            else:
                for i in range(nrToGet):
                    obj.got.append(self.theBuffer.pop(0)) # move items from
                                                # buffer to requesting process
                if self.monitored:
                    self.bufferMon.observe(y = self.nrBuffered, t = whichSim.now())
                whichSim._post(obj, at = whichSim._t, prior = 1)
                # reactivate any put requestors for which space is now available
                # serve in queue order: do not serve second in queue before first
                # has been served
                while len(self.putQ):
                    proc = self.putQ[0]
                    if len(proc._whatToPut) + self.nrBuffered <= self.capacity:
                        for i in proc._whatToPut:
                            self.theBuffer.append(i) #move items to buffer
                        if not(self._sort is None):
                            self.theBuffer = self._sort(self.theBuffer)
                        if self.monitored:
                            self.bufferMon.observe(
                                        y = self.nrBuffered, t = whichSim.now())
                        self.putQ.takeout(proc) # dequeue requestor's record
                        whichSim._post(proc, at = whichSim._t) # continue a blocked put requestor
                    else:
                        break
        else: # items to get determined by filtfunc
            movCand = filtfunc(self.theBuffer)
            if movCand: # get succeded
                whichSim._post(obj, at = whichSim._t, prior = 1)
                obj.got = movCand[:]
                for item in movCand:
                    self.theBuffer.remove(item)
                if self.monitored:
                    self.bufferMon.observe(y = self.nrBuffered, t = whichSim.now())
                # reactivate any put requestors for which space is now available
                # serve in queue order: do not serve second in queue before first
                # has been served
                while len(self.putQ):
                    proc = self.putQ[0]
                    if len(proc._whatToPut) + self.nrBuffered <= self.capacity:
                        for i in proc._whatToPut:
                            self.theBuffer.append(i) #move items to buffer
                        if not(self._sort is None):
                            self.theBuffer = self._sort(self.theBuffer)
                        if self.monitored:
                            self.bufferMon.observe(
                                        y = self.nrBuffered, t = whichSim.now())
                        self.putQ.takeout(proc) # dequeue requestor's record
                        whichSim._post(proc, at = whichSim._t) # continue a blocked put requestor
                    else:
                        break
            else: # get did not succeed, block
                obj._nrToGet = filtfunc
                self.getQ.enterGet(obj)
                # passivate / block queuing 'get' process
                obj._nextTime = None
