from SimPy.Simulation import *
from random import uniform,seed
import string

## Model components ------------------------
def theTime(time):

    hrs=int(time/60)
    min=int(time-hrs*60)
    return "%s:%s" %(string.zfill(str(hrs),2),string.zfill(str(min),2))

class worker(Process):
    def __init__(self,id,sim):
        Process.__init__(self,sim=sim)
        self.id = id
        self.output = 0
        self.idle = 0
        self.total_idle = 0

    def working_day(self,foobar):
        print "%s Worker %s arrives in factory" %(theTime(self.sim.now()),self.id)
        while self.sim.now()<17*60: #work till 5 pm
            yield hold,self,uniform(3,10)
            #print "%s Widget completed" %theTime(now())
            foobar.queue.append(self)
            if foobar.idle:
                self.sim.reactivate(foobar)
            else:
                self.idle = 1 #worker has to wait for foobar service
                start_idle = self.sim.now()
                #print "%s Worker %s queuing for foobar machine" %(theTime(now()),self.id)
            yield passivate,self #waiting and foobar service
            self.output += 1
            if self.idle:
                self.total_idle += self.sim.now()-start_idle
            self.idle=0
        print "%s %s goes home, having built %d widgets today." %(theTime(self.sim.now()),self.id,self.output)
        print "Worker %s was idle waiting for foobar machine for %3.1f hours" %(self.id,self.total_idle/60)

class foobar_machine(Process):
    def __init__(self,sim):
        Process.__init__(self,sim=sim)
        self.queue=[]
        self.idle=1

    def foobar_Process(self):
        yield passivate,self
        while 1:
            while len(self.queue) > 0:
                self.idle=0
                yield hold,self,3
                served=self.queue.pop(0)
                self.sim.reactivate(served)
            self.idle=1
            yield passivate,self
            
## Model -----------------------------------
class SimPy_Worker_Extend_Model(Simulation):
    def run(self):
        print 'SimPy_worker_extend'
        self.initialize()
        foo=foobar_machine(sim=self)
        self.activate(foo,foo.foobar_Process(),delay=0)
        john=worker("John",sim=self)
        self.activate(john,john.working_day(foo),at=510) #start at 8:30 am
        eve=worker("Eve",sim=self)
        self.activate(eve,eve.working_day(foo),at=510)
        self.simulate(until=18*60) #run simulation from midnight till 6 pm

## Expriment -------------------------------
seed(111333555)
SimPy_Worker_Extend_Model().run()
