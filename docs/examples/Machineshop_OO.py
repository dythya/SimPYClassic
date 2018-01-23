from SimPy.Simulation import *
import random
""" Machineshop_OO.py
Machineshop Model

An example showing interrupts and priority queuing.

Scenario:

A workshop has n identical machines. A stream of jobs (enough to keep
the machines busy) arrives. Each machine breaks down
periodically. Repairs are carried out by one repairman. The repairman
has other, less important tasks to perform, too. Once he starts one of
those, he completes it before starting with the machine repair. The
workshop works continously.  """

# Model components ------------------------


class Machine(Process):
    def __init__(self, name, sim):
        Process.__init__(self, name=name, sim=sim)
        myBreaker = Breakdown(self, sim=sim)
        sim.activate(myBreaker, myBreaker.breakmachine())
        self.partsMade = 0

    def working(self):
        while True:
            yield hold, self, timePerPart()
            if self.interrupted():
                # broken down
                parttimeleft = self.interruptLeft
                yield request, self, self.sim.repairman, 1
                yield hold, self, repairtime
                # repaired
                yield release, self, self.sim.repairman
                yield hold, self, parttimeleft
                # part completed
                self.partsMade += 1
            else:
                # part made
                self.partsMade += 1


class Breakdown(Process):
    def __init__(self, myMachine, sim):
        Process.__init__(self, sim=sim)
        self.myMachine = myMachine

    def breakmachine(self):
        while True:
            yield hold, self, timeToFailure()
            self.interrupt(self.myMachine)


class OtherJobs(Process):

    def doingJobs(self):
        while True:
            yield request, self, self.sim.repairman, 0
            # starts working on jobs
            yield hold, self, jobDuration
            yield release, self, self.sim.repairman


def timePerPart():
    return random.normalvariate(processingTimeMean, processingTimeSigma)


def timeToFailure():
    return random.expovariate(mean)

# Experiment data -------------------------


repairtime = 30.0           # minutes
processingTimeMean = 10.0   # minutes
processingTimeSigma = 2.0
timeToFailureMean = 300.0  # minutes
mean = 1 / timeToFailureMean  # per minute
jobDuration = 30            # minutes
nrMachines = 10
random.seed(111333555)
weeks = 4  # weeks
simTime = weeks * 24 * 60 * 7  # minutes

# Model


class MachineshopModel(Simulation):
    def run(self):
        print('Machineshop')
        self.initialize()
        self.repairman = Resource(capacity=1, qType=PriorityQ, sim=self)
        self.m = {}
        for i in range(nrMachines):
            self.m[i + 1] = Machine(name="Machine {0}".format(i + 1), sim=self)
            self.activate(self.m[i + 1], self.m[i + 1].working())
        oj = OtherJobs(sim=self)
        self.activate(oj, oj.doingJobs())
        self.simulate(until=simTime)  # minutes


# Experiment ------------------------------
model = MachineshopModel()
model.run()

# Analysis/output -------------------------

print("Machineshop results after {0} weeks".format(weeks))
for i in range(nrMachines):
    print("Machine {0}: {1}".format(i + 1, model.m[i + 1].partsMade))
