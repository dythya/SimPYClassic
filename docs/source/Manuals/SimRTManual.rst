

===============================================
 Simulation with Real Time Synchronization
===============================================

.. highlight:: python
   :linenothreshold: 5

:Authors: - Klaus Muller <Muller@users.sourceforge.net>
          - Tony Vignaux <Vignaux@users.sourceforge.net>
:Release: |release|
:Web-site: https://github.com/SimPyClassic/SimPyClassic
:Python-Version: 2.7+
:Date: December 2011
:Updated: January 2018

.. contents:: Contents
   :depth: 3

This manual describes **SimulationRT**, a SimPy module which supports
synchronizing the execution of simulation models with real (wallclock) time.

Acknowledgement
===============

SimulationRT is based on an idea by Geoff Jarrad of CSIRO (Australia). He
contributed a lot to its development and testing on Windows and Unix.

The code for the adjustment of the execution speed during the simulation run
was contributed by Robert C. Ramsdell.

Synchronizing with wall clock time
===================================

SimulationRT allows synchronizing simulation time and real (wallclock) time.
This capability can be used to implement e.g. interactive game applications or
to demonstrate a model's execution in real time.

It is identical to Simulation, except for the *simulate* function which takes
an additional parameter controlling real-time execution speed.

Here is an example:

.. highlight:: python
   :linenothreshold: 5

.. literalinclude:: SimulationRTprograms/RealTimeFireworks.py

*rel_speed* is the ratio **simulated time/wallclock time**. *rels_speed=1* sets the synchronization so that 1 simulation time unit
is executed in approximately 1 second of wallclock time.
Run under Python 2.6 on a Windows Vista-box (2.3 GHz), this output resulted
over about 17.5 seconds of wallclock time:

.. literalinclude:: SimulationRTprograms/RealTimeFireworks.out
   :language: text

Clearly, the wallclock time does not deviate significantly from the simulation time.

Changing the execution speed during a simulation run
==================================================================

By calling method *rtset* with a parameter, the ratio simulated time to wallclock time
can be changed during a run.

Here is an example:

.. literalinclude:: SimulationRTprograms/variableTimeRatio.py

The program changes the time ratio twice, at simulation times 5 and 10.

When run on a Windows Vista computer under Python 2.7, this results in this output:

.. literalinclude:: SimulationRTprograms/variableTimeRatio.out

Limitations
============
This module works much better under Windows than under Unix or Linux, i.e., it gives
much closer synchronization.
Unfortunately, the handling of time in Python is not platform-independent at all.
Here is a quote from the documentation of the *time* module::

    "clock()
    On Unix, return the current processor time as a floating point number expressed in seconds.
    The precision, and in fact the very definition of the meaning of ``processor time'' , depends
    on that of the C function of the same name, but in any case, this is the function to use for
    benchmarking Python or timing algorithms.

    On Windows, this function returns wall-clock seconds elapsed since the first call to this
    function, as a floating point number, based on the Win32 function QueryPerformanceCounter().
    The resolution is typically better than one microsecond.
    "

Also it is deprecated in 3.3 and up.


The SimulationRT API
======================

Structure
---------
Basically, SimulationStep has the same API as Simulation, but with:

    - a change in the definition of simulate, and
    - an additional method to change execution speed during a simulation
      run.

**simulate**
------------------

Executes the simulation model.

Call:

	**simulate(<optional parameters>)**

Mandatory parameters:
	None.

Optional parameters:
	- **until=0** : the maximum simulation (end) time (positive floating point number; default: 0)
	- **real_time=False** : flag to switch real time synchronization on or off (boolean; default: False, meaning no synchronization)
	- **rel_speed=1** : ratio simulation time over wallclock time; example: *rel_speed=200* executes 200 units of simulation time in about one second (positive floating point number; default: 1, i.e. 1 sec of simulation time is executed in about 1 sec of wallclock time)

Return value:
	Simulation status at exit.

**rtset**
------------------

Changes the ratio simulation time over wall clock time.

Call:

	**rtset(<new ratio>)**

Mandatory parameters:
	None

Optional parameters:
	- **rel_speed=1** : ratio simulation time over wallclock time; example: *rel_speed=200* executes 200 units of simulation time in about one second (positive floating point number; default: 1, i.e. 1 sec of simulation time is executed in about 1 sec of wallclock time)

Return value:
	None


