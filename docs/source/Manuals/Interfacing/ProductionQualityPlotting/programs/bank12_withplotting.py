#! /usr/local/bin/python
""" Based on bank12.py in Bank Tutorial.
This program uses matplotlib. It produces two plots:
- Queue length over time
- Histogram of queue length
"""
from SimPy.Simulation import *
import pylab as pyl
from random import Random


## Model components
class Source(Process):
    """ Source generates customers randomly"""
    def __init__(self,seed=333):
        Process.__init__(self)
        self.SEED = seed

    def generate(self,number,interval):
        rv = Random(self.SEED)
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(timeInBank=12.0))
            t = rv.expovariate(1.0/interval)
            yield hold,self,t


class Customer(Process):
    """ Customer arrives, is served and leaves """
    def __init__(self,name):
        Process.__init__(self)
        self.name = name

    def visit(self,timeInBank=0):
        arrive=now()
        yield request,self,counter
        wait=now()-arrive
        wate.observe(y=wait)
        tib = counterRV.expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,counter


class Observer(Process):
    def __init__(self):
        Process.__init__(self)

    def observe(self):
        while True:
            yield hold,self,5
            qu.observe(y=len(counter.waitQ))

# Model
def model(counterseed=3939393):
    global counter,counterRV,waitMonitor
    counter = Resource(name="Clerk",capacity = 1)
    counterRV = Random(counterseed)
    waitMonitor = Monitor()
    initialize()
    sourceseed=1133
    source = Source(seed = sourceseed)
    activate(source,source.generate(100,10.0))
    ob=Observer()
    activate(ob,ob.observe())
    simulate(until=2000.0)


qu=Monitor(name="Queue length")
wate=Monitor(name="Wait time")
## Experiment data
sourceSeed=333
## Experiment
model()
## Output
pyl.figure(figsize=(5.5,4))
pyl.plot(qu.tseries(),qu.yseries())
pyl.title("Bank12: queue length over time",
          fontsize=12,fontweight="bold")
pyl.xlabel("time",fontsize=9,fontweight="bold")
pyl.ylabel("queue length before counter",fontsize=9,fontweight="bold")
pyl.grid(True)
pyl.show()
pyl.savefig("./bank12.png")
print("Saved graph in current directory as bank12.png")

pyl.clf()
n, bins, patches = pyl.hist(qu.yseries(), 10, normed=True)
pyl.title("Bank12: Frequency of counter queue length",
          fontsize=12,fontweight="bold")
pyl.xlabel("queuelength",fontsize=9,fontweight="bold")
pyl.ylabel("frequency",fontsize=9,fontweight="bold")
pyl.grid(True)
pyl.xlim(0,30)
pyl.show()
pyl.savefig("./bank12histo.png")
print("Saved graph in current directory as bank12histo.png")
