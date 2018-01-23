.. Tutorials

.. .. image:: images/sm_SimPy_Logo.png
      :align: left

===============================================================================
The Bank Tutorial (OO API) Part 2: More  examples of SimPy Classic Simulation
===============================================================================

:Authors: G A Vignaux, K G Muller
:Date:  2010 April
:Release: |release|
:Python-Version: 2.7 and later

.. ---------------------------------------------------
..  TO DO
    add example of using SimpyTrace
    Reneging due to an event
    Interrupts - YES
    SimEvents?

.. ---------------------------------------------------



.. highlight:: python
   :linenothreshold: 5


.. .. contents:: Table Of Contents
      :depth: 2

..
    1  Introduction
    2  Priority Customers
      2.1  Priority Customers without preemption
      2.2  Priority Customers with preemption
    3  Balking and Reneging Customers
      3.1  Balking Customers
      3.2  Reneging (or abandoning) Customers
    4  Processes
      4.1  Interrupting a Process.
      4.2  ``waituntil`` the Bank door opens
      4.3  Wait for the doorman to give a signal: ``waitevent``
    5  Monitors
      5.1  Plotting a Histogram of Monitor results
      5.2  Monitoring a Resource
      5.3  Plotting from  Resource Monitors
    6  Acknowledgements
    7  References



.. .. sectnum::
      :depth: 2

.. raw:: latex

   \newpage

OO API Bank Tutorial version
----------------------------

This manual is a rework of the *Bank Tutorial Part 2*.
Its goal is to show how the simple tutorial models can
be written in the advanced OO API.

.. note:: To contrast the OO API with the procedural
   SimPy API, the reader should read both "Bank Tutorial Part 2"
   documents side by side.

Introduction
-------------------------------------

The first Bank tutorial, The Bank, developed and explained a
series of simulation models of a simple bank using SimPy_. In various
models, customers arrived randomly, queued up to be served at one or
several counters, modelled using the Resource class, and, in one case,
could choose the shortest among several queues. It demonstrated the
use of the Monitor class to record delays and showed how a ``model()``
mainline for the simulation was convenient to execute replications of
simulation runs.

In this extension to The Bank, I provide more examples of SimPy
facilities for which there was no room and for some that were
developed since it was written. These facilities are generally more
complicated than those introduced before. They include queueing with priority,
possibly with preemption, reneging, plotting, interrupting, waiting
until a condition occurs (``waituntil``) and waiting for events to
occur.

Starting with SimPy 2.0 an object-oriented programmer's interface was
added to the package and it is this version that is described here.
It is quite compatible with the procedural approach. The object-oriented
interface, however, can support the process of developing and extending a
simulation model better than the procedural approach.

.. _SimPy: https://github.com/SimPyClassic/SimPyClassic

The programs are available without line numbers and ready to go, in
directory ``bankprograms``. Some have trace statements for
demonstration purposes, others produce graphical output to the
screen. Let me encourage you to run them and modify them for yourself.

SimPy itself can be obtained from:
https://github.com/SimPyClassic/SimPyClassic.  It is compatible with
Python version 2.7 onwards.  The examples in this documentation run
with SimPy version 1.5 and later.

This tutorial should be read with the SimPy Manual and CheatsheetOO at
your side for reference.


.. raw:: latex

   \newpage

Priority Customers
-------------------

In many situations there is a system of priority service. Those
customers with high priority are served first, those with low priority
must wait. In some cases, preemptive priority will even allow a
high-priority customer to interrupt the service of one with a lower
priority.

SimPy implements priority requests with an extra numerical priority
argument in the ``yield request`` command, higher values meaning
higher priority. For this to operate, the requested Resource must have
been defined with ``qType=PriorityQ``. This require importing the ``PriorityQ``
class from ``SimPy.Simulation``.

Priority Customers without preemption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. index:: priority

In the first example, we modify the program with random arrivals, one
counter, and a fixed service time (like ``bank07.py`` in The Bank
tutorial) to process a high priority customer. Warning: the ``seedVal``
value has been changed to ``98989`` to make the story more exciting.

The modifications are to the definition of the ``counter`` where we
change the ``qType`` and to the ``yield request`` command in the
``visit`` PEM of the customer. We also need to provide each customer
with a priority. Since the default is ``priority=0`` this is easy for
most of them.

To observe the priority in action, while all other customers have the
default priority of 0, in lines 43 to 44 we create and
activate one special customer, ``Guido``, with priority 100 who
arrives at time ``23.0`` (line 44). This is to ensure that he arrives
after ``Customer03``.

The ``visit`` customer method has a new parameter, ``P=0`` (line
20) which allows us to set the customer priority.

