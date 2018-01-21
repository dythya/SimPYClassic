==============================================
|simpylogo| LIST OF MODELS using SimPy Classic
==============================================

:SimPy version: 2.3
:Web-site: https://github.com/SimPyClassic/SimPyClassic
:Python-Version: 2.7 or later and 3.x except for the GUI ones

These models are examples of SimPy use written by several authors and usually
developed for other purposes, such as teaching and consulting. They are in a
variety of styles.

Most models are given in two versions, one with the procedural SimPy API
and the other (identified by an "_OO" appended to the program name) with
the Object Oriented API introduced in SimPy 2.0.

All of these examples come with SimPY in the docs/examples directory.

NOTE: The SimGUI examples do not work for Python 3 as the SimGUI
library has not been ported to Python 3.

New Program Structure
+++++++++++++++++++++++++

M/M/C Queue: MCC.py, MCC_OO.py
==============================

M/M/C (multiple server queue model). This demonstrates both the multiple
capacity Resource class and the observe method of the Monitor class. Random
arrivals, exponential service-times. (TV)

Jobs arrive at random into a c-server queue with exponential service-time
distribution. Simulate to determine the average number in the system and the
average time jobs spend in the system.

.. literalinclude:: ../../../examples/MMC.py
.. literalinclude:: ../../../examples/program_output/MMC.out

.. literalinclude:: ../../../examples/MMC_OO.py
.. literalinclude:: ../../../examples/program_output/MMC.out


BCC: bcc.py, bcc_OO.py
======================

Determine the probability of rejection of random arrivals to a 2-server system
with different service-time distributions. No queues allowed, blocked
customers are rejected (BCC). Distributions are Erlang, exponential, and
hyperexponential. The theoretical probability is also calculated.  (TV)

.. literalinclude:: ../../../examples/bcc.py
.. literalinclude:: ../../../examples/program_output/bcc.out

.. literalinclude:: ../../../examples/bcc_OO.py
.. literalinclude:: ../../../examples/program_output/bcc.out


callCenter.py, callCenter_OO.py
===============================

Scenario: A call center runs around the clock. It has a number of agents
online with different skills.  Calls by clients with different questions
arrive at an expected rate of callrate per minute (expo. distribution). An
agent only deals with clients with questions in his competence areas. The
number of agents online and their skills remain constant -- when an agent goes
offline, he is replaced by one with the same skills.  The expected service
time tService[i] per question follows an exponential distribution.  Clients
are impatient and renege if they don't get service within time tImpatience.

The model returns the frequency distribution of client waiting times, the
percentage of reneging clients, and the load on the agents.  This model
demonstrates the use of yield get with a filter function. (KGM)

.. literalinclude:: ../../../examples/callCenter.py
.. literalinclude:: ../../../examples/program_output/callCenter.out

Object Oriented version.

.. literalinclude:: ../../../examples/callCenter_OO.py
.. literalinclude:: ../../../examples/program_output/callCenter.out


cellphone.py, cellphone_OO.py
=============================

Simulate the operation of a BCC cellphone system. Calls arrive at random to a
cellphone hub with a fixed number of channels. Service times are assumed
exponential. The objective is to determine the statistics of busy periods in
the operation of a BCC cellphone system.

The program simulates the operation for 10 observation periods and measures
the mean and variance of the total time blocked, and the number of times
blocking occurred in each hour. An observational gap occurs between the
observation periods to make each one's measurement independent.  (TV)

.. literalinclude:: ../../../examples/cellphone.py
.. literalinclude:: ../../../examples/program_output/cellphone.out

Object orientated

.. literalinclude:: ../../../examples/cellphone_OO.py
.. literalinclude:: ../../../examples/program_output/cellphone.out


Computer CPU: centralserver.py, centralserver_OO.py
===================================================

A primitive central-server model with a single CPU and a single disk. A fixed
number of users send "tasks" to the system which are processed and sent back
to the user who then thinks for a time before sending a task back. Service
times are exponential. This system can be solved analytically. (TV)

The user of each terminal thinks for a time (exponential, mean 100.0 sec)
and then submits a task to the CPU with a service time (exponential, mean 1.0
sec). The user then remains idle until the task completes service and returns
to him or her. The arriving tasks form a single FCFS queue in front of the
CPU.

Upon leaving the CPU a task is either finished (probability 0.20) and returns
to its user to begin another think time, or requires data from a disk
drive (probability 0.8). If a task requires access to the disk, it joins a
FCFS queue before service (service time at the disk, exponential, mean 1.39
sec). When finished with the disk, a task returns to the CPU queue again for
another compute time (exp, mean 1.$ sec).

The objective is to measure the throughput of the CPU (tasks per second)

.. literalinclude:: ../../../examples/centralserver.py
.. literalinclude:: ../../../examples/program_output/centralserver.out

OO version

.. literalinclude:: ../../../examples/centralserver_OO.py
.. literalinclude:: ../../../examples/program_output/centralserver.out


