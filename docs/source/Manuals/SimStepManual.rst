

============================================
SimPy Classic Simulation with Event Stepping
============================================


:Authors: - Klaus Muller <Muller@users.sourceforge.net>
          - Tony Vignaux <Vignaux@users.sourceforge.net>
:Release: |release|
:Web-site: https://github.com/SimPyClassic/SimPyClassic
:Python Version: 2.7+
:Date: December 2011
:Updated: January 2018

.. contents:: Contents
   :depth: 2

This manual describes **SimulationStep**, a SimPy module which supports
stepping through a simulation model event by event.

Introduction
============

SimulationStep can assist with debugging models, interacting with them on
an event-by-event basis, getting event-by-event output from a model (e.g.
for plotting purposes), etc.

SimulationStep is a derivative of the Simulation module. Over and above
the capabilities provided by Simulation, SimulationStep supports stepping
through a simulation model event by event. It caters for:

    - running a simulation model, with calling a user-defined procedure after every event,
    - running a simulation model one event at a time by repeated calls,
    - starting and stopping the event stepping mode under program control.

SimulationStep overview
=======================

Here is a simple program which shows basic event stepping capabilities::

    ## Stepping1.py
    from __future__ import generators
    from SimPy.SimulationStep import *                  # (1)

    def callbackTimeTrace():                            # (2)
        """Prints event times
        """
        print "at time=%s"%now()
            
    class Man(Process):
        def walk(self):
            print "got up"
            yield hold,self,1
            print "got to door"
            yield hold,self,10
            print "got to mail box"
            yield hold,self,10
            print "got home again"
            
    #trace event times
    initialize()
    otto=Man()
    activate(otto,otto.walk())
    startStepping()                                     # (3)
    simulate(callback=callbackTimeTrace,until=100)      # (4)

A trivial simulation model, but with event stepping:

	(1) import the stepping version of Simulation
 	(2) define a procedure which gets called after every event
 	(3) switch into event stepping mode
	(4) run the model with event callback to the procedure defined at (2); ``simulate`` in SimulationStep has an extra named parameter, ``callback``.
    
Running it produces this output::

    got up
    at time=0
    got to door
    at time=1
    got to mail box
    at time=11
    got home again
    at time=21
    at time=21

The callback outputs the simulation time after every event.

Here is another example, the same model, but now with the user getting control back after every 
event::

    ## Stepping2.py
    from __future__ import generators
    from SimPy.SimulationStep import *

    def callbackUserControl():
        """Allows user to control stepping
        """
        a=raw_input("[Time=%s] Select one: End run (e), Continue stepping (s), Run to end (r)= "%now())
        if a=="e":
            stopSimulation()
        elif a=="s":
            return
        else:
            stopStepping()
            
    class Man(Process):
        def walk(self):
            print "got up"
            yield hold,self,1
            print "got to door"
            yield hold,self,10
            print "got to mail box"
            yield hold,self,10
            print "got home again"
    #allow user control
    initialize()
    otto=Man()
    activate(otto,otto.walk())
    startStepping()
    simulate(callback=callbackUserControl,until=100)

Its interactive output looks like this::

    got up
    [Time=0] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    got to door
    [Time=1] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    got to mail box
    [Time=11] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    got home again
    [Time=21] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    [Time=21] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    
or this (the user stopped stepping mode at time=1)::

    got up
    [Time=0] Select one: End run (e), Continue stepping (s), Run to end (r)= s
    got to door
    [Time=1] Select one: End run (e), Continue stepping (s), Run to end (r)= r
    got to mail box
    got home again

If one wants to run a tested/debugged model full speed, i.e. without stepping,
one can write a program as follows::

    ## Stepping2Fast.py
    from __future__ import generators
    if __debug__:
	    from SimPy.SimulationStep import *
    else:
	    from SimPy.Simulation import *

    def callbackUserControl():
        """Allows user to control stepping
        """
        if __debug__:
		    a=raw_input("[Time=%s] Select one: End run (e), Continue stepping (s),\
                         Run to end (r)= "%now())
		    if a=="e":
		        stopSimulation()
		    elif a=="s":
		        return
		    else:
		        stopStepping()
            
    class Man(Process):
        def walk(self):
            print "got up"
            yield hold,self,1
            print "got to door"
            yield hold,self,10
            print "got to mail box"
            yield hold,self,10
            print "got home again"
    #allow user control if debugging
    initialize()
    otto=Man()
    activate(otto,otto.walk())
    if __debug__:
	    startStepping()
	    simulate(callback=callbackUserControl,until=100)
    else:
	    simulate(until=100)
	    
If one runs this with the Python command line option '-O', any 
statement starting with ``if __debug__:`` is ignored/skipped by the
Python interpreter.
    
The SimulationStep API
======================

Structure
---------
Basically, SimulationStep has the same API as Simulation, but with
the following additions and changes::

    def startStepping()         **new**
    def stopStepping()          **new**
    def simulate()              **changed**
    def simulateStep()          **new**

**startStepping**
------------------

Starts the event-stepping.

Call:

	**startStepping()**

Mandatory parameters:
	None.

Optional parameters:
	None

Return value:
	None.

**stopStepping**
------------------
Stops event-stepping.

Call:
	**stopStepping()**
	
Mandatory parameters:
	None
	
Optional parameters:
	None
	
Return value:
	None
		
**simulate**
----------------
Runs a simulation with callback to a user-defined function after each event, if stepping is turned on.
By default, stepping is switched off.

Call:
	**simulate(callback=<proc>,until=<endtime>)**
	
Mandatory parameters:
	None
	
Optional parameters:
	- **until = 0**: the simulation time until which the simulation is to run (positive floating point or integer number)
	- **callback = lambda:None**: the function to be called after every event (function reference)
	
Return value:
	The simulation status at exit (string)
	
**simulateStep**
----------------
Runs a simulation for one event, with (optional) callback to a user-defined function 
after the event, if stepping is turned on. By default, stepping is switched off.
Thus, to execute the model to completion, *simulateStep* must be called repeatedly.

**Note: it is not yet clear to the developers whether this part of the API offers any advantages
or capabilities over and above the *simulate* function. The survival of this function
in future versions depends on the feedback from the user community.**

Call:
	**simulateStep(callback=<proc>,until=<endtime>)**
	
Mandatory parameters:
	None
	
Optional parameters:
	- **until = 0**: the simulation time until which the simulation is to run (positive floating point or integer number)
	- **callback = lambda:None**: the function to be called after every event (function reference)
	
Return value:
	The tuple **(simulation status at exit (string),<resumability flag>)**. 
	<resumability flag> can have one of two string values: **"resumable"** if there
	are more events to be executed, and **"notResumable"** if all events have been exhausted
	or an error has occurred. *simulateStep* should normally only be called if 
	"resumable" is returned.
	


