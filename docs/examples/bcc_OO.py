""" bcc_OO.py

  Queue with blocked customers cleared
  Jobs (e.g messages) arrive randomly at rate 1.0 per minute at a
  2-server system.  Mean service time is 0.75 minutes and the
  service-time distribution is (1) exponential, (2) Erlang-5, or (3)
  hyperexponential with p=1/8,m1=2.0, and m2=4/7. However no
  queue is allowed; a job arriving when all the servers are busy is
  rejected.

  Develop and run a simulation program to estimate the probability of
  rejection (which, in steady-state, is the same as p(c)) Measure
  and compare the probability for each service time distribution.
  Though you should test the program with a trace, running just a few
  jobs, the final runs should be of 10000 jobs without a trace. Stop
  the simulation when 10000 jobs have been generated.
"""

from SimPy.Simulation import *
from random import seed, Random, expovariate

# Model components ------------------------

dist = ""


def bcc(lam, mu, s):
    """ bcc - blocked customers cleared model

    - returns p[i], i = 0,1,..s.
    - ps = p[s] = prob of blocking
    - lameff = effective arrival rate = lam*(1-ps)

    See Winston 22.11 for Blocked Customers Cleared Model (Erlang B formula)
    """
    rho = lam / mu
    n = range(s + 1)
    p = [0] * (s + 1)
    p[0] = 1
    sump = 1.0
    for i in n[1:]:
        p[i] = (rho / i) * p[i - 1]
        sump = sump + p[i]
    p0 = 1.0 / sump
    for i in n:
        p[i] = p[i] * p0
    p0 = p[0]
    ps = p[s]
    lameff = lam * (1 - ps)
    L = rho * (1 - ps)
    return {'lambda': lam, 'mu': mu, 's': s,
            'p0': p0, 'p[i]': p, 'ps': ps, 'L': L}


def ErlangVariate(mean, K):
    """ Erlang random variate

    mean = mean
    K = shape parameter
    g = rv to be used
    """
    sum = 0.0
    mu = K / mean
    for i in range(K):
        sum += expovariate(mu)
    return (sum)


def HyperVariate(p, m1, m2):
    """ Hyperexponential random variate

    p = prob of branch 1
    m1 = mean of exponential, branch 1
    m2 = mean of exponential, branch 2
    g = rv to be used
    """
    if random() < p:
        return expovariate(1.0 / m1)
    else:
        return expovariate(1.0 / m2)


def testHyperVariate():
    """ tests the HyerVariate rv generator"""
    ERR = 0
    x = (1.0981, 1.45546, 5.7470156)
    p = 0.0, 1.0, 0.5
    g = Random(1113355)
    for i in range(3):
        x1 = HyperVariate(p[i], 1.0, 10.0, g)
        # print(p[i], x1)
        assert abs(x1 - x[i]) < 0.001, 'HyperVariate error'


def erlangB(rho, c):
    """ Erlang's B formula for probabilities in no-queue

    Returns p[n] list
    see also SPlus and R version in que.q mmcK
    que.py has bcc.
    """
    n = range(c + 1)
    pn = list(range(c + 1))
    term = 1
    pn[0] = 1
    sum = 1
    term = 1.0
    i = 1
    while i < (c + 1):
        term *= rho / i
        pn[i] = term
        sum += pn[i]
        i += 1
    for i in n:
        pn[i] = pn[i] / sum
    return(pn)


class JobGen(Process):
    """ generates a sequence of Jobs
    """

    def execute(self, JobRate, MaxJob, mu):
        global NoInService, Busy
        for i in range(MaxJob):
            j = Job(sim=self.sim)
            self.sim.activate(j, j.execute(i, mu), delay=0.0)
            t = expovariate(JobRate)
            MT.tally(t)
            yield hold, self, t
        self.trace("Job generator finished")

    def trace(self, message):
        if JobGenTRACING:
            print("{0:8.4f} \t{1}".format(self.sim.now(), message))


class Job(Process):
    """ Jobs that are either accepted or rejected
    """

    def execute(self, i, mu):
        """ Job execution, only if accepted"""
        global NoInService, Busy, dist, NoRejected
        if NoInService < c:
            self.trace("Job %2d accepted b=%1d" % (i, Busy))
            NoInService += 1
            if NoInService == c:
                Busy = 1
                try:
                    BM.accum(Busy, self.sim.now())
                except:
                    "accum error BM=", BM
            # yield hold,self,Job.g.expovariate(self.mu);
            # dist= "Exponential"
            yield hold, self, ErlangVariate(1.0 / mu, 5)
            dist = "Erlang     "
            # yield hold,self,HyperVariate(1.0/8,m1=2.0,m2=4.0/7,g=Job.g);
            # dist= "HyperExpon "
            NoInService -= 1
            Busy = 0
            BM.accum(Busy, self.sim.now())
            self.trace("Job %2d leaving b=%1d" % (i, Busy))
        else:
            self.trace("Job %2d REJECT  b=%1d" % (i, Busy))
            NoRejected += 1

    def trace(self, message):
        if JobTRACING:
            print("{0:8.4f} \t{1}".format(self.sim.now(), message))


# Experiment data -------------------------
c = 2
lam = 1.0  # per minute
mu = 1.0 / 0.75  # per minute
p = 1.0 / 8
m1 = 2.0
m2 = 4.0 / 7.0
K = 5
rho = lam / mu

NoRejected = 0
NoInService = 0
Busy = 0

JobRate = lam
JobMax = 10000

JobTRACING = 0
JobGenTRACING = 0


# Model/Experiment ------------------------------

seed(111333)
s = Simulation()
BM = Monitor(sim=s)
MT = Monitor(sim=s)

s.initialize()
jbg = JobGen(sim=s)
s.activate(jbg, jbg.execute(1.0, JobMax, mu), 0.0)
s.simulate(until=20000.0)

# Analysis/output -------------------------

print('bcc')
print("time at the end = {0}".format(s.now()))
print("now = {0}\tstartTime = {1}".format(s.now(), BM.startTime))
print("No Rejected = {0:d}, ratio= {1}".format(
    NoRejected, (1.0 * NoRejected) / JobMax))
print("Busy proportion ({0}) = {1:8.6f}".format(dist, BM.timeAverage()))
print("Erlang pc (th)                = {0:8.6f}".format(erlangB(rho, c)[c]))