Messages on a Jackson Network: jacksonnetwork.py, jacksonnetwork_OO.py
======================================================================

A Jackson network with 3 nodes, exponential service times and probability
switching. The simulation measures the delay for jobs moving through the
system.  (TV)

Messages arrive randomly at rate 1.5 per second at a communication network
with 3 nodes (computers). Each computer (node) can queue messages.

.. literalinclude:: ../../../examples/jacksonnetwork.py
.. literalinclude:: ../../../examples/program_output/jacksonnetwork.out

OO version

.. literalinclude:: ../../../examples/jacksonnetwork_OO.py
.. literalinclude:: ../../../examples/program_output/jacksonnetwork.out


Miscellaneous Models
+++++++++++++++++++++


Bank Customers who can renege: bank08renege.py, bank08renege_OO.py
==================================================================

(Note currently does not run under Python 3)

Use of reneging (compound ``yield request``) based on ``bank08.py`` of the
tutorial TheBank. Customers leave if they lose patience with waiting.

.. literalinclude:: ../../../examples/bank08renege.py
.. literalinclude:: ../../../examples/program_output/bank08renege.out

OO version

.. literalinclude:: ../../../examples/bank08renege_OO.py
.. literalinclude:: ../../../examples/program_output/bank08renege.out


Carwash: Carwash.py, Carwash_OO.py
==================================

Using a Store object for implementing master/slave cooperation between
processes.  Scenario is a carwash installation with multiple machines. Two
model implementations are shown, one with the carwash as master in the
cooperation, and the other with the car as master.

.. literalinclude:: ../../../examples/Carwash.py
.. literalinclude:: ../../../examples/program_output/Carwash.out

Here is the OO version:

.. literalinclude:: ../../../examples/Carwash_OO.py
.. literalinclude:: ../../../examples/program_output/Carwash.out


Game of Life: CellularAutomata.py
=================================

A two-dimensional cellular automaton. Does the game of Life. (KGM)

.. literalinclude:: ../../../examples/CellularAutomata.py
.. literalinclude:: ../../../examples/program_output/CellularAutomata.out


SimPy's event signalling synchronisation constructs: demoSimPyEvents.py
=======================================================================

Demo of the event signalling constructs. Three small simulations are included:
Pavlov's drooling dogs, an activity simulation where a job is completed after
a number of parallel activities, and the simulation of a US-style 4-way stop
intersection.

.. literalinclude:: ../../../examples/demoSimPyEvents.py
.. literalinclude:: ../../../examples/program_output/demoSimPyEvents.out


Find the Shortest Path: shortestPath_SimPy.py, shortestPath_SimPy_OO.py
=======================================================================

A fun example of using SimPy for non-queuing work. It simulates a searcher
through a graph, seeking the shortest path. (KGM)

.. literalinclude:: ../../../examples/shortestPath_SimPy.py
.. literalinclude:: ../../../examples/program_output/shortestPath_SimPy.out

Here is the OO version:

.. literalinclude:: ../../../examples/shortestPath_SimPy_OO.py
.. literalinclude:: ../../../examples/program_output/shortestPath_SimPy.out


Machine Shop Model: Machineshop.py, Machineshop_OO.py
=====================================================

A workshop has n identical machines. A stream of jobs (enough to keep the
machines busy) arrives. Each machine breaks down periodically. Repairs are
carried out by one repairman. The repairman has other, less important tasks to
perform, too. Once he starts one of those, he completes it before starting
with the machine repair. The workshop works continuously.

This is an example of the use of the ``interrupt()`` method. (KGM)

.. literalinclude:: ../../../examples/Machineshop.py
.. literalinclude:: ../../../examples/program_output/Machineshop.out

Here is the OO version:

.. literalinclude:: ../../../examples/Machineshop_OO.py
.. literalinclude:: ../../../examples/program_output/Machineshop.out

Supermarket: Market.py, Market_OO.py
====================================

A supermarket checkout with multiple counters and extended Monitor objects.
Written and analysed by David Mertz in an article for developerWorks (). (MM)

.. literalinclude:: ../../../examples/Market.py
.. literalinclude:: ../../../examples/program_output/Market.out

Here is the OO version:

.. literalinclude:: ../../../examples/Market_OO.py
.. literalinclude:: ../../../examples/program_output/Market.out


Movie Theatre Ticket Counter: Movie_renege.py, Movie_renege_OO.py
=================================================================

Use of reneging (compound ``yield request``) constructs for reneging at
occurrence of an event. Scenario is a movie ticket counter with a limited
number of tickets for three movies (next show only). When a movie is sold out,
all people waiting to buy ticket for that movie renege (leave queue).

.. literalinclude:: ../../../examples/Movie_renege.py
.. literalinclude:: ../../../examples/program_output/Movie_renege.out

Here is the OO version:

