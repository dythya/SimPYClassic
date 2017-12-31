# coding=utf-8
from SimPy.Simulation  import *
from SimPy import (Globals, Simulation, SimulationStep, SimulationTrace,
                   SimulationRT)
import pytest
from random import random

class P(Process):
   """ P class for testing"""
   def __init__(self,name="",T = 0,sim=None):
        Process.__init__(self,name = name,sim = sim)
        self.name=name
        self.T = T

   def execute(self):
        yield hold,self,self.T

class PActions(Process):
   """ PActions class for testing"""
   def __init__(self,name="",T = 0,sim=None):
        Process.__init__(self,name = name,sim = sim)

        self.T = T

   def ACTIONS(self):
        yield hold,self,self.T

class ToStop(Process):
    """For testing stopSimulation
    """
    def run(self,stopTime):
        yield hold,self,self.sim.now()+stopTime
        self.sim.stopSimulation()
        yield hold,self,10

class ToCollect(Process):
    """For testing startCollection
    """
    def run(self,mon1,mon2,tal1,tal2):
        while True:
            yield hold,self,1
            mon1.observe(self.sim.now())
            mon2.observe(self.sim.now())
            tal1.observe(self.sim.now())
            tal2.observe(self.sim.now())

class ForEvtTimes(Process):
    """For testing allEventTimes
    """
    def run(self):
        yield hold,self


@pytest.fixture(autouse=True, params=[
    # Execute tests using a dedicated simulation instance (SimPy OO style).
    'default',
    # Execute tests using a SimulationStep instance.
    'step',
    # Execute tests using a SimulationTrace instance.
    'trace',
    # Execute tests using a SimulationRT instance.
    'rt',
    # Execute tests using the global simulation object (SimPy 1.x style).
    'global-default',
    # Execute tests using the global SimulationStep object.
    'global-step',
    # Execute tests using the global SimulationTrace object.
    'global-trace',
    # Execute tests using the global SimulationRT object.
    'global-rt'
])
def sim(request):
    if request.param == 'default':
        return Simulation.Simulation()
    elif request.param == 'step':
        return SimulationStep.SimulationStep()
    elif request.param == 'trace':
        return SimulationTrace.SimulationTrace()
    elif request.param == 'rt':
        return SimulationRT.SimulationRT()
    elif request.param.startswith('global'):
        if request.param.endswith('default'):
            Globals.sim = Simulation.Simulation()
        elif request.param.endswith('step'):
            Globals.sim = SimulationStep.SimulationStep()
        elif request.param.endswith('trace'):
            Globals.sim = SimulationTrace.SimulationTrace()
        elif request.param.endswith('rt'):
            Globals.sim = SimulationRT.SimulationRT()
        return Globals.sim

# Simulation tests
# ----------------

def test_simulation_init(sim):
    """Test initialisation
    """
    result=sim.simulate(until=10)
    assert result=="SimPy: No activities scheduled",\
           "There should have been no activities."
    assert(sim.now()==0),"time not 0"

def test_simulation_Activate(sim):
    """Test activate()
    """
    P1 = P(name="P1",T=100.0,sim=sim)
    sim.activate(P1,P1.execute(),0)
    sim.simulate(until=5)
    assert(sim.now()==5),"Simulate stopped at %s not %s"%(sim.now(),5)

def test_simulation_start(sim):
   """Test start method
   """
   P1 = P(name="P1",T=100.0,sim=sim)
   P1.start(P1.execute(),0)
   sim.simulate(until=5)
   assert(sim.now()==5),"Simulate stopped at %s not %s"%(sim.now(),5)

def test_simulation_start_actions(sim):
    """Test start method with ACTIONS PEM
    """
    P1 = PActions(name="P1",T=100.0,sim=sim)
    P1.start()
    sim.simulate(until=5)
    assert(sim.now()==5),"Simulate stopped at %s not %s"%(sim.now(),5)

def test_simulation_yield(sim):
    """Test yield hold and simulate(until)
    """
    P1 = P(name="P1",T=10,sim=sim)
    sim.activate(P1,P1.execute(),0)
    sim.simulate(until=5)
    assert(sim.now()==5),"Simulate stopped at %s not %s"%(sim.now(),5)
    ## should stop at 0 for next event is at 10s
    P2 = P(name="P2",T=10,sim=sim)
    sim.initialize()
    sim.activate(P2,P2.execute(),0)
    sim.simulate(until=20)
    assert(sim.now()==10),"P1 hold to %s not %s"%(sim.now(),10)

def test_simulation_stop_simulation(sim):
    """Test stopSimulation function/method
    """
    timeToStop = 7
    ts = ToStop(sim=sim)
    sim.activate(ts,ts.run(stopTime = timeToStop))
    sim.simulate(until = 50)
    assert(sim.now()==timeToStop),\
    "stopSimulation not working; now = %s instead of %s"%(sim.now(),timeToStop)

def test_simulation_start_collection(sim):
   """Test startCollection function/method
   """
   tStart = 9
   mon1 = Monitor("mon1",sim=sim)
   mon2 = Monitor("mon2",sim=sim)
   tal1 = Tally("tal1",sim=sim)
   tal2 = Tally("tal2",sim=sim)
   sim.startCollection(when = tStart,monitors=[mon1,mon2],tallies=[tal1,tal2])
   tc = ToCollect(sim=sim)
   sim.activate(tc,tc.run(mon1,mon2,tal1,tal2))
   sim.simulate(until=50)
   assert(mon1[0]==mon2[0]==[tStart,tStart]),\
          "startCollection not working correctly for Monitors"
   assert(tal1.count()==tal2.count()==50-tStart+1),\
          "startCollection not working for Tally"

def test_simulation_all_event_times(sim):
   """Test allEventTimes function/method
   """
   for i in range(3):
       f = ForEvtTimes(sim=sim)
       sim.activate(f,f.run(),at=i)
   assert(sim.allEventTimes()==[0,1,2]),\
          "allEventTimes not working"

# Resource tests
# --------------

class Job(Process):
   """ Job class for testing"""
   def __init__(self,server=None,name="",sim=None):
        Process.__init__(self,name = name,sim = sim)

        self.R=server

   def execute(self):
        yield request,self,self.R

def test_resource_init(sim):
    """Test initialisation"""
    R = Resource(sim=sim)
    assert R.name == "a_resource", "Not null name"
    assert R.capacity == 1, "Not unit capacity"
    assert R.unitName =="units", "Not the correct unit name"
    R = Resource(name='',capacity=1,sim=sim)
    assert R.name == "", "Not null name"
    assert R.capacity == 1, "Not unit capacity"
    assert R.unitName =="units", "Not the correct unit name"
    R = Resource(capacity=3,name="3-version",unitName="blobs",sim=sim)
    assert R.name =="3-version" , "Wrong name, it is"+R.name
    assert R.capacity == 3, "Not capacity 3, it is "+repr(R.capacity)
    assert R.unitName =="blobs", "Not the correct unit name"
    ## next test 0 capacity is allowed
    R = Resource(capacity=0,name="0-version",sim=sim)
    assert R.capacity ==0, "Not capacity 0, it is "+repr(R.capacity)

def test_resource_request(sim):
    """Test request"""
    ## now test requesting: ------------------------------------
    R0 = Resource(name='',capacity=0, sim=sim)
    assert R0.name == "", "Not null name"
    assert R0.capacity == 0, "Not capacity 0, it is "+repr(R0.capacity)
    R1 = Resource(capacity=0,name="3-version",unitName="blobs", sim=sim)
    J= Job(name="job",server=R1, sim=sim)
    sim.activate(J,J.execute(), at=0.0) # this requests a unit of R1
    ## when simulation starts
    sim.simulate(until=10.0)
    assert R1.n == 0 , "Should be 0, it is "+str(R1.n)
    lenW = len(R1.waitQ)
    assert lenW==1,"Should be 1, it is "+str(lenW)
    assert len(R1.activeQ)==0,"len activeQ Should be 0, it is "+\
    str(len(R1.activeQ))

def test_resource_request_2(sim):
    """Test request2 with capacity = 1"""
    ## now test requesting: ------------------------------------
    R2 = Resource(capacity=1,name="3-version",unitName="blobs", sim=sim)
    J2= Job(name="job",server=R2, sim=sim)
    sim.activate(J2,J2.execute(), at=0.0) # requests a unit of R2
    ## when simulation starts
    sim.simulate(until = 10.0)
    assert R2.n == 0 , "Should be 0, it is "+str(R2.n)
    lenW = len(R2.waitQ)
    lenA = len(R2.activeQ)
    assert lenW==0,"lenW Should be 0, it is "+str(lenW)
    assert lenA==1,"lenA Should be 1, it is "+str(lenA)

