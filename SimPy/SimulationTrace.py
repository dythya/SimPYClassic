# coding=utf-8
"""
SimulationTrace 2.1 Traces execution of SimPy models.
Implements SimPy Processes, Resources, Buffers, and the backbone simulation
scheduling by coroutine calls. Provides data collection through classes
Monitor and Tally.
Based on generators.

"""
from __future__ import print_function

from builtins import str
from SimPy.Lister import *
from SimPy.Simulation import *


def trace_dispatch(trace, command, func):
    """
    Returns a wrapper for ``func`` which will record the dispatch in the trace
    log.
    """
    def dispatch(event):
        func(event)
        trace.recordEvent(command, event)

    return dispatch

class SimulationTrace(Simulation):
    def __init__(self):
        Simulation.__init__(self)
        self.trace = Trace(sim=self)
        # Trace method to be called on _post calls.
        self._post_tracing = None

        # We use our own instance of the command dictionary.
        self._dispatch = dict(Simulation._dispatch)

        # Now wrap all commands in a tracing call.
        for command, func in list(self._dispatch.items()):
            self._dispatch[command] = trace_dispatch(self.trace, command, func)

    def initialize(self):
        Simulation.initialize(self)


    def _post(self, what, at, prior=False):
        if self._post_tracing is not None: self._post_tracing(what, at, prior)
        Simulation._post(self, what, at, prior)

    def activate(
            self, obj, process, at='undefined', delay='undefined', prior=False):
        # Activate _post tracing.
        self._post_tracing = self.trace.recordActivate
        Simulation.activate(self, obj, process, at, delay, prior)
        self._post_tracing = None

    def reactivate(
            self, obj, at='undefined', delay='undefined', prior=False):
        # Activate _post tracing.
        self._post_tracing = self.trace.recordReactivate
        Simulation.reactivate(self, obj, at, delay, prior)
        self._post_tracing = None

    def _terminate(self, process):
        self.trace.tterminated(process)
        Simulation._terminate(self, process)

    def simulate(self, until=0):
        try:
            return Simulation.simulate(self, until)
        finally:
            if not(self.trace.outfile is sys.stdout):
                self.trace.outfile.close()

