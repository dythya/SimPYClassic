"""MMC_OO.py

An M/M/c queue

Jobs arrive at random into a c-server queue with
exponential service-time distribution. Simulate to
determine the average  number in the system and
the average time jobs spend in the system.

- c = Number of servers = 3
- rate = Arrival rate = 2.0
- stime = mean service time = 1.0

"""
from SimPy.Simulation import *
from random import expovariate, seed

# Model components ------------------------


class Generator(Process):
    """ generates Jobs at random """

    def execute(self, maxNumber, rate, stime):
        ''' generate Jobs at exponential intervals '''
        for i in range(maxNumber):
            L = Job("Job {0}".format(i), sim=self.sim)
            self.sim.activate(L, L.execute(stime), delay=0)
            yield hold, self, expovariate(rate)


class Job(Process):
    ''' Jobs request a gatekeeper and hold
        it for an exponential time '''

    NoInSystem = 0

    def execute(self, stime):
        arrTime = self.sim.now()
        self.trace("Hello World")
        Job.NoInSystem += 1
        self.sim.m.observe(Job.NoInSystem)
        yield request, self, self.sim.server
        self.trace("At last    ")
        t = expovariate(1.0 / stime)
        self.sim.msT.observe(t)
        yield hold, self, t
        yield release, self, self.sim.server
        Job.NoInSystem -= 1
        self.sim.m.observe(Job.NoInSystem)
        self.sim.mT.observe(self.sim.now() - arrTime)
        self.trace("Geronimo   ")

    def trace(self, message):
        FMT = "{0:7.4f} {1:6} {2:10} {(3:2d)}"
        if TRACING:
            print(FMT.format(self.sim.now(), self.name,
                             message, Job.NoInSystem))

# Experiment data -------------------------


TRACING = False
c = 3  # number of servers in M/M/c system
stime = 1.0  # mean service time
rate = 2.0  # mean arrival rate
maxNumber = 1000
seed(333555777)  # seed for random numbers

# Model -----------------------------------


class MMCmodel(Simulation):
    def run(self):
        self.initialize()
        self.m = Monitor(sim=self)  # monitor for the number of jobs
        self.mT = Monitor(sim=self)  # monitor for the time in system
        self.msT = Monitor(sim=self)  # monitor for the generated service times
        self.server = Resource(capacity=c, name='Gatekeeper', sim=self)
        g = Generator(name='gen', sim=self)
        self.activate(g, g.execute(maxNumber=maxNumber,
                                   rate=rate, stime=stime))
        self.m.observe(0)  # number in system is 0 at the start
        self.simulate(until=3000.0)


# Experiment ------------------------------
model = MMCmodel()
model.run()

# Analysis/output -------------------------

print('MMC')
print("{0:2d} servers, {1:6.4f} arrival rate, "
      "{2:6.4f} mean service time".format(c, rate, stime))
print("Average number in the system is {0:6.4f}".format(model.m.timeAverage()))
print("Average time in the system is   {0:6.4f}".format(model.mT.mean()))
print("Actual average service-time is  {0:6.4f}".format(model.msT.mean()))