def test_resource_request_3(sim):
    """Test request3 with capacity = 1 several requests"""
    ## now test requesting: ------------------------------------
    R3 = Resource(capacity=1,name="3-version",unitName="blobs", sim=sim)
    J2= Job(name="job",server=R3, sim=sim)
    J3= Job(name="job",server=R3, sim=sim)
    J4= Job(name="job",server=R3, sim=sim)
    sim.activate(J2,J2.execute(), at=0.0) # requests a unit of R3
    sim.activate(J3,J3.execute(), at=0.0) # requests a unit of R3
    sim.activate(J4,J4.execute(), at=0.0) # requests a unit of R3
    ## when simulation starts
    sim.simulate(until = 10.0)
    assert R3.n == 0 , "Should be 0, it is "+str(R3.n)
    lenW = len(R3.waitQ)
    lenA = len(R3.activeQ)
    assert lenW==2,"lenW Should be 2, it is "+str(lenW)
    assert R3.waitQ==[J3,J4],"WaitQ wrong"+str(R3.waitQ)
    assert lenA==1,"lenA Should be 1, it is "+str(lenA)
    assert R3.activeQ==[J2],"activeQ wrong, it is %s"%str(R3.activeQ[0])

def test_resource_request_4(sim):
    """Test request4 with capacity = 2 several requests"""
    ## now test requesting: ------------------------------------
    R3 = Resource(capacity=2,name="4-version",unitName="blobs", sim=sim)
    J2= Job(name="job",server=R3, sim=sim)
    J3= Job(name="job",server=R3, sim=sim)
    J4= Job(name="job",server=R3, sim=sim)
    sim.activate(J2,J2.execute(), at=0.0) # requests a unit of R3
    sim.activate(J3,J3.execute(), at=0.0) # requests a unit of R3
    sim.activate(J4,J4.execute(), at=0.0) # requests a unit of R3
    ## when simulation starts
    sim.simulate(until = 10.0)
    assert R3.n == 0 , "Should be 0, it is "+str(R3.n)
    lenW = len(R3.waitQ)
    lenA = len(R3.activeQ)
    assert lenW==1,"lenW Should be 1, it is "+str(lenW)
    assert R3.waitQ==[J4],"WaitQ wrong"+str(R3.waitQ)
    assert lenA==2,"lenA Should be 2, it is "+str(lenA)
    assert R3.activeQ==[J2,J3],"activeQ wrong, it is %s"%str(R3.activeQ[0])
##
#------- Test Priority Queues
##
def test_resource_request_priority(sim):
    """Test PriorityQ, with no preemption, 0 capacity"""
    class Job(Process):
       """ Job class for testing"""
       def __init__(self,server=None,name="",sim=None):
          Process.__init__(self,name = name,sim=sim)

          self.R=server

       def execute(self,priority):
          yield request,self,self.R,priority

    Rp = Resource(capacity=0,qType=PriorityQ,sim=sim)
    J5 = Job(name="job 5",server=Rp,sim=sim)
    J6 = Job(name="job 6",server=Rp,sim=sim)
    J7 = Job(name="job 7",server=Rp,sim=sim)
    sim.activate(J5,J5.execute(priority=3))
    sim.activate(J6,J6.execute(priority=0))
    sim.activate(J7,J7.execute(priority=1))
    sim.simulate(until=100)
    assert Rp.waitQ == [J5,J7,J6],"WaitQ wrong: %s"\
                           %str([(x.name,x.priority[Rp]) for x in Rp.waitQ])

    """Test PriorityQ mechanism"""

    def sorted(q):
       if not q or len(q) == 1:
          sortok=1
          return sortok
       sortok = q[0] >= q[1] and sorted(q[2:])
       return sortok

    Rp=Resource(capacity=0,qType=PriorityQ,sim=sim)
    for i in range(10):
       J=Job(name="job "+str(i),server=Rp,sim=sim)
       sim.activate(J,J.execute(priority=random()))
    sim.simulate(until=1000)
    qp=[x._priority[Rp] for x in Rp.waitQ]
    assert sorted(qp),"waitQ not sorted by priority: %s"\
                       %str([(x.name,x._priority[Rp]) for x in Rp.waitQ])

def test_resource_request_priority_1(sim):
    """Test PriorityQ, with no preemption, capacity == 1"""
    class Job(Process):
       """ Job class for testing"""
       def __init__(self,server=None,name="",sim=None):
          Process.__init__(self, name = name, sim=sim)

          self.R=server

       def execute(self,priority):
          yield request,self,self.R,priority

    Rp = Resource(capacity=1,qType=PriorityQ,sim=sim)
    J5 = Job(name="job 5",server=Rp,sim=sim)
    J6 = Job(name="job 6",server=Rp,sim=sim)
    J7 = Job(name="job 7",server=Rp,sim=sim)
    sim.activate(J5,J5.execute(priority=2))
    sim.activate(J6,J6.execute(priority=4))
    sim.activate(J7,J7.execute(priority=3))
    sim.simulate(until=100)
    assert Rp.waitQ == [J6,J7],"WaitQ wrong: %s"\
                               %[(x.name,x._priority[Rp]) for x in Rp.waitQ]

def test_resource_request_priority_2(sim):
    """Test PriorityQ, with preemption, capacity == 1"""
    class nuJob(Process):
        def __init__(self,name = "", sim=None):
            Process.__init__(self, name = name, sim=sim)

        def execute(self,res,priority):
            self.preempt=len(res.activeQ) > 0\
                         and priority > res.activeQ[-1]._priority[res]
            t=self.sim.now()
            yield request,self,res,priority
            if self.preempt:
                assert len(res.waitQ) == 1, \
                    "No preemption activeQ= %s"%res.activeQ[0].name
            yield hold,self,30
            t1=self.sim.now()
            if self.preempt:
                assert t+30 == t1,\
                    "Wrong completion time for preemptor %s"%self.name
            else:
                assert t+60 == t1,\
                    "Wrong completion time for preempted %s %s:"\
                    %(self.name, self.sim.now())
            yield release,self,res

    res=Resource(name="server",capacity=1,qType=PriorityQ,preemptable=1,
                 sim=sim)
    n1=nuJob(name="nuJob 1",sim=sim)
    n2=nuJob(name="nuJob 2",sim=sim)
    sim.activate(n1,n1.execute(res,priority=0))
    sim.activate(n2,n2.execute(res,priority=1),at=15)
    sim.simulate(until=100)

def test_resource_request_priority_3(sim):
    """Test preemption of preemptor"""
    class nuJob(Process):
       seqOut=[]
       def __init__(self,name="",sim=None):
          Process.__init__(self, name = name, sim=sim)
          self.serviceTime=30

       def execute(self,res,priority):
          self.preempt=len(res.activeQ) > 0\
                       and priority > res.activeQ[-1]._priority[res]
          nrwaiting=len(res.waitQ)
          yield request,self,res,priority
          if self.preempt:
             assert len(res.waitQ) == nrwaiting + 1,\
                    "No preemption activeQ= %s"%res.activeQ[0].name
          yield hold,self,self.serviceTime
          yield release,self,res
          nuJob.seqOut.append((self,self.sim.now()))

    res=Resource(name="server",capacity=1,qType=PriorityQ,preemptable=1,
                 sim=sim)
    n1=nuJob(name="nuJob 1",sim=sim)
    n2=nuJob(name="nuJob 2",sim=sim)
    n3=nuJob(name="nuJob 3",sim=sim)
    sim.activate(n1,n1.execute(res,priority=-1))
    start2=10
    sim.activate(n2,n2.execute(res,priority=0),at=start2)
    start3=20
    sim.activate(n3,n3.execute(res,priority=1),at=start3)
    sim.simulate(until=100)
    assert [x[1] for x in nuJob.seqOut]\
            == [start3+n3.serviceTime,start2+2*n2.serviceTime,90],\
           "Wrong service sequence/times: %s"%[x[1] for x in nuJob.seqOut]

def test_resource_request_nested_preempt(sim):
    """Test that a process can preempt another process holding multiple resources
    """
    class Requestor(Process):
        def run(self,res1,res2,res3,priority=1):
            yield request,self,res1,priority
            yield request,self,res2,priority
            yield request,self,res3,priority
            record.observe(t=self.sim.now(),y=self.name)
            yield hold,self,100
            record.observe(t=self.sim.now(),y=self.name)
            yield release,self,res3
            yield release,self,res2
            yield release,self,res1

    outer=Resource(name="outer",qType=PriorityQ,preemptable=True,sim=sim)
    inner=Resource(name="inner",qType=PriorityQ,preemptable=True,sim=sim)
    innermost=Resource(name="innermost",qType=PriorityQ,preemptable=True,
                       sim=sim)
    record=Monitor(sim=sim)
    r1=Requestor("r1",sim=sim)
    sim.activate(r1,r1.run(res1=outer,res2=inner,res3=innermost,priority=1))
    r2=Requestor("r2",sim=sim)
    sim.activate(r2,r2.run(res1=outer,res2=inner,res3=innermost,priority=10),
               at=50)
    sim.simulate(until=200)
    assert record==[[0,"r1"],[50,"r2"],[150,"r2"],[200,"r1"]],\
            "was %s; preempt did not work"%record

