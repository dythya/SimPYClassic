__doc__ = """ bank11.py: Simulate customers arriving
    at random, using a Source, requesting service
    from two counters each with their own queue
    random servicetime.
    Uses a Monitor object to record waiting times
"""
from SimPy.Simulation import *
# Lmona
from random import Random
from SimPy.SimGUI import *


class Source(Process):
    """ Source generates customers randomly"""

    def __init__(self, seed=333):
        Process.__init__(self)
        self.SEED = seed

    def generate(self, number, interval):
        rv = Random(self.SEED)
        for i in range(number):
            c = Customer(name="Customer{0:02d}".format(i))
            activate(c, c.visit(timeInBank=12.0))
            t = rv.expovariate(1.0 / interval)
            yield hold, self, t


def NoInSystem(R):
    """ The number of customers in the resource R
    in waitQ and active Q"""
    return (len(R.waitQ) + len(R.activeQ))


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def __init__(self, name):
        Process.__init__(self)
        self.name = name

    def visit(self, timeInBank=0):
        arrive = now()
        Qlength = [NoInSystem(counter[i]) for i in range(Nc)]
        if gui.params.trace:
            gui.writeConsole("{0:7.4f} {1}: Here I am. Queues are: {2}".format(
                now(), self.name, Qlength))
        for i in range(Nc):
            if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                join = i
                break
        yield request, self, counter[join]
        wait = now() - arrive
        waitMonitor.observe(wait, t=now())
        if gui.params.trace:
            gui.writeConsole("{0:7.4f} {1}: Waited {2:6.3f}".format(
                now(), self.name, wait))
        tib = counterRV.expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, counter[join]
        if gui.params.trace:
            gui.writeConsole(
                "{0:7.4f} {1}: Finished    ".format(now(), self.name))


def model(counterseed=3939393):
    global Nc, counter, counterRV, waitMonitor
    Nc = 2
    counter = [Resource(name="Clerk0"), Resource(name="Clerk1")]
    counterRV = Random(counterseed)
    gui.mon1 = waitMonitor = Monitor("Customer waiting times")
    waitMonitor.tlab = "arrival time"
    waitMonitor.ylab = "waiting time"
    initialize()
    source = Source(seed=gui.params.sourceseed)
    activate(source, source.generate(
        gui.params.numberCustomers, gui.params.interval), 0.0)
    result = simulate(until=gui.params.endtime)
    gui.writeStatusLine(text="Time at simulation end: {0:.1f}"
                        " -- Customers still waiting: {1}"
                        .format(now(),
                                len(counter[0].waitQ) +
                                len(counter[1].waitQ)))


def statistics():
    if gui.noRunYet:
        showwarning(title='Model warning',
                    message="Run simulation first -- no data available.")
        return
    gui.writeConsole(text="\nRun parameters: {0}".format(gui.params))
    gui.writeConsole(text="Average wait for {0:4d} customers was {1:6.2f}"
                     .format(waitMonitor.count(), waitMonitor.mean()))


def run():
    model(gui.params.counterseed)
    gui.noRunYet = False


def showAuthors():
    gui.showTextBox(text="Tony Vignaux\nKlaus Muller",
                    title="Author information")


class MyGUI(SimGUI):
    def __init__(self, win, **p):
        SimGUI.__init__(self, win, **p)
        self.help.add_command(label="Author(s)",
                              command=showAuthors, underline=0)
        self.view.add_command(label="Statistics",
                              command=statistics, underline=0)
        self.run.add_command(label="Run bank11 model",
                             command=run, underline=0)

        self.params = Parameters(
            endtime=2000,
            sourceseed=1133,
            counterseed=3939393,
            numberCustomers=50,
            interval=10.0,
            trace=0)


root = Tk()
gui = MyGUI(root, title="SimPy GUI example", doc=__doc__, consoleHeight=40)
gui.mainloop()