In lines 39 to 40 the ``BankModel`` 's resource attribute ``k``
named ``Counter`` is defined with ``qType=PriorityQ`` so
that we can request it with priority (line 25) using the
statement ``yield request,self,self.sim.k,P``

In line 23 we print out the number of customers waiting when each
customer arrives.


.. literalinclude:: bankprograms_OO/bank20_OO.py

The resulting output is as follows. The number of customers in the
queue just as each arrives is displayed in the trace. That count does
not include any customer in service.

.. literalinclude:: bankprograms/bank20.out

.. index:: random arrival, bank20_OO

Reading carefully one can see that when ``Guido`` arrives
``Customer00`` has been served and left at ``12.000``), ``Customer01``
is in service and two (customers 02 and 03) are queueing. ``Guido``
has priority over those waiting and is served before them at
``24.000``. When ``Guido`` leaves at ``36.000``, ``Customer02`` starts
service.


Priority Customers with preemption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. index::
   single: priority: preemption
   single: bank23_OO

Now we allow ``Guido`` to have preemptive priority. He will displace
any customer in service when he arrives. That customer will resume
when ``Guido`` finishes (unless higher priority customers
intervene). It requires only a change to one line of the program,
adding the argument, ``preemptable=True`` to the ``Resource``
statement in line 40.

.. literalinclude:: bankprograms_OO/bank23_OO.py


Though ``Guido`` arrives at the same time, ``23.000``, he no longer
has to wait and immediately goes into service, displacing the
incumbent, ``Customer01``. That customer had already completed
``23.000-12.000 = 11.000`` minutes of his service. When ``Guido``
finishes at ``35.000``, ``Customer01`` resumes service and takes
``36.000-35.000 = 1.000`` minutes to finish. His total service time
is the  same as before (``12.000`` minutes).

.. literalinclude:: bankprograms/bank23.out



.. raw:: latex

   \newpage

Balking and Reneging Customers
--------------------------------

.. index:: balking, reneging, abandoning (reneging)


Balking occurs when a customer refuses to join a queue if it is too
long. Reneging (or, better, abandonment) occurs if an impatient
customer gives up while still waiting and before being served.

Balking Customers
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   single: balking
   single: bank24_OO

Another term for a system with balking customers is one where "blocked
customers" are "cleared", termed by engineers a BCC system. This is
very convenient analytically in queueing theory and formulae developed
using this assumption are used extensively for planning communication
systems. The easiest case is when no queueing is allowed.

As an example let us investigate a BCC system with a single server but
the waiting space is limited. We will estimate the rate of balking
when the maximum number in the queue is set to 1. On arrival into the
system the customer must first check to see if there is room. We will
need the number of customers in the system or waiting. We could keep a
count, incrementing when a customer joins the queue or, since we have
a Resource, use the length of the Resource's ``waitQ``. Choosing the
latter we test (on line 23). If there is not enough room, we
balk, incrementing a class variable ``Customer.numBalking`` at line
32 to get the total number balking during the run.


.. literalinclude:: bankprograms_OO/bank24_OO.py


The resulting output for a run of this program showing balking
occurring is given below:

.. literalinclude:: bankprograms/bank24.out


When ``Customer02`` arrives, numbers 00 is already in service and 01
is waiting. There is no room so 02 balks. By the vagaries of
exponential random numbers, 00 takes a very long time to serve (55.0607
minutes) so the first one to find room is number 07 at 73.0765.


Reneging (or abandoning) Customers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Often in practice an impatient customer will leave the queue before
being served. SimPy can model this *reneging* behaviour using a
*compound yield statement*. In such a statement there are two
yield clauses. An example is::

    yield (request,self,counter),(hold,self,maxWaitTime)

The first tuple of this statement is the usual ``yield request``,
asking for a unit of ``counter`` Resource. The process will either get
the unit immediately or be queued by the Resource. The second tuple is
a reneging clause which has the same syntax as a ``yield hold``. The
requesting process will renege if the wait exceeds ``maxWaitTime``.

There is a complication, though. The requesting PEM must discover what
actually happened. Did the process get the resource or did it
renege? This involves a *mandatory* test of ``self.acquired(``\
*resource*\
``)``. In our example, this test is in line 26.

.. literalinclude:: bankprograms_OO/bank21_OO.py



.. literalinclude:: bankprograms/bank21.out


``Customer01`` arrives after 00 but has only 12 minutes
patience. After that time in the queue (at time 14.166) he abandons
the queue to leave 02 to take his place. 03 also abandons. 04 finds an
empty system and takes the server without having to wait.

.. ==================================================================