.. literalinclude:: ../../../examples/Movie_renege_OO.py
.. literalinclude:: ../../../examples/program_output/Movie_renege.out



Workers Sharing Tools, waitUntil: needResources.py, needResources_OO.py
=======================================================================

Demo of ``waitUntil`` capability. It simulates three workers each requiring a
set of tools to do their jobs. Tools are shared, scarce resources for which
they compete.

.. literalinclude:: ../../../examples/needResources.py
.. literalinclude:: ../../../examples/program_output/needResources.out

Here is the OO version:

.. literalinclude:: ../../../examples/needResources_OO.py
.. literalinclude:: ../../../examples/program_output/needResources.out


Widget Factory: SimPy_worker_extend.py, SimPy_worker_extend_OO.py
=================================================================

Factory making widgets with queues for machines. (MM)

.. literalinclude:: ../../../examples/SimPy_worker_extend.py
.. literalinclude:: ../../../examples/program_output/SimPy_worker_extend.out

Here is the OO version:

.. literalinclude:: ../../../examples/SimPy_worker_extend_OO.py
.. literalinclude:: ../../../examples/program_output/SimPy_worker_extend.out


Widget Packing Machine: WidgetPacking.py, WidgetPacking_OO.py
=============================================================

Using buffers for producer/consumer scenarios. Scenario is a group of widget
producing machines and a widget packer, synchronised via a buffer. Two models
are shown: the first uses a Level for buffering non-distinguishable items
(widgets), and the second a Store for distinguishable items (widgets of
different weight).

.. literalinclude:: ../../../examples/WidgetPacking.py
.. literalinclude:: ../../../examples/program_output/WidgetPacking.out

Here is the OO version:

.. literalinclude:: ../../../examples/WidgetPacking_OO.py
.. literalinclude:: ../../../examples/program_output/WidgetPacking.out


GUI Input
++++++++++

The GUI examples do not run under Python 3.x, as only the core
SimPy libraries were ported.


Fireworks using SimGUI: GUIdemo.py, GUIdemo_OO.py
=================================================

A firework show. This is a very basic model, demonstrating the ease
of interfacing to SimGUI.

.. literalinclude:: ../../../examples/GUIdemo.py

Here is the OO version:

.. literalinclude:: ../../../examples/GUIdemo_OO.py


Bank Customers using SimGUI: bank11GUI.py, bank11GUI_OO.py
==========================================================

Simulation with customers arriving at random to a bank with two counters. This
is a modification of the bank11 simulation using SimGUI to run the simulation.

.. literalinclude:: ../../../examples/bank11GUI.py

Here is the OO version:

.. literalinclude:: ../../../examples/bank11GUI_OO.py


Bank Customers using SimulationStep: SimGUIStep.py
==================================================

(broken for python 2.x global name 'simulateStep' is not defined)

Another modification of the bank11 simulation this time showing the ability to
step between events.

.. literalinclude:: ../../../examples/SimGUIStep.py


Plot
++++

Patisserie Francaise bakery: bakery.py, bakery_OO.py
====================================================

The Patisserie Francaise bakery has three ovens baking their renowned
baguettes for retail and restaurant customers. They start baking one
hour before the shop opens and stop at closing time.

They bake batches of 40 breads at a time,
taking 25..30 minutes (uniformly distributed) per batch. Retail customers
arrive at a rate of 40 per hour (exponentially distributed). They buy
1, 2 or 3 baguettes with equal probability. Restaurant buyers arrive
at a rate of 4 per hour (exponentially dist.). They buy 20,40 or 60
baguettes with equal probability.

The simulation answers the following questions:

a) What is the mean waiting time for retail and restaurant
buyers?

b) What is their maximum waiting time?

c) What percentage of customer has to wait longer than 15 minutes?

SimPy.SimPlot is used to graph the number of baguettes over time. (KGM)

.. literalinclude:: ../../../examples/bakery.py

Here is the OO version:

.. literalinclude:: ../../../examples/bakery_OO.py


Bank Customers Demos SimPlot: bank11Plot.py
===========================================

A modification of the bank11 simulation with graphical output. It plots
service and waiting times.

.. literalinclude:: ../../../examples/bank11Plot.py

Debugger
+++++++++

Stepping thru Simpulation Events: SimpleDebugger.py
===================================================

A utility module for stepping through the events of a simulation
under user control, using SimulationTrace.

.. literalinclude:: ../../../examples/SimpleDebugger.py

Here is the OO version:

.. literalinclude:: ../../../examples/SimpleDebugger_OO.py




:Authors:  - Tony Vignaux <Vignaux@users.sourceforge.net>,
           - Klaus Muller <Muller@users.sourceforge.net>
           - Karen Turner (updated 2012)
           - Steven Kennedy (updated for Python 3 2012)
:Created: 2002-December
:Date: 2012-April


.. |simpylogo| image:: ../../_static/sm_SimPy_Logo.png


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