def test_resource_monitored(sim):
    """ test monitoring of number in the two queues, waitQ and activeQ
    """
    class Job(Process):
        def __init__(self,name='',sim=None):
           Process.__init__(self,name = name,sim=sim)

        def execute(self,res):
           yield request,self,res
           yield hold,self,2
           yield release,self,res

    res=Resource(name="server",capacity=1,monitored=1,sim=sim)
    n1=Job(name="Job 1",sim=sim)
    n2=Job(name="Job 2",sim=sim)
    n3=Job(name="Job 3",sim=sim)
    sim.activate(n1,n1.execute(res),at=2)
    sim.activate(n2,n2.execute(res),at=2)
    sim.activate(n3,n3.execute(res),at=2) # 3 arrive at 2
    sim.simulate(until=100)
    assert res.waitMon == [[0, 0],[2, 1], [2, 2], [4, 1], [6, 0]],\
           'Wrong waitMon:%s'%res.waitMon
    assert res.actMon == [[0, 0],[2, 1], [4, 0], [4, 1], [6, 0], [6, 1], [8, 0]],\
            'Wrong actMon:%s'%res.actMon
    assert res.waitMon.timeAverage() == (0 * 2 + 2 * 2 + 1 * 2) / float(sim.now()), \
           'Wrong waitMon.timeAverage:%s'%res.waitMon.timeAverage()

# Interrupt tests
# ---------------