.. raw:: latex

   \newpage

Processes
---------------------

In some simulations it is valuable for one SimPy Process to interrupt
another. This can only be done when the *victim* is "active"; that is
when it has an event scheduled for it. It must be executing a ``yield
hold`` statement.

A process waiting for a resource (after a ``yield request``
statement) is passive and cannot be interrupted by another. Instead
the ``yield waituntil`` and ``yield waitevent`` facilities have been
introduced to allow processes to wait for conditions set by other
processes.

Interrupting a Process.
~~~~~~~~~~~~~~~~~~~~~~~~~~

``Klaus`` goes into the bank to talk to the manager. For clarity we
ignore the counters and other customers. During his conversation his
cellphone rings. When he finishes the call he continues the
conversation.

In this example, ``call`` is an object of the ``Call`` Process class
whose only purpose is to make the cellphone ring after a delay,
``timeOfCall``, an argument to its ``ring`` PEM (line 26).

``klaus``, a ``Customer``, is interrupted by the call (line 29).
He is in the middle of a ``yield hold`` (line 12). When he exits
from that command it is as if he went into a trance when talking to
the bank manager. He suddenly wakes up and must check (line 13)
to see whether has finished his conversation (if there was no call) or
has been interrupted.

If ``self.interrupted()`` is ``False`` he was not interrupted and
leaves the bank (line 21) normally. If it is ``True``, he was
interrupted by the call, remembers how much conversation he has left
(line 14), resets the interrupt (line 15) and then deals
with the call. When he finishes (line 19) he can resume the
conversation, with, now we assume, a thoroughly irritated bank manager
v(line 20).


.. literalinclude:: bankprograms_OO/bank22_OO.py


.. literalinclude:: bankprograms/bank22.out
   :language: text


As this has no random numbers the results are reasonably clear: the
interrupting call occurs at 9.0. It takes ``klaus`` 3 minutes to
listen to the message and he resumes the conversation with the bank
manager at 12.0. His total time of conversation is 9.0 + 11.0 = 20.0
minutes as it would have been if the interrupt had not occurred.


``waituntil`` the Bank door opens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customers arrive at random, some of them getting to the bank before
the door is opened by a doorman. They wait for the door to be opened
and then rush in and queue to be served. The door is modeled by an
attribute ``door`` of ``BankModel``.

This model uses the ``waituntil`` yield command. In the program listing
the door is initially closed (line 58) and a method to test if
it is open is defined at line 54.

The ``Doorman`` class is defined starting at line 7 and the single
``doorman`` is created and activated at at lines 59 and 60. The
doorman waits for an average 10 minutes (line 11) and then
opens the door.

The ``Customer`` class is defined at 24 and a new customer prints out
``Here I am`` on arrival. If the door is still closed, he adds ``but
the door is shut`` and settles down to wait (line 35), using the
``yield waituntil`` command. When the door is opened by the doorman the
``dooropen`` state is changed and the customer (and all others waiting
for the door) proceed. A customer arriving when the door is open will
not be delayed.


.. literalinclude:: bankprograms_OO/bank14_OO.py


An output run for this programs shows how the first three customers
have to wait until the door is opened.

.. literalinclude:: bankprograms/bank14.out
   :language: text


Wait for the doorman to give a signal: ``waitevent``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customers arrive at random, some of them getting to the bank before
the door is open. This is controlled by an automatic machine called
the doorman which opens the door only at intervals of 30 minutes (it
is a very secure bank). The customers wait for the door to be opened
and all those waiting enter and proceed to the counter. The door is
closed behind them.

This model uses the ``yield waitevent`` command which requires a
``SimEvent`` attribute for ``BankModel`` to be defined (line 56).
The ``Doorman`` class is defined
at line 7 and the ``doorman`` is created and activated at at labels
56 and 57. The doorman waits for a fixed time (label
12) and then tells the customers that the door is open. This is
achieved on line 13 by signalling the ``dooropen`` event.

