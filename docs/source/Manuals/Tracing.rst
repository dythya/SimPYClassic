.. highlight:: python
   :linenothreshold: 5 
 
=============================
Simulation with Tracing
=============================

:Authors: - Klaus Muller <Muller@users.sourceforge.net>
:SimPy release: |release|
:Web-site: https://github.com/SimPyClassic/SimPyClassic
:Python-Version: 2.7 and later
:Date: December 2011
:Updated: January 2018

.. contents:: Contents
   :depth: 2

Introduction
-------------------
The tracing utility has been developed to give users insight into the
dynamics of the execution of SimPy simulation programs. It can help
developers with testing and users with explaining SimPy models to themselves
and others (e.g. for documentation or teaching purposes).

Tracing *SimPy* programs
-------------------------

Tracing any *SimPy* program is as simple as replacing:: 

	from SimPy.Simulation import *

with::

	from SimPy.SimulationTrace import *

This will give a complete trace of all the scheduling statements 
executed during the program's execution.

An even nicer way is to replace this import by::

	if __debug__:
		from SimPy.SimulationTrace import *
	else:
		from SimPy.Simulation import *


This gives a trace during the development and debugging. If one then 
executes the program with 
*python -O myprog.py*, tracing is switched off, and no run-time
overhead is incurred. (*__debug__* is a
global Python constant which is set to False by commandline options -O
and -OO.)

For the same reason, any user call to *trace* methods should be written
as::

	if __debug__:
		trace.ttext("This will only show during debugging")

Here is an example (bank02.py from the Bank Tutorial)::

	from SimPy.SimulationTrace import * #   <== changed for tracing
	##from SimPy.Simulation import * 

	""" Simulate a single customer """
	class Customer(Process):
		""" Customer arrives, looks around and leaves """
		def __init__(self,name):
			Process.__init__(self)
			self.name = name
			
	def visit(self,timeInBank=0):
		print "%7.4f %s: Here I am"%(now(),self.name)
		yield hold,self,timeInBank
		print "%7.4f %s: I must leave"%(now(),self.name)
		
	def model():
		initialize()
		c1=Customer(name="Klaus")
		activate(c1,c1.visit(timeInBank=10.0),delay=5.0)
		c2=Customer(name="Tony")
		activate(c2,c2.visit(timeInBank=8.0),delay=2.0)
		c3=Customer(name="Evelyn")
		activate(c3,c3.visit(timeInBank=20.0),delay=12.0)
		simulate(until=400.0)
		
	model()

This program produces the following output::

  0 activate <Klaus> at time: 5.0 prior: 0
  0 activate <Tony> at time: 2.0 prior: 0
  0 activate <Evelyn> at time: 12.0 prior: 0
  2.0000 Tony: Here I am
  2.0 hold <Tony> delay: 8.0
  5.0000 Klaus: Here I am
  5.0 hold <Klaus> delay: 10.0
  10.0000 Tony: I must leave
  10.0 <Tony> terminated
  12.0000 Evelyn: Here I am
  12.0 hold <Evelyn> delay: 20.0
  15.0000 Klaus: I must leave
  15.0 <Klaus> terminated
  32.0000 Evelyn: I must leave
  32.0 <Evelyn> terminated


Another example::

    """ bank09.py: Simulate customers arriving
        at random, using a Source requesting service
        from several clerks but a single queue
        with a random servicetime
    """
    from __future__ import generators
    from SimPy.SimulationTrace  import *
    from random import Random

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
            print "%7.4f %s: Here I am "%(now(),self.name)
            yield request,self,counter
            wait=now()-arrive
            print "%7.4f %s: Waited %6.3f"%(now(),self.name,wait)
            tib = counterRV.expovariate(1.0/timeInBank)
            yield hold,self,tib
            yield release,self,counter
            print "%7.4f %s: Finished"%(now(),self.name)

    def model(counterseed=3939393):
        global counter,counterRV
        counter = Resource(name="Clerk",capacity = 2) #Lcapacity
        counterRV = Random(counterseed)
        initialize()
        sourceseed = 1133
        source = Source(seed = sourceseed)
        activate(source,source.generate(5,10.0),0.0)
        simulate(until=400.0)

    model()

This produces::

      0 activate <a_process> at time: 0 prior: 0
    0 activate <Customer00> at time: 0 prior: 0
    0 hold <a_process> delay: 8.73140489458
     0.0000 Customer00: Here I am 
    0 request <Customer00> <Clerk>  priority: default 
    . . .waitQ: [] 
    . . .activeQ: ['Customer00']
     0.0000 Customer00: Waited  0.000
    0 hold <Customer00> delay: 8.90355092634
    8.73140489458 activate <Customer01> at time: 8.73140489458 prior: 0
    8.73140489458 hold <a_process> delay: 8.76709801376
     8.7314 Customer01: Here I am 
    8.73140489458 request <Customer01> <Clerk>  priority: default 
    . . .waitQ: [] 
    . . .activeQ: ['Customer00', 'Customer01']
     8.7314 Customer01: Waited  0.000
    8.73140489458 hold <Customer01> delay: 21.6676883425
    8.90355092634 release <Customer00> <Clerk> 
    . . .waitQ: [] 
    . . .activeQ: ['Customer01']
     8.9036 Customer00: Finished
    8.90355092634 <Customer00> terminated
    17.4985029083 activate <Customer02> at time: 17.4985029083 prior: 0

    . . . . . 
 