class Trace(Lister):
    commands={hold:'hold', passivate:'passivate', request:'request', release:'release',
              waitevent:'waitevent', queueevent:'queueevent', waituntil:'waituntil',
            get:'get', put:'put'}

    def __init__(self, start = 0, end = 10000000000, toTrace=\
                 ['hold', 'activate', 'cancel', 'reactivate', 'passivate', 'request',
                  'release', 'interrupt', 'terminated', 'waitevent', 'queueevent',
                  'signal', 'waituntil', 'put', 'get'
                 ],outfile = sys.stdout,sim=None):

        Trace.commandsproc={hold:Trace.thold, passivate:Trace.tpassivate,
                            request:Trace.trequest, release:Trace.trelease,
                            waitevent:Trace.twaitevent,
                            queueevent:Trace.tqueueevent,
                            waituntil:Trace.twaituntil,
                            get:Trace.tget, put:Trace.tput}
        if sim is None: sim=Globals.sim
        self.sim=sim
        self.start = start
        self.end = end
        self.toTrace = toTrace
        self.tracego = True
        self.outfile = outfile
        self._comment = None

    def treset(self):
        Trace.commandsproc={hold:Trace.thold, passivate:Trace.tpassivate,
                            request:Trace.trequest, release:Trace.trelease,
                            waitevent:Trace.twaitevent,
                            queueevent:Trace.tqueueevent,
                            waituntil:Trace.twaituntil,
                            get:Trace.tget, put:Trace.tput}
        self.start = 0
        self.end = 10000000000
        self.toTrace = ['hold', 'activate', 'cancel', 'reactivate', 'passivate', 'request',
                        'release', 'interrupt', 'terminated', 'waitevent', 'queueevent',
                        'signal', 'waituntil', 'put', 'get']
        self.tracego = True
        self.outfile = sys.stdout
        self._comment = None

    def tchange(self,**kmvar):
        for v in kmvar:
            if v == 'start':
                self.start = kmvar[v]
            elif v == 'end':
                self.end = kmvar[v]
            elif v == 'toTrace':
                self.toTrace = kmvar[v]
            elif v == 'outfile':
                self.outfile = kmvar[v]

    def tstart(self):
        self.tracego = True

    def tstop(self):
        self.tracego = False

    def ifTrace(self, cond):
        if self.tracego and (self.start <= self.sim.now() <= self.end)\
           and cond:
            return True

    def thold(self, par):
        try:
            return 'delay: %s' % par[0][2]
        except:
            return 'delay: 0'
    thold = classmethod(thold)

    def trequest(self, par):
        res = par[0][2]
        if len(par[0]) == 4:
            priority = 'priority: ' + str(par[0][3])
        else:
            priority = 'priority: default'
        wQ = [x.name for x in res.waitQ]
        aQ = [x.name for x in res.activeQ]
        return '<%s> %s\n. . .waitQ: %s\n. . .activeQ: %s' % (res.name, priority, wQ, aQ)
    trequest = classmethod(trequest)

    def trelease(self, par):
        res = par[0][2]
        wQ = [x.name for x in res.waitQ]
        aQ = [x.name for x in res.activeQ]
        return '<%s>\n. . .waitQ: %s\n. . .activeQ: %s' % (res.name, wQ, aQ)
    trelease = classmethod(trelease)

    def tpassivate(self, par):
        return ""
    tpassivate = classmethod(tpassivate)

    def tactivate(self, par):
        pass
    tactivate = classmethod(tactivate)

    def twaitevent(self, par):
        evt = par[0][2]
        if type(evt) == list or type(evt) == tuple:
            enames = [x.name for x in evt]
            return 'waits for events <%s> '%enames
        else:
            return 'waits for event <%s> '%evt.name
    twaitevent = classmethod(twaitevent)

    def tqueueevent(self, par):
        evt = par[0][2]
        if type(evt) == list or type(evt) == tuple:
            enames = [x.name for x in evt]
            return 'queues for events <%s> '%enames
        else:
            return 'queues for event <%s> '%evt.name
    tqueueevent = classmethod(tqueueevent)

    def tsignal(self, evt):
        wQ = [x.name for x in evt.waits]
        qQ = [x.name for x in evt.queues]
        return '<%s> \n. . .  occurred: %s\n. . .  waiting: %s\n. . .  queueing: %s'\
                %(evt.name, evt.occurred, wQ, qQ)
        pass
    tsignal = classmethod(tsignal)

    def twaituntil(self, par):
        condition = par[0][2]
        return 'for condition <%s> '%condition.__name__
    twaituntil = classmethod(twaituntil)

    def tget(self, par):
        buff = par[0][2]
        if len(par[0]) == 5:
            priority = 'priority: ' + str(par[0][4])
        else:
            priority = 'priority: default'
        if len(par[0]) == 3:
            nrToGet = 1
        else:
            nrToGet = par[0][3]
        toGet = 'to get: %s %s from' % (nrToGet, buff.unitName)
        getQ = [x.name for x in buff.getQ]
        putQ = [x.name for x in buff.putQ]
        try:
            inBuffer = buff.amount
        except:
            inBuffer = buff.nrBuffered
        return '%s <%s> %s \n. . .getQ: %s \n. . .putQ: %s \n. . .in buffer: %s'\
            %(toGet, buff.name, priority, getQ, putQ, inBuffer)
    tget = classmethod(tget)

    def tput(self, par):
        buff = par[0][2]
        if len(par[0]) == 5:
            priority = 'priority: ' + str(par[0][4])
        else:
            priority = 'priority: default'
        if len(par[0]) == 3:
            nrToPut = 1
        else:
            if type(par[0][3]) == type([]):
                nrToPut = len(par[0][3])
            else:
                nrToPut = par[0][3]
        getQ = [x.name for x in buff.getQ]
        putQ = [x.name for x in buff.putQ]
        toPut = 'to put: %s %s into' % (nrToPut, buff.unitName)
        try:
            inBuffer = buff.amount
        except:
            inBuffer = buff.nrBuffered
        return '%s <%s> %s \n. . .getQ: %s \n. . .putQ: %s \n. . .in buffer: %s'\
            %(toPut, buff.name, priority, getQ, putQ, inBuffer)
    tput = classmethod(tput)

    def recordEvent(self, command, whole):
        if self.ifTrace(Trace.commands[command] in self.toTrace):
            if not type(whole[0][0]) == tuple:
                print(whole[0][1].sim.now(),\
                    Trace.commands[command],\
                    '<' + whole[0][1].name + '>',\
                    Trace.commandsproc[command](whole), file=self.outfile)
                if self._comment:
                    print('----', self._comment, file=self.outfile)
            else:
                print(whole[0][0][1].sim.now(),\
                         Trace.commands[command],\
                         '<' + whole[0][0][1].name + '>'+\
                         Trace.commandsproc[command](whole[0]), file=self.outfile)
                print('|| RENEGE COMMAND:', file=self.outfile)
                command1 = whole[0][1][0]
                print('||\t', Trace.commands[command1],\
                    '<' + whole[0][1][1].name + '>',\
                      Trace.commandsproc[command1]((whole[0][1],)), file=self.outfile)
                if self._comment:
                    print('----', self._comment, file=self.outfile)

        self._comment = None

    def recordInterrupt(self, who, victim):
        if self.ifTrace('interrupt' in self.toTrace):
            print('%s interrupt by: <%s> of: <%s>'\
                                   %(who.sim.now(),who.name, victim.name), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def recordCancel(self, who, victim):
        if self.ifTrace('cancel' in self.toTrace):
            print('%s cancel by: <%s> of: <%s> '\
            %(who.sim.now(),who.name, victim.name), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def recordActivate(self, who, when, prior):
        if self.ifTrace('activate' in self.toTrace):
            print('%s activate <%s> at time: %s prior: %s'\
                     %(who.sim.now(),who.name,when, prior), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def recordReactivate(self, who, when, prior):
        if self.ifTrace('reactivate' in self.toTrace):
            print('%s reactivate <%s> time: %s prior: %s'\
                     %(who.sim.now(),who.name,when, prior), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def recordSignal(self, evt):
        if self.ifTrace('signal' in self.toTrace):
            print('%s event <%s> is signalled' \
                                   %(evt.sim.now(),evt.name), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def tterminated(self, who):
        if self.ifTrace('terminated' in self.toTrace):
            print('%s <%s> terminated'\
                     %(who.sim.now(),who.name), file=self.outfile)
            if self._comment:
                print('----', self._comment, file=self.outfile)
        self._comment = None

    def ttext(self, par):
        self._comment = par

# For backward compatibility
Globals.sim = SimulationTrace()
trace = Globals.sim.trace
step = Globals.sim.step
peek = Globals.sim.peek
allMonitors = Globals.sim.allMonitors
allTallies = Globals.sim.allTallies
# End backward compatibility
