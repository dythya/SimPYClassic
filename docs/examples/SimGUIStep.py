from SimPy.SimGUI import *
from SimPy.SimulationStep import *
from random import Random

__version__ = '$Revision$ $Date$ kgm'

if __name__ == '__main__':

    class Source(Process):
        """ Source generates customers randomly"""

        def __init__(self, seed=333):
            Process.__init__(self)
            self.SEED = seed

        def generate(self, number, interval):
            rv = Random(self.SEED)
            for i in range(number):
                c = Customer(name="Customer{0:02d}".format(i,))
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
            # print("{0:7.4f} {1}: Here I am. {2}   ".format(now(),
            #                                                self.name,
            #                                                Qlength))
            for i in range(Nc):
                if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                    join = i
                    break
            yield request, self, counter[join]
            wait = now() - arrive
            waitMonitor.observe(wait, t=now())  # Lmond
            # print("{0:7.4f} {1}: Waited {2:6.3f}".format(now(),
            #                                              self.name,wait))
            tib = counterRV.expovariate(1.0 / timeInBank)
            yield hold, self, tib
            yield release, self, counter[join]
            serviceMonitor.observe(now() - arrive, t=now())
            if trace:
                gui.writeConsole("Customer leaves at {0:.1f}".format(now()))
            # print("{0:7.4f} {1}: Finished    ".format(now(),self.name))

    def showtime():
        gui.topconsole.config(text="time = {0}".format(now()))
        gui.root.update()

    def runStep():
        if gui.noRunYet:
            showwarning("SimPy warning", "Run 'Start run (stepping)' first")
            return
        showtime()
        a = simulateStep(until=gui.params.endtime)
        if a[1] == "notResumable":
            gui.writeConsole(text="Run ended. Status: {0}".format(a[0]))
        showtime()

    def runNoStep():
        showtime()
        for i in range(gui.params.nrRuns):
            simulate(until=gui.param.sendtime)
        showtime()
        gui.writeConsole("{0} simulation run(s) completed\n".format(i + 1))

    def contStep():
        return

    def model():
        global Nc, counter, counterRV, waitMonitor, serviceMonitor, trace
        global lastLeave, noRunYet, initialized
        counterRV = Random(gui.params.counterseed)
        sourceseed = gui.params.sourceseed
        nrRuns = gui.params.nrRuns
        lastLeave = 0
        gui.noRunYet = True
        for runNr in range(nrRuns):
            gui.noRunYet = False
            trace = gui.params.trace
            if trace:
                gui.writeConsole(text='\n** Run {0}'.format(runNr + 1))
            Nc = 2
            counter = [Resource(name="Clerk0"), Resource(name="Clerk1")]
            gui.waitMoni = waitMonitor = Monitor(name='Waiting Times')
            waitMonitor.xlab = 'Time'
            waitMonitor.ylab = 'Customer waiting time'
            gui.serviceMoni = serviceMonitor = Monitor(name='Service Times')
            serviceMonitor.xlab = 'Time'
            serviceMonitor.ylab = 'Total service time = wait+service'
            initialize()
            source = Source(seed=sourceseed)
            activate(source, source.generate(
                gui.params.numberCustomers, gui.params.interval), 0.0)
            simulate(showtime, until=gui.params.endtime)
            showtime()
            lastLeave += now()
        gui.writeConsole("{0} simulation run(s) completed\n".format(nrRuns))
        gui.writeConsole("Parameters:\n{0}".format(gui.params))

    def modelstep():
        global Nc, counter, counterRV, waitMonitor, serviceMonitor, trace
        global lastLeave, noRunYet
        counterRV = Random(gui.params.counterseed)
        sourceseed = gui.params.sourceseed
        nrRuns = gui.params.nrRuns
        lastLeave = 0
        gui.noRunYet = True
        trace = gui.params.trace
        if trace:
            gui.writeConsole(text='\n** Run {0}'.format(runNr + 1))
        Nc = 2
        counter = [Resource(name="Clerk0"), Resource(name="Clerk1")]
        gui.waitMoni = waitMonitor = Monitor(name='Waiting Times')
        waitMonitor.xlab = 'Time'
        waitMonitor.ylab = 'Customer waiting time'
        gui.serviceMoni = serviceMonitor = Monitor(name='Service Times')
        serviceMonitor.xlab = 'Time'
        serviceMonitor.ylab = 'Total service time = wait+service'
        initialize()
        source = Source(seed=sourceseed)
        activate(source, source.generate(
            gui.params.numberCustomers, gui.params.interval), 0.0)
        simulateStep(until=gui.params.endtime)
        gui.noRunYet = False

    def statistics():
        if gui.noRunYet:
            showwarning(title='SimPy warning',
                        message="Run simulation first -- no data available.")
            return
        aver = lastLeave / gui.params.nrRuns
        gui.writeConsole(text="Average time for {0} customers to get through "
                              "bank: {1:.1f}\n({2} runs)\n"
                              .format(gui.params.numberCustomers, aver,
                                      gui.params.nrRuns))

    __doc__ = """
Modified bank11.py (from Bank Tutorial) with GUI.

Model: Simulate customers arriving
at random, using a Source, requesting service
from two counters each with their own queue
random servicetime.

Uses Monitor objects to record waiting times
and total service times."""

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
            self.run.add_command(label="Start run (event stepping)",
                                 command=modelstep, underline=0)
            self.run.add_command(label="Next event",
                                 command=runStep, underline=0)
            self.run.add_command(label="Complete run (no stepping)",
                                 command=model, underline=0)

    root = Tk()
    gui = MyGUI(root, title="SimPy GUI example", doc=__doc__)
    gui.params = Parameters(endtime=2000,
                            sourceseed=1133,
                            counterseed=3939393,
                            numberCustomers=50,
                            interval=10.0,
                            trace=0,
                            nrRuns=1)
    gui.mainloop()