And here is an example showing the trace output for compound yield statements::

    from SimPy.SimulationTrace import *
    class Client(Process):
        def __init__(self,name):
            Process.__init__(self,name)
        def getServed(self,tank):
            yield (get,self,tank,10),(hold,self,1.5)
            if self.acquired(tank):
                print "%s got 10 %s"%(self.name,tank.unitName)
            else:
                print "%s reneged"%self.name 
    class Filler(Process):
        def __init__(self,name):
            Process.__init__(self,name)
        def fill(self,tank):
            for i in range(3):
                yield hold,self,1
                yield put,self,tank,10
    initialize()
    tank=Level(name="Tank",unitName="gallons")
    for i in range(2):
        c=Client("Client %s"%i)
        activate(c,c.getServed(tank))
    f=Filler("Tanker")
    activate(f,f.fill(tank))
    simulate(until=10)
    
It produces this output::

    0 get <Client 0>to get: 10 gallons from <Tank>  priority: default 
    . . .getQ: ['Client 0'] 
    . . .putQ: [] 
    . . .in buffer: 0
    || RENEGE COMMAND:
    ||	hold <Client 0> delay: 1.5
    0 get <Client 1>to get: 10 gallons from <Tank>  priority: default 
    . . .getQ: ['Client 0', 'Client 1'] 
    . . .putQ: [] 
    . . .in buffer: 0
    || RENEGE COMMAND:
    ||	hold <Client 1> delay: 1.5
    0 hold <Tanker> delay: 1
    0 hold <RENEGE-hold for Client 0> delay: 1.5
    0 hold <RENEGE-hold for Client 1> delay: 1.5
    1 put <Tanker> to put: 10 gallons into <Tank>  priority: default 
    . . .getQ: ['Client 1'] 
    . . .putQ: [] 
    . . .in buffer: 0
    1 hold <Tanker> delay: 1
    Client 0 got 10 gallons
    1 <Client 0> terminated
    1.5 <RENEGE-hold for Client 1> terminated
    Client 1 reneged
    1.5 <Client 1> terminated
    2 put <Tanker> to put: 10 gallons into <Tank>  priority: default 
    . . .getQ: [] 
    . . .putQ: [] 
    . . .in buffer: 10
    2 hold <Tanker> delay: 1
    3 put <Tanker> to put: 10 gallons into <Tank>  priority: default 
    . . .getQ: [] 
    . . .putQ: [] 
    . . .in buffer: 20
    3 <Tanker> terminated
    
In this example, the Client entities are requesting 10 gallons from the *tank* (a Level object). 
If they can't get them within 1.5 time units, they renege (give up waiting).
The renege command parts of the compound statements (*hold,self,1.5*)are shown 
in the trace output with a prefix of || to indicate that they are being executed 
in parallel with the primary command part (*get,self,tank,10*). They are being
executed by behind-the-scenes processes (e.g. *RENEGE-hold for Client 0*).

