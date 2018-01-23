.. Tutorials

.. .. image:: images/sm_SimPy_Logo.png
      :align: left

===================================================================
The Bank Tutorial part 2: More  examples of SimPy Classic Simulation
====================================================================

.. ---------------------------------------------------
..  TO DO
    add example of using SimpyTrace
    Reneging due to an event
    Interrupts - YES
    SimEvents?

.. ---------------------------------------------------

:Author: G A Vignaux
:Date:  2012 February
:Updated: January 2018
:Release: |release|
:Python-Version: 2.7 and later


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

.. _SimPy: https://github.com/SimPyClassic/SimPyClassic

The programs are available without line numbers and ready to go, in
directory ``bankprograms``. Some have trace statements for
demonstration purposes, others produce graphical output to the
screen. Let me encourage you to run them and modify them for yourself

SimPy itself can be obtained from:
https://github.com/SimPyClassic/SimPyClassic.  It is compatible with
Python version 2.7 onwards.  The examples in this documentation run
with SimPy version 1.5 and later.

This tutorial should be read with the SimPy Manual or Cheatsheet at
your side for reference.

.. raw:: latex

   \newpage

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
``timeOfCall``, an argument to its ``ring`` PEM (label #7).

..
   12  1
   13 2
   14 3
   19 4
   20 5
   21 6
   26 7
   29 8


``klaus``, a ``Customer``, is interrupted by the call (Label #8).
He is in the middle of a ``yield hold`` (label #1). When he exits
from that command it is as if he went into a trance when talking to
the bank manager. He suddenly wakes up and must check (label #2)
to see whether has finished his conversation (if there was no call) or
has been interrupted.

If ``self.interrupted()`` is ``False`` he was not interrupted and
leaves the bank (label #6) normally. If it is ``True``, he was
interrupted by the call, remembers how much conversation he has left
(Label #3), resets the interrupt and then deals with the call. When he
finishes (label #4) he can resume the conversation, with, now we
assume, a thoroughly irritated bank manager (label #5).

.. literalinclude:: bankprograms/bank22.py


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
and then rush in and queue to be served.

This model uses the ``waituntil`` yield command. In the program listing
the door is initially closed (label #1) and a function to test if
it is open is defined at label #2.

..
   07  1
   08  2
   11  3
   16  4
   29  5
   40  6
   65  7
   66  8

The ``Doorman`` class is defined starting at label #3 and the single
``doorman`` is created and activated at at labels #7 and #8. The
doorman waits for an average 10 minutes (label #4) and then
opens the door.

The ``Customer`` class is defined at label #5 and a new customer prints out
``Here I am`` on arrival. If the door is still closed, he adds ``but
the door is shut`` and settles down to wait (label #6), using the
``yield waituntil`` command. When the door is opened by the doorman the
``dooropen`` state is changed and the customer (and all others waiting
for the door) proceed. A customer arriving when the door is open will
not be delayed.

.. literalinclude:: bankprograms/bank14.py

The output from a run for this programs shows how the first customer
has to wait until the door is opened.

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

..
   07 1
   10 2
   15 3
   16 4
   29 5
   39 6
   66 7
   67 8


This model uses the ``yield waitevent`` command which requires a
``SimEvent`` to be defined (label #1).  The ``Doorman`` class is
defined at label #2 and the ``doorman`` is created and activated at
labels #7 and #8. The doorman waits for a fixed time (label #3) and
then tells the customers that the door is open. This is achieved on
label #4 by signalling the ``dooropen`` event.

The ``Customer`` class is defined at label #5 and in its PEM, when a
customer arrives, he prints out ``Here I am``. If the door is still
closed, he adds `"but the door is shut`` and settles down to wait for
the door to be opened using the ``yield waitevent`` command (label
#6). When the door is opened by the doorman (that is, he sends the
``dooropen.signal()`` the customer and any others waiting may proceed.


.. literalinclude:: bankprograms/bank13.py


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
       Mon.observe(n,now())

Thus you make the change (not only increases) and *then* observe the new
value. Of course the simulation time ``now()`` has not changed between
the two statements.



Plotting a Histogram of Monitor results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Monitor can construct a histogram from its data using the
``histogram`` method. In this model we monitor the time in the system
for the customers. This is calculated for each customer at label #2,
using the arrival time saved at label #1. We create the Monitor,
``Mon``, at label #4 and the times are ``observed`` at label #3.

The histogram is constructed from the Monitor, after the simulation
has finished, at label #5. The SimPy SimPlot package allows
simple plotting of results from simulations.  Here we use the SimPlot
``plotHistogram`` method. The plotting routines appear between labels
#6 and #7. The ``plotHistogram`` call is in label #7.

.. literalinclude:: bankprograms/bank17.py



Plotting from  Resource Monitors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..
  03 1
  20 2
  37 3
  43  4
  44 5
  50 6
  51 7
  52 8
  53 9




Like all Monitors, ``waitMon`` and ``actMon`` in a monitored Resource
contain information that enables us to graph the output. Alternative
plotting packages can be used; here we use the simple ``SimPy.SimPlot``
package just to graph the number of customers waiting for the
counter. The program is a simple modification of the one that uses a
monitored Resource.

The SimPlot package is imported at #3. No major changes are made to
the main part of the program except that I commented out the print
statements. The changes occur in the ``model`` routine from #3 to
#5.The simulation now generates and processes 20 customers (#4).
``model`` does not return a value but the Monitors of the ``counter``
Resource still exist when the simulation has terminated.

The additional plotting actions take place from #6 to #9. Lines #7 and
#8 construct a step plot and graphs the
number in the waiting queue as a function of time. ``waitMon`` is
primarily a list of *[time,value]* pairs which the ``plotStep`` method
of the SimPlot object, ``plt`` uses without change. On running the
program the graph is plotted; the user has to terminate the plotting
``mainloop`` on the screen.


.. literalinclude:: bankprograms/bank16.py




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