class Interruptor(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def breakin(self,waitbefore,howoften=1):
      for i in range(howoften):
         yield hold,self,waitbefore
         self.interrupt(victim)

class Interrupted(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def myActivity(self,howlong,theEnd=200):
      global igothit
      igothit={}
      while self.sim.now()<=theEnd:
         yield hold,self,howlong
         if self.interrupted():
            byWhom=self.interruptCause
            igothit[self.sim.now()]=byWhom
         else:
            pass

def test_interrupt_1(sim):
    """
    Test single interrupt during victim activity
    """
    global victim
    breaker=Interruptor(sim=sim)
    sim.activate(breaker,breaker.breakin(10))
    victim=Interrupted(sim=sim)
    sim.activate(victim,victim.myActivity(100))
    sim.simulate(until=200)
    assert igothit[10] == breaker, "Not interrupted at 10 by breaker"
    assert len(igothit) == 1 , "Interrupted more than once"

#      assert len(igothit) == 3 , "Interrupted wrong number of times"

def test_interrupt_2(sim):
    """
    Test multiple interrupts during victim activity
    """
    global victim
    breaker=Interruptor(sim=sim)
    sim.activate(breaker,breaker.breakin(10,howoften=3))
    victim=Interrupted(sim=sim)
    sim.activate(victim,victim.myActivity(100))
    sim.simulate(until=200)
    for i in (10,20,30):
        assert igothit[i] == breaker, "Not interrupted at %s by breaker" %i
    assert len(igothit) == 3 , "Interrupted wrong number of times"

def test_interrupt_3(sim):
    """
    Test interrupts after victim activity
    """
    global victim
    breaker=Interruptor(sim=sim)
    sim.activate(breaker,breaker.breakin(50,howoften=5))
    victim=Interrupted(sim=sim)
    sim.activate(victim,victim.myActivity(10,theEnd=10))
    sim.simulate(until=200)
    assert len(igothit) == 0 , "There has been an interrupt after victim lifetime"

def test_interrupt_4(sim):
    """
    Test multiple interrupts by multiple processes during victim activity
    """
    global victim
    breaker1=Interruptor(sim=sim)
    sim.activate(breaker1,breaker1.breakin(15,howoften=3))
    breaker2=Interruptor(sim=sim)
    sim.activate(breaker2,breaker2.breakin(20,howoften=3))
    victim=Interrupted(sim=sim)
    sim.activate(victim,victim.myActivity(100))
    sim.simulate(until=200)
    for i in (15,30,45):
        assert igothit[i] == breaker1, "Not interrupted at %s by breaker1" %i
    for i in (20,40,60):
        assert igothit[i] == breaker2, "Not interrupted at %s by breaker2" %i
    assert len(igothit) == 6 , "Interrupted wrong number of times"

def test_interrupt_5(sim):
    """
    Test reset of 'interrupted' state.
    """
    global victim
    breaker=Interruptor(sim=sim)
    victim=Interrupted(sim=sim)

    def newProcess(self):
        while True:
            assert not self.interrupted(),"Incorrectly interrupted"
            yield hold,self,100
            if self.interrupted():
                self.interruptReset()
                assert not self.interrupted(),"Incorrectly interrupted"

    victim.newProcess=newProcess
    sim.activate(victim,newProcess(victim))
    sim.activate(breaker,breaker.breakin(10,howoften=3))
    sim.simulate(until=1000)


# Process state tests
# -------------------

class PS1(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def life1(self):
      yield hold,self,10

   def life2(self):
      yield hold,self,10
      yield passivate,self
      yield hold,self,10

class Observer1(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def look1(self,p):
      assert p.active(),"p not active"
      assert not p.passive(), "p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      yield hold,self,11
      assert not p.active(),"p active"
      assert not p.passive(),"p passive"
      assert p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"

   def look2(self,p):
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"
      self.sim.activate(p,p.life1())
      yield hold,self,11
      assert not p.active(),"p active"
      assert not p.passive(),"p not passive"
      assert p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"

   def look3(self,p):
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"
      self.sim.activate(p,p.life2())
      yield hold,self,11
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

   def look4(self,p):
      yield hold,self,5
      assert p.active(),"p not active"
      assert not p.passive(),"p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      self.cancel(p)
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      self.sim.reactivate(p)
      assert p.active(),"p not active"
      assert not p.passive(),"p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      yield hold,self
      assert not p.active(),"p active"
      assert not p.passive(),"p passive"
      assert p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

   def look5(self,p):
      yield hold,self,11
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      self.cancel(p)
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

class PS2(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def life1(self,res):
      yield hold,self,1
      yield request,self,res
      yield hold,self,5
      yield request,self,res

   def life2(self,res):
      yield request,self,res
      assert self.interrupted(),"p not interrupted"
      assert self.queuing(res)
      self.interruptReset()
      assert not self.interrupted(), "p interrupted"
      assert self.queuing(res)

class Observer2(Process):
   def __init__(self,sim=None):
      Process.__init__(self,sim=sim)

   def look1(self,p1,p2,res):
      assert p1.active(), "p1 not active"
      assert not p1.queuing(res), "p1 queuing"
      assert p2.active(), "p2 not active"
      assert not p2.queuing(res), "p2 queuing"
      yield hold,self,2
      assert p1.active(), "p1 not active"
      assert not p1.queuing(res), "p1 queuing"
      assert p2.passive(), "p2 active"
      assert p2.queuing(res), "p2 not queuing"

   def look2(self,p,res):
      yield request,self,res
      yield hold,self,5
      assert p.passive(),"p not passive"
      assert p.queuing(res),"p not queuing for resource"
      assert not p.interrupted(), "p interrupted"
      self.interrupt(p)
      yield hold,self

def test_state_1(sim):
    """
    Tests state transitions by hold
    """
    ## active => hold => terminated
    sim.initialize()
    p=PS1(sim=sim)
    sim.activate(p,p.life1())
    ob=Observer1(sim=sim)
    sim.activate(ob,ob.look1(p),prior=True)
    sim.simulate(until=12)

def test_state_2(sim):
    """
    Tests state transitions by activate and passivate
    """
    ## passive => activate => hold => terminated
    p=PS1(sim=sim)
    ob1=Observer1(sim=sim)
    sim.activate(ob1,ob1.look2(p))
    sim.simulate(until=12)
    ## passive => activate => hold => active => passivate => passive
    sim.initialize()
    p1=PS1(sim=sim)
    ob2=Observer1(sim=sim)
    sim.activate(ob2,ob2.look3(p1),prior=True)
    sim.simulate(until=12)

def test_state_3(sim):
    """
    Tests state transitions by cancel()
    """
    ## active => cancel => passive => reactivate => active => terminated
    p2=PS1(sim=sim)
    sim.activate(p2,p2.life1())
    ob3=Observer1(sim=sim)
    sim.activate(ob3,ob3.look4(p2))
    sim.simulate(until=12)

    ## passive => cancel => passive
    sim.initialize()
    p3=PS1(sim=sim)
    sim.activate(p3,p3.life2())
    ob4=Observer1(sim=sim)
    sim.activate(ob4,ob4.look5(p3))
    sim.simulate(until=12)

def test_state_4(sim):
    """
    Test request/release state transitions
    """
    ## not queuing,active => request => queuing,passive => release => not queuing,active
    res=Resource(capacity=1,sim=sim)
    pq1=PS2(sim=sim)
    sim.activate(pq1,pq1.life1(res))
    pq2=PS2(sim=sim)
    sim.activate(pq2,pq2.life1(res))
    obq1=Observer2(sim=sim)
    sim.activate(obq1,obq1.look1(pq1,pq2,res))
    sim.simulate(until=12)

    ## queuing,passive => interrupt =>  queuing, interrupted => interruptRest => queuing, not interrupted
    sim.initialize()
    res=Resource(capacity=1,sim=sim)
    pq3=PS2(sim=sim)
    sim.activate(pq3,pq3.life2(res))
    obq2=Observer2(sim=sim)
    sim.activate(obq2,obq2.look2(pq3,res),prior=True)
    sim.simulate(until=12)


# Event/Signal tests
# ------------------

class SignalProcess(Process):
   def __init__(self,**var):
       Process.__init__(self,**var)

   def makeSignal(self,ev1,ev2):
      yield hold,self,1
      ev1.signal("from SignalProcess")
      while ev2.queues:
         nq0=len(ev2.queues)
         ev2.signal("from SignalProcess")
         assert len(ev2.queues)==(nq0-1),"wrong number of processes dequeued"

class WaitProcess(Process):
   def __init__(self,**var):
       Process.__init__(self,**var)

   def waitForSig(self,ev1):
      yield waitevent,self,ev1
      assert ev1.waits==[],"not all processes waiting for event out of waiting list"
      assert ev1 in self.eventsFired,"did not record firing event"

class QueueProcess(Process):
   def __init__(self,**var):
       Process.__init__(self,**var)

   def queueForSig(self,ev2):
      yield queueevent,self,ev2
      assert ev2 in self.eventsFired,"did not record firing event"

class SignalProcessOR(Process):
   def __init__(self,**var):
       Process.__init__(self,**var)

   def makeSignal(self,ev1,ev2):
      yield hold,self,1
      ev1.signal("from SignalProcess")
      yield hold,self,3
      assert len(ev2.queues)==QueueProcessOR.nrProcesses,"wrong number of processes queuing for event ev2"
      while ev2.queues:
          nq0=len(ev2.queues)
          ev2.signal("from SignalProcess")
          assert len(ev2.queues)==(nq0-1),"wrong number of processes dequeued"
      assert not ev2.queues,"not all processes queuing for ev2 dequeued"

class WaitProcessOR(Process):
   def __init__(self,**var):
       Process.__init__(self,**var)

   def waitForSig(self,evset):
      yield waitevent,self,evset
      for e in evset:
         assert e.waits==[],"process not out of waiting list for all events in OR"

class WaitProcessOR1(Process):
    def __init__(self,**var):
       Process.__init__(self,**var)

    def signalandwait(self):
      e1=SimEvent(sim = self.sim)
      e1.signal()
      e2=SimEvent(sim = self.sim)
      e2.signal()
      yield waitevent,self,[e1,e2]
      assert self.eventsFired==[e1,e2],"eventsFired does not report all events"


class QueueProcessOR(Process):
    nrProcesses=0
    def __init__(self,**var):
        Process.__init__(self,**var)
        QueueProcessOR.nrProcesses+=1

    def queueForSig(self,evset):
      yield queueevent,self,evset
      occurred=False
      for e in evset:
          occurred=occurred or (e in self.eventsFired)
      assert occurred,"queuing process activated by wrong event(s)"

class QueueProcessOR1(Process):
    def __init__(self,**var):
       Process.__init__(self,**var)

    def signalandqueue(self):
        e1=SimEvent(sim = self.sim)
        e1.signal()
        e2=SimEvent(sim = self.sim)
        e2.signal()
        yield queueevent,self,[e1,e2]
        assert self.eventsFired==[e1,e2],\
                "(queueevent) eventsFired does not report all fired events"

def test_sim_events_1(sim):
    """
    Tests basic signal semantics
    """
    e=SimEvent(sim=sim)
    e.signal("param")
    assert e.occurred,"signal does not set 'occurred' to True"
    assert e.signalparam=="param","signal parameter wrong"
    e.signal()
    assert e.signalparam is None,"signal with no parameter did not overwrite signalparam"
    e.signal()
    assert e.occurred,"multiple calls to signal do not set 'occurred'"

def test_sim_events_2(sim):
    """
    Tests basic waiting and queuing semantics
    """
    ev1=SimEvent("ev1",sim=sim)
    ev2=SimEvent("ev2",sim=sim)
    w1=WaitProcess(sim=sim)
    sim.activate(w1,w1.waitForSig(ev1))
    w2=WaitProcess(sim=sim)
    sim.activate(w2,w2.waitForSig(ev1))
    for i in range(3):
        q=QueueProcess(sim=sim)
        sim.activate(q,q.queueForSig(ev2))
    sim.simulate(until=2)
    # FIXME This is ugly: Reset QueueProcessOR.nrProcesses variable for
    # following tests.
    QueueProcessOR.nrProcesses = 0

def test_sim_events_3(sim):
    """
    Tests waiting, queuing for at least one event out of a list/tuple.
    """
    e1=SimEvent("e1",sim=sim)
    e2=SimEvent("e2",sim=sim)
    e3=SimEvent("e3",sim=sim)
    s=SignalProcessOR(sim=sim)
    sim.activate(s,s.makeSignal(e1,e3))
    w=WaitProcessOR(sim=sim)
    sim.activate(w,w.waitForSig([e1,e2]))
    for i in range(5):
        q=QueueProcessOR(sim=sim)
        sim.activate(q,q.queueForSig([e2,e3]))
    sim.simulate(until=10)
    # FIXME This is ugly: Reset QueueProcessOR.nrProcesses variable for
    # following tests.
    QueueProcessOR.nrProcesses = 0

def test_sim_events_4(sim):
    """Tests that eventsFired reports all events which fired
    """
    w=WaitProcessOR1(sim=sim)
    sim.activate(w,w.signalandwait())
    sim.simulate(until=5)

def test_sim_events_5(sim):
    """Tests that eventsFired reports all events which fired
    """
    w=QueueProcessOR1(sim=sim)
    sim.activate(w,w.signalandqueue())
    sim.simulate(until=5)

# Waituntil tests
# ---------------

class Signaller(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def makeconditions(self,waiter):
        global a,b,c
        a=True
        yield hold,self,1
        b=True
        yield hold,self,1
        c=True
        yield hold,self,1
        assert waiter.terminated(),"waituntil did not fire"

class Waiter(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def waitforit(self):
        def waitcond():
            return a and b and c
        yield waituntil,self,waitcond

def test_waituntil(sim):
     global a,b,c
     a=b=c=False
     w=Waiter(sim=sim)
     sim.activate(w,w.waitforit())
     s=Signaller(sim=sim)
     sim.activate(s,s.makeconditions(w))
     sim.simulate(until=5)

# Compound "yield request" tests
# ------------------------------
#
# Tests "yield (request,self,res),(hold,self,delay)" == timeout renege for both
# unmonitored and monitored resources

class JobTO(Process):
   """ Job class for testing timeout reneging
   """
   def __init__(self,server=None,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
        self.res=server
        self.gotResource=None

   def execute(self,timeout,usetime):
        yield (request,self,self.res),(hold,self,timeout)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False

class JobTO_P(Process):
   """ Job class for testing timeout reneging with priorities
   """
   def __init__(self,server=None,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
        self.res=server
        self.gotResource=None

   def execute(self,timeout,usetime,priority):
        yield (request,self,self.res,priority),(hold,self,timeout)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False

def test_no_timeout(sim):
    """Test that resource gets acquired without timeout
    """
    res=Resource(name="Server",capacity=1,sim=sim)
    usetime=5
    timeout=1000000
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert sim.now()==2*usetime,"time not ==2*usetime"
    assert j1.gotResource and j2.gotResource,\
        "at least one job failed to get resource"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"

def test_no_timeout_M(sim):
    """Test that resource gets acquired without timeout.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=1,monitored=True,sim=sim)
    usetime=5
    timeout=1000000
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert sim.now()==2*usetime,"time not ==2*usetime"
    assert j1.gotResource and j2.gotResource,\
        "at least one job failed to get resource"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[usetime,0]],"res.waitMon wrong: %s"%res.waitMon

def test_timeout_1(sim):
    """Test that timeout occurs when resource busy
    """
    res=Resource(name="Server",capacity=1,sim=sim)
    usetime=5
    timeout=3
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert(sim.now()==usetime),"time not ==usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"

def test_timeout_1M(sim):
    """Test that timeout occurs when resource busy.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=1,monitored=True,sim=sim)
    usetime=5
    timeout=3
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert(sim.now()==usetime),"time not == usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[timeout,0]],"res.waitMon wrong: %s"%res.waitMon

def test_timeout__MP(sim):
    """Test that timeout occurs when resource busy.
       Resource monitored. Requests with priority and preemption.
    """
    res=Resource(name="Server",capacity=1,monitored=True,
                 qType=PriorityQ,preemptable=True,sim=sim)
    usetime=5
    timeout=3
    j1=JobTO_P(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime,priority=1))
    j2=JobTO_P(server=res,name="Job_2",sim=sim)
    j2_arrival=1
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime,priority=5),
               at=j2_arrival)
    j3=JobTO_P(server=res,name="Job_2",sim=sim)
    j3_arrival=2
    sim.activate(j3,j3.execute(timeout=timeout,usetime=usetime,priority=10),
               at=j3_arrival)
    sim.simulate(until=3*usetime)
    assert(sim.now()== 3*usetime),"time not == 2* usetime, but %s"%now()
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(j2.gotResource),"Job_2 did renege"
    assert(j2.gotResource),"Job_3 did renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[j2_arrival,1],[j3_arrival,2],[usetime+j3_arrival,1],\
          [usetime+j2_arrival+usetime,0]],"res.waitMon wrong: %s"%res.waitMon

def test_timeout_2(sim):
    """Test that timeout occurs when resource has no capacity free
    """
    res=Resource(name="Server",capacity=0,sim=sim)
    usetime=5
    timeout=3
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert sim.now()==timeout,"time %s not == timeout"%sim.now()
    assert not j1.gotResource,"Job_1 got resource"
    assert not j2.gotResource,"Job_2 got resource"
    assert not (res.waitQ or res.activeQ),\
           "job waiting or using resource"

def test_timeout_2M(sim):
    """Test that timeout occurs when resource has no capacity free.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=0,monitored=True,sim=sim)
    usetime=5
    timeout=3
    j1=JobTO(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(timeout=timeout,usetime=usetime))
    j2=JobTO(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(timeout=timeout,usetime=usetime))
    sim.simulate(until=2*usetime)
    assert sim.now()==timeout,"time %s not == timeout"%sim.now()
    assert not j1.gotResource,"Job_1 got resource"
    assert not j2.gotResource,"Job_2 got resource"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[0,2],[timeout,1],[timeout,0]],\
        "res.waitMon is wrong: %s"%res.waitMon

# Compound "yield request" tests
# ------------------------------
#
# Tests "yield (request,self,res),(waitevent,self,event)" == event renege for
# both unmonitored and monitored resources


class JobEvt(Process):
   """ Job class for testing event reneging
   """
   def __init__(self,server=None,name="",sim=None):
        Process.__init__(self,name = name, sim = sim)
        self.res=server
        self.gotResource=None

   def execute(self,event,usetime):
        yield (request,self,self.res),(waitevent,self,event)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False

class JobEvtMulti(Process):
   """ Job class for testing event reneging with multi-event lists
   """
   def __init__(self,server=None,name="",sim=None):
        Process.__init__(self,name = name, sim=sim)
        self.res=server
        self.gotResource=None

   def execute(self,eventlist,usetime):
        yield (request,self,self.res),(waitevent,self,eventlist)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False

class FireEvent(Process):
    """Fires reneging event
    """
    def __init__(self,name="",sim=None):
        Process.__init__(self,name,sim=sim)
    def fire(self,fireDelay,event):
        yield hold,self,fireDelay
        event.signal()

def test_no_event_(sim):
    """Test that processes acquire resource normally if no event fires
    """
    event=SimEvent("Renege_trigger",sim=sim) #never gets fired
    res=Resource(name="Server",capacity=1,sim=sim)
    usetime=5
    j1=JobEvt(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(event=event,usetime=usetime))
    j2=JobEvt(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(event=event,usetime=usetime))
    sim.simulate(until=2*usetime)
    # Both jobs should get server (in sequence)
    assert sim.now()==2*usetime,"time not ==2*usetime"
    assert j1.gotResource and j2.gotResource,\
        "at least one job failed to get resource"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"

def test_no_event_M(sim):
    """Test that processes acquire resource normally if no event fires.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=1,monitored=True,sim=sim)
    event=SimEvent("Renege_trigger",sim=sim) #never gets fired
    usetime=5
    j1=JobEvt(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(event=event,usetime=usetime))
    j2=JobEvt(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(event=event,usetime=usetime))
    sim.simulate(until=2*usetime)
    # Both jobs should get server (in sequence)
    assert sim.now()==2*usetime,"time not ==2*usetime"
    assert j1.gotResource and j2.gotResource,\
        "at least one job failed to get resource"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[usetime,0]],"res.waitMoni is wrong: %s"%res.waitMon

def test_wait_event_1(sim):
    """Test that signalled event leads to renege when resource busy
    """
    res=Resource(name="Server",capacity=1,sim=sim)
    event=SimEvent("Renege_trigger",sim=sim)
    usetime=5
    eventtime=1
    j1=JobEvt(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(event=event,usetime=usetime))
    j2=JobEvt(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(event=event,usetime=usetime))
    f=FireEvent(name="FireEvent",sim=sim)
    sim.activate(f,f.fire(fireDelay=eventtime,event=event))
    sim.simulate(until=2*usetime)
    # Job_1 should get server, Job_2 renege
    assert(sim.now()==usetime),"time not ==usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"

def test_wait_event_1M(sim):
    """Test that signalled event leads to renege when resource busy.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=1,monitored=True,sim=sim)
    event=SimEvent("Renege_trigger",sim=sim)
    usetime=5
    eventtime=1
    j1=JobEvt(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(event=event,usetime=usetime))
    j2=JobEvt(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(event=event,usetime=usetime))
    f=FireEvent(name="FireEvent",sim=sim)
    sim.activate(f,f.fire(fireDelay=eventtime,event=event))
    sim.simulate(until=2*usetime)
    # Job_1 should get server, Job_2 renege
    assert(sim.now()==usetime),"time not == usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[eventtime,0]],"res.waitMon is wrong: %s"%res.waitMon

def test_wait_event_2(sim):
    """Test that renege-triggering event can be one of an event list
    """
    res=Resource(name="Server",capacity=1,sim=sim)
    event1=SimEvent("Renege_trigger_1",sim=sim)
    event2=SimEvent("Renege_trigger_2",sim=sim)
    usetime=5
    eventtime=1 #for both events
    j1=JobEvtMulti(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(eventlist=[event1,event2],usetime=usetime))
    j2=JobEvtMulti(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(eventlist=[event1,event2],usetime=usetime))
    f1=FireEvent(name="FireEvent_1",sim=sim)
    sim.activate(f1,f1.fire(fireDelay=eventtime,event=event1))
    f2=FireEvent(name="FireEvent_2",sim=sim)
    sim.activate(f2,f2.fire(fireDelay=eventtime,event=event2))
    sim.simulate(until=2*usetime)
    # Job_1 should get server, Job_2 should renege
    assert(sim.now()==usetime),"time not ==usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"

def test_wait_event_2M(sim):
    """Test that renege-triggering event can be one of an event list.
       Resource monitored.
    """
    res=Resource(name="Server",capacity=1,monitored=True,sim=sim)
    event1=SimEvent("Renege_trigger_1",sim=sim)
    event2=SimEvent("Renege_trigger_2",sim=sim)
    usetime=5
    eventtime=1 #for both events
    j1=JobEvtMulti(server=res,name="Job_1",sim=sim)
    sim.activate(j1,j1.execute(eventlist=[event1,event2],usetime=usetime))
    j2=JobEvtMulti(server=res,name="Job_2",sim=sim)
    sim.activate(j2,j2.execute(eventlist=[event1,event2],usetime=usetime))
    f1=FireEvent(name="FireEvent_1",sim=sim)
    sim.activate(f1,f1.fire(fireDelay=eventtime,event=event1))
    f2=FireEvent(name="FireEvent_2",sim=sim)
    sim.activate(f2,f2.fire(fireDelay=eventtime,event=event2))
    sim.simulate(until=2*usetime)
    # Job_1 should get server, Job_2 should renege
    assert(sim.now()==usetime),"time not ==usetime"
    assert(j1.gotResource),"Job_1 did not get resource"
    assert(not j2.gotResource),"Job_2 did not renege"
    assert not (res.waitQ or res.activeQ),\
        "job waiting or using resource"
    assert res.waitMon==[[0,0],[0,1],[eventtime,0]],"res.waitMon is wrong: %s"%res.waitMon

# Compound "yield request" tests
# ------------------------------
#
# Tests "yield get,self,level,whatToGet" and
# "yield put,self,level,whatToPut,priority" for level instances

class Producer(Process):
    produced=0
    def __init__(self,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
    def produce(self,buffer):
        for i in range(4):
            Producer.produced+=1
            yield put,self,buffer
            yield hold,self,1
    def producePriority(self,buffer,priority):
        """PriorityQ for Producers"""
        Producer.produced+=4
        yield put,self,buffer,4,priority
        yield hold,self,1
        self.done=self.sim.now()
        doneList.append(self.name)
    def produce1(self,buffer):
        for i in range(4):
            yield put,self,buffer,4
            yield hold,self,1
class Consumer(Process):
    consumed=0
    def __init__(self,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
    def consume(self,buffer):
        """FIFO"""
        yield get,self,buffer
        Consumer.consumed+=1
        assert self.got==1,"wrong self.got: %s"%self.got
        yield get,self,buffer,3
        Consumer.consumed+=3
        assert self.got==3,"wrong self.got: %s"%self.got

    def consume1(self,buffer):
        """producer PriorityQ, consumer FIFO"""
        while True:
            yield get,self,buffer,2
            yield hold,self,1
    def consumePriority(self,buffer,priority):
        """PriorityQ for Consumers"""
        yield get,self,buffer,4,priority
        doneList.append(self.name)

class  ProducerPrincL(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def produce(self,buffer,productionTime):
        while True:
            assert not(buffer.amount>0 and len(buffer.getQ)>0),\
                "Consumer(s) waiting while buffer not empty"
            yield hold,self,productionTime
            yield put,self,buffer,1

class ConsumerPrincL(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def consume(self,buffer,consumptionTime):
        while True:
            assert not(buffer.amount==0 and len(buffer.putQ)>0),\
                "Producer(s) waiting while buffer empty"
            yield get,self,buffer,1
            yield hold,self,consumptionTime

def test_static(sim):
    """Tests initialization of Level instances
    """
    a=Level(sim=sim)
    assert a.capacity==sys.maxsize,"wrong capacity:%s"%a
    assert a.amount==0,"wrong buffer content: %s"%a
    assert a.name=="a_level","wrong name: %s"%a
    assert not a.monitored,"should not be monitored: %s"%a
    assert a.putQMon is None,"should not have putQMon: %s"%a
    assert a.getQMon is None,"should not have getQMon: %s"%a
    assert a.bufferMon is None,"should not have bufferMon: %s"%a
    assert a.putQType.__name__=="FIFO" and a.getQType.__name__=="FIFO",\
           "putQType and getQType should be FIFO: %s"%a

    b=Level(name="b",initialBuffered=10.0,monitored=True,capacity=12,
                putQType=PriorityQ,sim=sim)
    a=Level(sim=sim)
    assert b.capacity==12,"wrong capacity:%s"%b
    assert b.amount==10,"wrong buffer content: %s"%b
    assert b.name=="b","wrong name: %s"%b
    assert b.monitored,"should be monitored: %s"%b
    assert not (b.putQMon is None),"should have putQMon: %s"%b
    assert not (b.getQMon is None),"should have getQMon: %s"%b
    assert not (b.bufferMon is None),"should have bufferMon: %s"%b
    assert b.putQType.__name__=="PriorityQ",\
           "putQType should be PriorityQ: %s"%b
    assert b.getQType.__name__=="FIFO",\
            "getQType should be PriorityQ: %s"%b

def test_con_prod_Principle(sim):
    """Level: tests basic Producer/Consumer principles:
    -   Consumers must not be waiting while Level buffer value > 0,
    -   Producers must not be waiting while Level buffer value == 0
    """
    bufferSize=1
    productionTime=1
    consumptionTime=5
    endtime=50
    buffer=Level(capacity=bufferSize,sim=sim)
    consumer=ConsumerPrincL(sim=sim)
    sim.activate(consumer,consumer.consume(buffer,consumptionTime))
    producer=ProducerPrincL(sim=sim)
    sim.activate(producer,producer.produce(buffer,productionTime))
    sim.simulate(until=endtime)

def test_con_prod_1(sim):
    """Level: tests put/get in 1 Producer/ 1 Consumer scenario"""
    buffer=Level(initialBuffered=0,sim=sim)
    p=Producer(sim=sim)
    sim.activate(p,p.produce(buffer))
    c=Consumer(sim=sim)
    sim.activate(c,c.consume(buffer))
    sim.simulate(until=100)
    assert Producer.produced-Consumer.consumed==buffer.amount,\
        "items produced/consumed/buffered do not tally: %s %s %s"\
            %(Producer.produced,Consumer.consumed,buffer.amount)

def test_con_prod_M(sim):
    """Level: tests put/get in multiple Producer/Consumer scenario"""
    buffer=Level(initialBuffered=0,sim=sim)
    Producer.produced=0
    Consumer.consumed=0
    for i in range(2):
        c=Consumer(sim=sim)
        sim.activate(c,c.consume(buffer))
    for i in range(3):
        p=Producer(sim=sim)
        sim.activate(p,p.produce(buffer))
    sim.simulate(until=10)
    assert Producer.produced-Consumer.consumed==buffer.amount,\
        "items produced/consumed/buffered do not tally: %s %s %s"\
            %(Producer.produced,Consumer.consumed,buffer.amount)

def test_con_prod_prior_M(sim):
    """Level: tests put/get in multiple Producer/Consumer scenario,
    with Producers having different priorities.
    How: Producers forced to queue; all after first should be done in
    priority order
    """
    global doneList
    doneList=[]
    buffer=Level(capacity=7,putQType=PriorityQ,monitored=True,sim=sim)
    for i in range(4):
        p=Producer(str(i), sim=sim)
        pPriority=i
        sim.activate(p,p.producePriority(buffer=buffer,priority=pPriority))
    c=Consumer(sim=sim)
    sim.activate(c,c.consume1(buffer=buffer))
    sim.simulate(until=100)
    assert doneList==["0","3","2","1"],"puts were not done in priority order: %s"\
                                %doneList

def test_con_prior_prod_M(sim):
    """Level: tests put/get in multiple Producer/Consumer scenario, with
    Consumers having different priorities.
    How: Consumers forced to queue; all after first should be done in
    priority order
    """
    global doneList
    doneList=[]
    buffer=Level(capacity=7,getQType=PriorityQ,monitored=True,sim=sim)
    for i in range(4):
        c=Consumer(str(i), sim=sim)
        cPriority=i
        sim.activate(c,c.consumePriority(buffer=buffer,priority=cPriority))
    p=Producer(sim=sim)
    sim.activate(p,p.produce1(buffer=buffer))
    sim.simulate(until=100)
    assert doneList==["3","2","1","0"],"gets were not done in priority order: %s"\
                                %doneList

# Compound "yield request" tests
# ------------------------------
#
# Tests "yield get,self,store,whatToGet" and "yield put,self,store,whatToPut"
# for Store instances.

class ProducerWidget(Process):
    produced=0
    def __init__(self,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
    def produce(self,buffer):
        for i in range(4):
            ProducerWidget.produced+=1
            yield put,self,buffer,[Widget(weight=5)]
            yield hold,self,1
    def producePriority(self,buffer,priority):
        """PriorityQ for Producers"""
        ProducerWidget.produced+=4
        toStore=[Widget(weight=5)]*4
        yield put,self,buffer,toStore,priority
        yield hold,self,1
        self.done=self.sim.now()
        doneList.append(self.name)
    def produce1(self,buffer):
        for i in range(4):
            yield put,self,buffer,[Widget(weight=5)]*4
            yield hold,self,1
    def produceUnordered(self,buffer):
        produced=[Widget(weight=i) for i in [9,1,8,2,7,3,6,4,5]]
        yield put,self,buffer,produced

class ConsumerWidget(Process):
    consumed=0
    def __init__(self,name="",sim=None):
        Process.__init__(self,name=name,sim=sim)
    def consume(self,buffer):
        """FIFO"""
        yield get,self,buffer
        ConsumerWidget.consumed+=1
        assert len(self.got)==1,"wrong self.got: %s"%self.got
        yield get,self,buffer,3
        ConsumerWidget.consumed+=3
        assert len(self.got)==3,"wrong self.got: %s"%self.got

    def consume1(self,buffer):
        """producer PriorityQ, consumer FIFO"""
        while True:
            yield get,self,buffer,2
            yield hold,self,1

    def consumePriority(self,buffer,priority):
        """PriorityQ for Consumers"""
        yield get,self,buffer,4,priority
        doneList.append(self.name)

    def consumeSorted(self,buffer,gotten):
        yield get,self,buffer
        gotten.append(self.got[0].weight)

class Widget:
    def __init__(self,weight):
        self.weight=weight

def mySortFunc(self,par):
    """Sorts Widget instances by weight attribute."""
    tmplist=[(x.weight,x) for x in par]
    tmplist.sort()
    return [x for (key,x) in tmplist]

class  ProducerPrincS(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def produce(self,buffer,productionTime):
        while True:
            assert not(buffer.nrBuffered>0 and len(buffer.getQ)>0),\
                "Consumer(s) waiting while buffer not empty"
            yield hold,self,productionTime
            product=WidgetPrinc()
            yield put,self,buffer,[product]

class ConsumerPrincS(Process):
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def consume(self,buffer,consumptionTime):
        while True:
            assert not(buffer.nrBuffered==0 and buffer.putQ),\
                "Producer(s) waiting while buffer empty"
            yield get,self,buffer,1
            yield hold,self,consumptionTime

class WidgetPrinc:
    pass

class FilterConsumer(Process):
    """Used in testBufferFilter"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    class Widget:
        def __init__(self,weighs):
            self.weight=weighs

    def getItems(self,store,a,b):
        """get all items with weight between a and b"""
        def between_a_and_b(buf):
            res=[]
            for item in buf:
                if a<item.weight<b:
                    res.append(item)

        all=store.buffered
        yield get,self,store,between_a_and_b
        "All retrieved items weight in range?"
        for it in self.got:
            assert a<it.weight<b,"weight %s not in range %s..%s"\
                                 %(it.weight,a,b)
        "Any item fitting filter pred left in buffer?"
        for it in store.buffer:
            assert not (a<it.weight<b),\
                "item left in buffer which fits filter (%s<%s<%s)"\
                %(a,it.weight,b)
        "All items either in store.buffer of self.got?"
        for it in all:
            assert (it in self.buffer) or (it in self.got),\
                   "item w. weight %s neither in store nor in got"%it.weight

def test_static(sim):
    """Store: tests initialization of Store instances
    """
    a=Store(sim=sim)
    assert a.capacity==sys.maxsize,"wrong capacity:%s"%a
    assert a.nrBuffered==0,"wrong buffer content: %s"%a
    assert a.name=="a_store","wrong name: %s"%a
    assert not a.monitored,"should not be monitored: %s"%a
    assert a.putQMon is None,"should not have putQMon: %s"%a
    assert a.getQMon is None,"should not have getQMon: %s"%a
    assert a.bufferMon is None,"should not have bufferMon: %s"%a
    assert a.putQType.__name__=="FIFO" and a.getQType.__name__=="FIFO",\
           "putQType and getQType should be FIFO: %s"%a

    stored=[Widget(weight=5)]*10
    b=Store(name="b",initialBuffered=stored,monitored=True,capacity=12,
                putQType=PriorityQ,sim=sim)
    assert b.capacity==12,"wrong capacity:%s"%b
    assert b.nrBuffered==10,"wrong buffer content: %s"%b
    assert b.name=="b","wrong name: %s"%b
    assert b.monitored,"should be monitored: %s"%b
    assert not (b.putQMon is None),"should have putQMon: %s"%b
    assert not (b.getQMon is None),"should have getQMon: %s"%b
    assert not (b.bufferMon is None),"should have bufferMon: %s"%b
    assert b.putQType.__name__=="PriorityQ",\
           "putQType should be PriorityQ: %s"%b
    assert b.getQType.__name__=="FIFO",\
            "getQType should be PriorityQ: %s"%b

def test_con_prod_principle(sim):
    """Store: tests basic Producer/Consumer principles:
    -   Consumers must not be waiting while items in Store buffer,
    -   Producers must not be waiting while space available in Store buffer
    """
    bufferSize=1
    productionTime=1
    consumptionTime=5
    endtime=50
    buffer=Store(capacity=bufferSize,sim=sim)
    consumer=ConsumerPrincS(sim=sim)
    sim.activate(consumer,consumer.consume(buffer,consumptionTime))
    producer=ProducerPrincS(sim=sim)
    sim.activate(producer,producer.produce(buffer,productionTime))
    sim.simulate(until=endtime)

def test_con_prod_1(sim):
    """Store: tests put/get in 1 Producer/ 1 Consumer scenario"""
    buffer=Store(initialBuffered=[],sim=sim)
    p=ProducerWidget(sim=sim)
    sim.activate(p,p.produce(buffer))
    c=ConsumerWidget(sim=sim)
    sim.activate(c,c.consume(buffer))
    sim.simulate(until=100)
    assert \
       ProducerWidget.produced-ConsumerWidget.consumed==buffer.nrBuffered,\
       "items produced/consumed/buffered do not tally: %s %s %s"\
       %(ProducerWidget.produced,ConsumerWidget.consumed,buffer.nrBuffered)

def test_con_prod_M(sim):
    """Store: tests put/get in multiple Producer/Consumer scenario"""
    buffer=Store(initialBuffered=[],sim=sim)
    ProducerWidget.produced=0
    ConsumerWidget.consumed=0
    for i in range(2):
        c=ConsumerWidget(sim=sim)
        sim.activate(c,c.consume(buffer))
    for i in range(3):
        p=ProducerWidget(sim=sim)
        sim.activate(p,p.produce(buffer))
    sim.simulate(until=10)
    assert ProducerWidget.produced-ConsumerWidget.consumed==buffer.nrBuffered,\
        "items produced/consumed/buffered do not tally: %s %s %s"\
        %(ProducerWidget.produced,ConsumerWidget.consumed,buffer.nrBuffered)

def test_con_prod_prior_M(sim):
    """Store: Tests put/get in multiple Producer/Consumer scenario,
    with Producers having different priorities.
    How; Producers forced to queue; all after first should be done in
    priority order
    """
    global doneList
    doneList=[]
    buffer=Store(capacity=7,putQType=PriorityQ,monitored=True,sim=sim)
    for i in range(4):
        p=ProducerWidget(name=str(i), sim=sim)
        pPriority=i
        sim.activate(p,p.producePriority(buffer=buffer,priority=pPriority))
    c=ConsumerWidget(sim=sim)
    sim.activate(c,c.consume1(buffer=buffer))
    sim.simulate(until=100)
    assert doneList==["0","3","2","1"],"puts were not done in priority order: %s"\
                                %doneList

def test_con_prior_prod_M(sim):
    """Tests put/get in multiple Producer/Consumer scenario, with
    Consumers having different priorities.
    How; Consumers forced to queue; all after first should be done in
    priority order
    """
    global doneList
    doneList=[]
    buffer=Store(capacity=7,getQType=PriorityQ,monitored=True,sim=sim)
    for i in range(4):
        c=ConsumerWidget(name=str(i),sim=sim)
        cPriority=i
        sim.activate(c,c.consumePriority(buffer=buffer,priority=cPriority))
    p=ProducerWidget(sim=sim)
    sim.activate(p,p.produce1(buffer=buffer))
    sim.simulate(until=100)
    assert doneList==["3","2","1","0"],\
          "gets were not done in priority order: %s"%doneList

def test_buffer_sort(sim):
    """Tests the optional sorting of theBuffer by applying a user-defined
    sort function."""
    gotten=[]
    sortedStore=Store(sim=sim)
    sortedStore.addSort(mySortFunc)
    p=ProducerWidget(sim=sim)
    sim.activate(p,p.produceUnordered(sortedStore))
    for i in range(9):
        c=ConsumerWidget(sim=sim)
        sim.activate(c,c.consumeSorted(buffer=sortedStore,gotten=gotten),at=1)
    sim.simulate(until=10)
    assert gotten==[1,2,3,4,5,6,7,8,9],"sort wrong: %s"%gotten

def test_buffer_filter(sim):
    """Tests get from a Store with a filter function
    """
    ItClass=FilterConsumer.Widget
    all=[ItClass(1),ItClass(4),ItClass(6),ItClass(12)]
    st=Store(initialBuffered = all, sim=sim)
    fc=FilterConsumer(sim=sim)
    minw=2;maxw=10
    sim.activate(fc,fc.getItems(store=st,a=minw,b=maxw))
    sim.simulate(until=1)

## ------------------------------------------------------------------
##
##  Store: Tests for compound get/put
##
## ------------------------------------------------------------------
class TBT(Process):
    """Store: For testBasicTime"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def tbt(self,store):
        yield get,self,store,1
        assert self.got,"Did not get Item"
        yield (get,self,store,1),(hold,self,5)
        if self.acquired(store):
            assert len(self.got)==1,"did not get 1 Item"
        else:
            assert not self.got and self.sim.now()==5 and not store.getQ,\
                   "time renege not working"

class TBE(Process):
    """Store: For testBasicEvent"""
    def __init__(self,name="",sim=None):
        Process.__init__(self,sim=sim)
    def tbe(self,store,trigger):
        yield get,self,store,1
        assert self.got,"Did not get Item"
        yield (get,self,store,1),(waitevent,self,trigger)
        if self.acquired(store):
            assert False, "should have reneged"
        else:
            assert self.eventsFired[0]==trigger and self.sim.now()==5 \
                and not store.getQ,"event renege not working"

class TBEtrigger(Process):
    """Store: For testBasicEvent"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def fire(self,trigger):
        yield hold,self,5
        trigger.signal()


class TBTput(Process):
    """Store: for testBasicTimePut"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def tbt(self,store):
        class Item:pass
        yield (put,self,store,[Item()]),(hold,self,4)
        if self.stored(store):
            assert store.nrBuffered==1 and not store.putQ,\
                   "put did not execute"
        else:
            assert False,"should not have reneged"
        yield (put,self,store,[Item()]),(hold,self,5)
        if self.stored(store):
            assert False,"should have reneged"
        else:
            assert store.nrBuffered==1 and not store.putQ,\
                   "renege not working correctly"

class TBEput(Process):
    """Store: for testBasicEventPut"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def tbe(self,store,trigger):
        class Item:pass
        yield (put,self,store,[Item()]),(waitevent,self,trigger)
        if self.stored(store):
            assert store.nrBuffered==1 and not store.putQ,\
                   "put did not execute"
        else:
            assert False,"should have not have reneged"
        yield (put,self,store,[Item()]),(waitevent,self,trigger)
        if self.stored(store):
            assert False,"should have reneged"
        else:
            assert self.sim.now()==5 and self.eventsFired[0]==trigger\
                   and not store.putQ,"renege not working correctly"

class TBEtriggerPut(Process):
    """Store: For testBasicEventPut"""
    def __init__(self,sim=None):
        Process.__init__(self,sim=sim)
    def fire(self,trigger):
        yield hold,self,5
        trigger.signal()

# Tests for compound get statements
# ---------------------------------
#
# Tests "yield (get,self,store),(hold,self,time)" == timeout renege for both
# unmonitored and monitored Stores

def test_basic_time(sim):
    """Store (unmonitored):
    test 'yield (get,self,store),(hold,self,timeout)"""
    class Item(object):
        pass
    st=Store(initialBuffered=[Item()],sim=sim)
    t=TBT(sim=sim)
    sim.activate(t,t.tbt(store=st))
    sim.simulate(until=10)

def test_basic_time_put(sim):
    """Store (unmonitored):
    test 'yield (put,self,store),(hold,self,time)"""
    st=Store(capacity=1,sim=sim)
    t=TBTput(sim=sim)
    sim.activate(t,t.tbt(store=st))
    sim.simulate(until=10)

def test_basic_time_put_M(sim):
    """Store (monitored):
    test monitors with 'yield (put,self,store),(hold,self,time)"""
    st=Store(capacity=1,monitored=True,sim=sim)
    t=TBTput(sim=sim)
    sim.activate(t,t.tbt(store=st))
    sim.simulate(until=10)
    #First put succeeds, second attempt reneges at t=5?
    assert st.putQMon==[[0,0],[0,1],[5,0]],"putQMon wrong: %s"\
                                           %st.putQMon
    #First Item goes into buffer at t=0, second not (renege)?
    assert st.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%st.bufferMon

def test_basic_event(sim):
    """Store (unmonitored):
    test 'yield (get,self,store),(waitevent,self,event)"""
    class Item(object):
        pass
    st=Store(initialBuffered=[Item()],sim=sim)
    trig=SimEvent(sim=sim)
    t=TBE(sim=sim)
    sim.activate(t,t.tbe(store=st,trigger=trig))
    tr=TBEtrigger(sim=sim)
    sim.activate(tr,tr.fire(trigger=trig))
    sim.simulate(until=10)

def test_basic_event_put(sim):
    """Store (unmonitored):
    test 'yield (put,self,store),(waitevent,self,event)"""
    s=SimEvent(sim=sim)
    store=Store(capacity=1,sim=sim)
    t=TBEtriggerPut(sim=sim)
    sim.activate(t,t.fire(trigger=s))
    tb=TBEput(sim=sim)
    sim.activate(tb,tb.tbe(store=store,trigger=s))
    sim.simulate(until=10)

def test_basic_event_put_M(sim):
    """Store (monitored):
    test monitors with 'yield (put,self,store),(waitevent,self,event)"""
    s=SimEvent(sim=sim)
    st=Store(capacity=1,monitored=True,sim=sim)
    t=TBEtriggerPut(sim=sim)
    sim.activate(t,t.fire(trigger=s))
    tb=TBEput(sim=sim)
    sim.activate(tb,tb.tbe(store=st,trigger=s))
    sim.simulate(until=10)
    #First put succeeds, second attempt reneges at t=5?
    assert st.putQMon==[[0,0],[0,1],[5,0]],"putQMon wrong: %s"\
                                           %st.putQMon
    #First Item goes into buffer at t=0, second not (renege)?
    assert st.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%st.bufferMon

## ------------------------------------------------------------------
##
##  Level: Tests for compound get
##
## ------------------------------------------------------------------
class TBTLev(Process):
    """Level: For testBasicTime"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def tbt(self,level):
        yield get,self,level,1
        assert self.got,"did not get 1 unit"
        yield (get,self,level,1),(hold,self,5)
        if self.acquired(level):
            assert self.got==1,"did not get 1 unit"
        else:
            assert not self.got and self.sim.now()==5,\
                   "time renege not working"

class TBELev(Process):
    """Level: For testBasicEvent"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def tbe(self,level,trigger):
        yield get,self,level,1
        assert self.got,"did not get 1 unit"
        yield (get,self,level,1),(waitevent,self,trigger)
        if self.acquired(level):
            assert self.got==1,"did not get 1 Item"
        else:
            assert self.sim.now()==5.5 and self.eventsFired[0]==trigger,\
                   "event renege not working"

class TBEtriggerLev(Process):
    """Level: For testBasicEvent"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def fire(self,trigger):
        yield hold,self,5.5
        trigger.signal()

class TBTLevPut(Process):
    """Level: For testBasicTimePut"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def tbt(self,level):
        yield put,self,level,1
        assert level.amount,"did not put 1 unit"
        yield (put,self,level,1),(hold,self,5)
        if self.stored(level):
            assert False,"should have reneged"
        else:
            assert level.amount==1 and self.sim.now()==5,\
                   "time renege not working"

class TBELevPut(Process):
    """Level: For testBasicEventPut and testBasicEventPutM"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def tbe(self,level,trigger):
        yield (put,self,level,1),(waitevent,self,trigger)
        if self.stored(level):
            assert level.amount==1,"did not put 1 unit"
        else:
            assert False,"should not have reneged"
        yield (put,self,level,1),(waitevent,self,trigger)
        if self.stored(level):
            assert False, "should have reneged"
        else:
            assert self.sim.now()==5.5 and self.eventsFired[0]==trigger ,\
                   "renege not working"

class TBEtriggerLevPut(Process):
    """Level: For testBasicEventPut"""
    def __init__(self,**par):
        Process.__init__(self,**par)
    def fire(self,trigger):
        yield hold,self,5.5
        trigger.signal()

# Tests for compound get and put statements
# -----------------------------------------

def test_basic_time(sim):
    """Level (unmonitored):
        test 'yield (get,self,level),(hold,self,timeout)
    """
    l=Level(initialBuffered=1,sim=sim)
    t=TBTLev(sim=sim)
    sim.activate(t,t.tbt(level=l))
    sim.simulate(until=10)

def test_basic_time_put(sim):
    """Level (unmonitored):
    test 'yield (put,self,level),(hold,self,timeout)"""
    l=Level(capacity=1,sim=sim)
    t=TBTLevPut(sim=sim)
    sim.activate(t,t.tbt(level=l))
    sim.simulate(until=10)

def test_basic_event(sim):
    """Level (unmonitored):
    test 'yield (get,self,level),(waitevent,self,event)"""
    l=Level(initialBuffered=1,sim=sim)
    trig=SimEvent(sim=sim)
    t=TBELev(sim=sim)
    sim.activate(t,t.tbe(level=l,trigger=trig))
    tr=TBEtriggerLev(sim=sim)
    sim.activate(tr,tr.fire(trigger=trig))
    sim.simulate(until=10)

def test_basic_event_M(sim):
    """Level (monitored):
    test monitors with 'yield (get,self,level),(waitevent,self,event)"""
    l=Level(initialBuffered=1,monitored=True,sim=sim)
    trig=SimEvent(sim=sim)
    t=TBELev(sim=sim)
    sim.activate(t,t.tbe(level=l,trigger=trig))
    tr=TBEtriggerLev(sim=sim)
    sim.activate(tr,tr.fire(trigger=trig))
    sim.simulate(until=10)
    #First get (t=0) succeeded and second timed out at t=5.5?
    assert l.getQMon==[[0,0],[0,1],[5.5,0]],"getQMon not working: %s"\
                                           %l.getQMon
    #Level amount incr. then decr. by 1 (t=0), 2nd get reneged at t=5.5?
    assert l.bufferMon==[[0,1],[0,0]],\
           "bufferMon not working: %s"%l.bufferMon

def test_basic_event_put(sim):
    """Level (unmonitored):
    test 'yield (put,self,level),(waitevent,self,event)"""
    l=Level(capacity=1,sim=sim)
    trig=SimEvent(sim=sim)
    t=TBELevPut(sim=sim)
    sim.activate(t,t.tbe(level=l,trigger=trig))
    tr=TBEtriggerLevPut(sim=sim)
    sim.activate(tr,tr.fire(trigger=trig))
    sim.simulate(until=10)

def test_basic_event_put_M(sim):
    """Level (monitored):
    test monitors with 'yield (put,self,level),(waitevent,self,event)"""
    l=Level(capacity=1,monitored=True,sim=sim)
    trig=SimEvent(sim=sim)
    t=TBELevPut(sim=sim)
    sim.activate(t,t.tbe(level=l,trigger=trig))
    tr=TBEtriggerLevPut(sim=sim)
    sim.activate(tr,tr.fire(trigger=trig))
    sim.simulate(until=10)
    "First put succeeds, second reneges at t=5.5?"
    assert l.putQMon==[[0,0],[0,1],[5.5,0]],"putQMon wrong: %s"\
                                            %l.putQMon
    "1 unit added at t=0, renege at t=5 before 2nd unit added?"
    assert l.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%l.bufferMon