The trace contains all calls of scheduling statements (**yield . . .**,
**activate()**, **reactivate()**, **cancel()** and also the termination
of processes (at completion of all their scheduling statements). For 
**yield request** and **yield release** calls, it provides also the queue
status (waiting customers in *waitQ* and customers being served in *activeQ*.

**trace.tchange()**: Changing the tracing
------------------------------------------

**trace** is an instance of the **Trace** class defined in *SimulationTrace.py*.
This gets automatically initialized upon importing *SimulationTrace*..

The tracing can be changed at runtime by calling **trace.tchange()** with one or
more of the following named parameters:

  *start*: 

    changes the tracing start time. Default is 0. Example: **trace.tchange(start=222.2)** 
    to start tracing at simulation time 222.2.

  *end*  : 

    changes the tracing end time. Default is a very large number (hopefully past 
    any simulation endtime you will ever use). 
    Example: **trace.tchange(end=33)** to stop tracing at time 33.

  *toTrace*: 

    changes the commands to be traced. Default is 
    *["hold","activate","cancel","reactivate","passivate","request",
    "release","interrupt","waitevent","queueevent",
    "signal","waituntil","put","get","terminated"]*.
    Value must be a list containing
    one or more of those values in the default. Note: "terminated" causes 
    tracing of all process terminations.
    Example: **trace.tchange(toTrace=["hold","activate"])** traces only the 
    *yield hold* and *activate()* statements. 

  *outfile*: 

    redirects the trace out put to a file (default is *sys.stdout*). Value
    must be a file object open for writing.
    Example: **trace.tchange(outfile=open(r"c:\\python25\\bank02trace.txt","w"))**

All these parameters can be combined. 
Example: **trace.tchange(start=45.0,toTrace=["terminated"])** will trace all
process terminations from time 45.0 till the end of the simulation.

The changes become effective at the time **trace.tchange()** is called. This
implies for example that, if the call **trace.tchange(start=50)** is made at time 
100, it has no effect before *now()==100*. 

**treset()**: Resetting the trace to default values
---------------------------------------------------

The trace parameters can be reset to their default values by calling **trace.treset()**.

**trace.tstart()**, **trace.tstop()**: Enabling/disabling the trace
---------------------------------------------------------------------

Calling **trace.tstart()** enables the tracing, and **trace.tstop()**
disables it. Neither call changes any tracing parameters.
 

**trace.ttext()**: Annotating the trace
---------------------------------------

The event-by-event trace output is already very useful in showing the sequence
in which SimPy's quasi-parallel processes are executed.

For documentation, publishing or teaching purposes, it is even more useful
if the trace output can be intermingled with output which not only
shows the command executed, but also contextual information such as 
the values of state variables. If one outputs the reason *why* a specific 
scheduling command is executed, the trace can give a natural language description
of the simulation scenario.

For such in-line annotation, the **trace.ttext(<string>)** method is
available. It provides a string which is output together with the trace of
the next scheduling statement. This string is valid *only* for the scheduling
statement following it.

Example::

    class Bus(Process):
        def __init__(self,name):
            Process.__init__(self,name)

        def operate(self,repairduration=0):
            tripleft = 1000
            while tripleft > 0:
                trace.ttext("Try to go for %s"%tripleft)
                yield hold,self,tripleft
                if self.interrupted():
                    tripleft=self.interruptLeft
                    self.interruptReset()
                    trace.ttext("Start repair taking %s time units"%repairduration)
                    yield hold,self,repairduration
                else:
                    break # no breakdown, ergo bus arrived
            trace.ttext("<%s> has arrived"%self.name)

    class Breakdown(Process):
        def __init__(self,myBus):
            Process.__init__(self,name="Breakdown "+myBus.name)
            self.bus=myBus

        def breakBus(self,interval):

            while True:
                trace.ttext("Breakdown process waiting for %s"%interval)
                yield hold,self,interval
                if self.bus.terminated(): break
                trace.ttext("Breakdown of %s"%self.bus.name)
                self.interrupt(self.bus)
                
    print"\n\n+++test_interrupt"
    initialize()
    b=Bus("Bus 1")
    trace.ttext("Start %s"%b.name)
    activate(b,b.operate(repairduration=20))
    br=Breakdown(b)
    trace.ttext("Start the Breakdown process for %s"%b.name)
    activate(br,br.breakBus(200))
    trace.start=100
    print simulate(until=4000)

    This produces:

    0 activate <Bus 1> at time: 0 prior: 0
    ---- Start Bus 1
    0 activate <Breakdown Bus 1> at time: 0 prior: 0
    ---- Start the Breakdown process for Bus 1
    200 reactivate <Bus 1> time: 200 prior: 0
    200 interrupt by: <Breakdown Bus 1> of: <Bus 1>
    ---- Breakdown of Bus 1
    200 hold <Breakdown Bus 1> delay: 200
    ---- Breakdown process waiting for 200
    200 hold <Bus 1> delay: 20
    ---- Start repair taking 20 time units
    220 hold <Bus 1> delay: 800
    ---- Try to go for 800
    400 reactivate <Bus 1> time: 400 prior: 0
    400 interrupt by: <Breakdown Bus 1> of: <Bus 1>
    ---- Breakdown of Bus 1
    400 hold <Breakdown Bus 1> delay: 200
    ---- Breakdown process waiting for 200
    400 hold <Bus 1> delay: 20
    ---- Start repair taking 20 time units
    420 hold <Bus 1> delay: 620

     . . . . . 

The line starting with "----" is the comment related to the command traced
in the preceding output line.

Nice output of class instances
------------------------------
   
After the import of *SimPy.SimulationTrace*, all instances of classes
*Process* and *Resource* (and all their subclasses) have a nice string
representation like so::

       >>> class Bus(Process):
    ... 	def __init__(self,id):
    ... 		Process.__init__(self,name=id)
    ... 		self.typ="Bus"
    ... 		
    >>> b=Bus("Line 15")
    >>> b
    <Instance of Bus, id 21860960:
         .name=Line 15
         .typ=Bus
    >
    >>> 

This can be handy in statements like **trace.ttext("Status of %s"%b)**.



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70 
   End:

 
 

