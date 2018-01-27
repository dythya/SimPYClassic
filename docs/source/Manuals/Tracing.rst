.. highlight:: python
   :linenothreshold: 5 
 
=====================================
SimPy Classic Simulation with Tracing
=====================================

:Authors: - Klaus Muller <Muller@users.sourceforge.net>
:Release: |release|
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

Here is an example (bank02.py from the Bank Tutorial):

.. literalinclude:: programs/tracing_bank02.py


This program produces the following output:

.. literalinclude:: programs/tracing_bank02.out


Another example:

.. literalinclude:: programs/tracing_bank09.py


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
 
And here is an example showing the trace output for compound yield statements:

.. literalinclude:: programs/tracing_compound_yield.py


It produces this output:

.. literalinclude:: programs/tracing_compound_yield.out


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

Example:

.. literalinclude:: programs/tracing_annotation.py


This produces::

    +++test_interrupt
    0 activate <Bus 1> at time: 0 prior: False
    ---- Start Bus 1
    0 activate <Breakdown Bus 1> at time: 0 prior: False
    ---- Start the Breakdown process for Bus 1
    200 reactivate <Bus 1> time: 200 prior: False
    200 interrupt by: <Breakdown Bus 1> of: <Bus 1>
    ---- Breakdown of Bus 1
    200 hold <Breakdown Bus 1> delay: 200
    ---- Breakdown process waiting for 200
    200 hold <Bus 1> delay: 20
    ---- Start repair taking 20 time units
    220 hold <Bus 1> delay: 800
    ---- Try to go for 800
    400 reactivate <Bus 1> time: 400 prior: False
    400 interrupt by: <Breakdown Bus 1> of: <Bus 1>
    ---- Breakdown of Bus 1
    400 hold <Breakdown Bus 1> delay: 200

     . . . . . 

The line starting with "----" is the comment related to the command traced
in the preceding output line.

Nice output of class instances
------------------------------
   
After the import of *SimPy.SimulationTrace*, all instances of classes
*Process* and *Resource* (and all their subclasses) have a nice string
representation like so::

       >>> class Bus(SimulationProcess):
    ... 	def __init__(self, id):
    ... 		Simulation.Process.__init__(self, name=id)
    ... 		self.typ = "Bus"
    ... 		
    >>> b = Bus("Line 15")
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
