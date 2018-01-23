""" bank11.py: Simulate customers arriving
    at random, using a Source, requesting service
    from two counters each with their own queue
    random servicetime.
    Uses a Monitor object to record waiting times
"""
from SimPy.Simulation import *
from SimPy.SimPlot import *
from random import Random


class Bank11(SimPlot):
    def __init__(self, **p):
        SimPlot.__init__(self, **p)

    def NoInSystem(self, R):
        """ The number of customers in the resource R
        in waitQ and active Q"""
        return (len(R.waitQ) + len(R.activeQ))

    def model(self):
        self.counterRV = Random(self.params["counterseed"])
        self.sourceseed = self.params["sourceseed"]
        nrRuns = self.params["nrRuns"]
        self.lastLeave = 0
        self.noRunYet = True
        for runNr in range(nrRuns):
            self.noRunYet = False
            self.Nc = 2
            self.counter = [Resource(name="Clerk0", monitored=False),
                            Resource(name="Clerk1", monitored=False)]
            self.waitMonitor = Monitor(name='Waiting Times')
            self.waitMonitor.xlab = 'Time'
            self.waitMonitor.ylab = 'Waiting time'
            self.serviceMonitor = Monitor(name='Service Times')
            self.serviceMonitor.xlab = 'Time'
            self.serviceMonitor.ylab = 'wait+service'
            initialize()
            source = Source(self, seed=self.sourceseed * 1000)
            activate(source, source.generate(self.params["numberCustomers"],
                                             self.params["interval"]), 0.0)
            simulate(until=self.params['endtime'])
            self.lastLeave += now()
        print("{0} run(s) completed".format(nrRuns))
        print("Parameters:\n{0}".format(self.params))


class Source(Process):
    """ Source generates customers randomly"""

    def __init__(self, modInst, seed=333):
        Process.__init__(self)
        self.modInst = modInst
        self.SEED = seed

    def generate(self, number, interval):
        rv = Random(self.SEED)
        for i in range(number):
            c = Customer(self.modInst, name="Customer{0:02d}".format(i))
            activate(c, c.visit(timeInBank=12.0))
            t = rv.expovariate(1.0 / interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """

    def __init__(self, modInst, **p):
        Process.__init__(self, **p)
        self.modInst = modInst

    def visit(self, timeInBank=0):
        arrive = now()
        Qlength = [self.modInst.NoInSystem(self.modInst.counter[i])
                   for i in range(self.modInst.Nc)]
        for i in range(self.modInst.Nc):
            if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                join = i
                break
        yield request, self, self.modInst.counter[join]
        wait = now() - arrive
        self.modInst.waitMonitor.observe(wait, t=now())
        # print("{0:7.4f} {1}: Waited {2:6.3f}".format(now(),self.name,wait))
        tib = self.modInst.counterRV.expovariate(1.0 / timeInBank)
        yield hold, self, tib
        yield release, self, self.modInst.counter[join]
        self.modInst.serviceMonitor.observe(now() - arrive, t=now())


root = Tk()
plt = Bank11()
plt.params = {"endtime": 2000,
              "sourceseed": 1133,
              "counterseed": 3939393,
              "numberCustomers": 50,
              "interval": 10.0,
              "trace": 0,
              "nrRuns": 1}
plt.model()
plt.plotLine(plt.waitMonitor, color='blue', width=2)
plt.plotLine(plt.serviceMonitor, color='red', width=2)
root.mainloop()