The ``Customer`` class is defined at 24 and in its PEM, when a
customer arrives, he prints out ``Here I am``. If the door is still
closed, he adds `"but the door is shut`` and settles down to wait for
the door to be opened using the ``yield waitevent`` command (line
34). When the door is opened by the doorman (that is, he sends
the ``dooropen.signal()`` the customer and any others waiting may
proceed.


.. literalinclude:: bankprograms_OO/bank13_OO.py


An output run for this programs shows how the first three customers
have to wait until the door is opened.

.. literalinclude:: bankprograms/bank13.out
   :language: text


.. ==================================================================

.. raw:: latex

   \newpage


Monitors
-------------

Monitors (and Tallys) are used to track and record values in a
simulation. They store a list of [time,value] pairs, one pair being
added whenever the ``observe`` method is called.  A particularly
useful characteristic is that they continue to exist after the
simulation has been completed. Thus further analysis of the results
can be carried out.


Monitors have a set of simple statistical methods such as ``mean`` and
``var`` to calculate the average and variance of the observed values
-- useful in estimating the mean delay, for example.

They also have the ``timeAverage`` method that calculates the
time-weighted average of the recorded values. It determines the total
area under the time~value graph and divides by the total time. This is
useful for estimating the average number of customers in the bank, for
example.  There is an *important caveat* in using this method. To
estimate the correct time average you must certainly ``observe`` the
value (say the number of customers in the system) whenever it changes
(as well as at any other time you wish) but, and this is important,
observing the *new* value. The *old* value was recorded earlier. In
practice this means that if we wish to observe a changing value,
``n``, using the Monitor, ``Mon``, we must keep to the the following
pattern::

       n = n+1
       Mon.observe(n,self.sim.now())

Thus you make the change (not only increases) and *then* observe the new
value. Of course the simulation time ``now()`` has not changed between
the two statements.



Plotting a Histogram of Monitor results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Monitor can construct a histogram from its data using the
``histogram`` method. In this model we monitor the time in the system
for the customers. This is calculated for each customer in line
29, using the arrival time saved in line 19. We create the
Monitor attribute of ``BankModel``, ``Mon``, at line 39 and the times
are ``observed`` at line 30.

The histogram is constructed from the Monitor, after the simulation
has finished, at line 58. The SimPy SimPlot package allows
simple plotting of results from simulations.  Here we use the SimPlot
``plotHistogram`` method. The plotting routines appear in lines
60-64. The ``plotHistogram`` call is in line 61.

.. literalinclude:: bankprograms_OO/bank17_OO.py




Monitoring a Resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now consider observing the number of customers waiting or executing in
a Resource. Because of the need to ``observe`` the value after the
change but at the same simulation instant, it is impossible to use the
length of the Resource's ``waitQ`` directly with a Monitor defined
outside the Resource. Instead Resources can be set up with built-in
Monitors.

Here is an example using a Monitored Resource. We intend to observe
the average number waiting and active in the ``counter``
resource. ``counter`` is defined at line 35 as a ``BankModel`` attribute
and we have set
``monitored=True``. This establishes two Monitors: ``waitMon``, to
record changes in the numbers waiting and ``actMon`` to record changes
in the numbers active in the ``counter``. We need make no further
change to the operation of the program as monitoring is then
automatic.  No ``observe`` calls are necessary.

After completion of the ``run`` method, we calculate the
``timeAverage`` of both ``waitMon`` and ``actMon`` (lines 53-54).
These can then be printed at the end of the program (line 55).

.. literalinclude:: bankprograms_OO/bank15_OO.py




Plotting from  Resource Monitors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like all Monitors, ``waitMon`` and ``actMon`` in a monitored Resource
contain information that enables us to graph the output. Alternative
plotting packages can be used; here we use the simple ``SimPy.SimPlot``
package just to graph the number of customers waiting for the
counter. The program is a simple modification of the one that uses a
monitored Resource.

The SimPlot package is imported at line 3. No major changes are
made to the main part of the program except that I commented out the
print statements. The changes occur in the ``run`` method from lines
38 to 39. The simulation now generates and processes 20
customers (line 39). The Monitors of the ``counter`` Resource attribute
still exist when the simulation has terminated.

The additional plotting actions take place in lines 54 to
57. Line 55-56 construct a step plot and graphs the
number in the waiting queue as a function of time. ``waitMon`` is
primarily a list of *[time,value]* pairs which the ``plotStep`` method
of the SimPlot object, ``plt`` uses without change. On running the
program the graph is plotted; the user has to terminate the plotting
``mainloop`` on the screen.


.. literalinclude:: bankprograms_OO/bank16_OO.py




.. Some of the following links need changing

.. _`SimPy`: https://github.com/SimPyClassic/SimPyClassic
.. _Python: https://www.python.org
.. _`Python web site`: https://www.python.org



Acknowledgements
------------------------------

I thank Klaus Muller, Bob Helmbold, Mukhlis Matti and the other
developers and users of SimPy for improving this document by sending
their comments. I would be grateful for any further corrections or
suggestions. Please send them to: *vignaux* at
*users.sourceforge.net*.


References
-------------------------------------

- Python website: https://www.python.org

- SimPy homepage: https://github.com/SimPyClassic/SimPyClassic

- The Bank:


..
  ------------------------------------------------------



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
