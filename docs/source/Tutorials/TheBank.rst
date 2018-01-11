====================================
The Bank
====================================

.. highlight:: python
   :linenothreshold: 5

.. index::
   Monitors, Tallys, Processes,Resources, Levels, Stores


Introduction
-------------------------------------

In this tutorial, `SimPy`_ is used to develop a simple simulation of a 
bank with a number of tellers.  This Python package provides
*Processes* to model active components such as messages, customers,
trucks, and planes. It has three classes to model facilities where
congestion might occur: *Resources* for ordinary queues, *Levels* for
the supply of quantities of material, and *Stores* for collections of
individual items. Only examples of *Resources* are described here. It
also provides *Monitors* and *Tallys* to record data like queue
lengths and delay times and to calculate simple averages.  It uses the
standard Python random package to generate random numbers.

Starting with SimPy 2.0 an object-oriented programmer's interface was
added to the package. It is compatible with the current procedural
approach which is used in most of the models described here.

.. _`SimPy`: https://github.com/SimPyClassic/SimPyClassic

SimPy can be obtained from: https://github.com/SimPyClassic/SimPyClassic.
The examples run with SimPy version 1.5 and later.  This tutorial is
best read with the SimPy Manual or Cheatsheet at your side for
reference.

Before attempting to use SimPy you should be familiar with the Python_
language. In particular you should be able to use *classes*. Python is
free and available for most machine types. You can find out more about
it at the `Python web site`_.  SimPy is compatible with Python version
2.7 and Python 3.x.

.. _Python: https://www.python.org
.. _`Python web site`: https://www.python.org



A customer arriving at a fixed time
-----------------------------------

In this tutorial we model a simple bank with customers arriving at
random. We develop the model step-by-step, starting out simply, and
producing a running program at each stage. The programs we develop are
available without line numbers and ready to go, in the
``bankprograms`` directory. Please copy them, run them and improve
them - and in the tradition of open-source software suggest your
modifications to the SimPy users list. Object-Oriented versions of all
the models are included in the bankprograms_OO sub directory.

A simulation should always be developed to answer a specific question;
in these models we investigate how changing the number of bank servers
or tellers might affect the waiting time for customers.

We first model a single customer who arrives at the bank for a visit,
looks around at the decor for a time and then leaves.  There is no
queueing. First we will assume his arrival time and the time he spends
in the bank are fixed.

We define a ``Customer`` class derived from the SimPy ``Process``
class. We create a ``Customer`` object, ``c`` who arrives at the bank
at simulation time ``5.0`` and leaves after a fixed time of ``10.0``
minutes.

Examine the following listing which is a complete runnable Python
script.  We use comments to divide the script up into sections. This
makes for clarity later when the programs get more complicated. At #1
is a normal Python documentation string; #2 imports the SimPy
simulation code.

.. index::
   pair: PEM; Process Execution Method

The ``Customer`` class definition at #3 defines our customer class and has
the required generator method (called ``visit`` #4) having a ``yield``
statement #6. Such a method is called a Process Execution Method (PEM) in
SimPy.

The customer's ``visit`` PEM at #4, models his activities.  When he
arrives (it will turn out to be a 'he' in this model), he will print out the
simulation time, ``now()``, and his name at #5.  The function ``now()``
can be used at any time in the simulation to find the current simulation time
though it cannot be changed by the programmer. The customer's name will be set
when the customer is created later in the script at #10.

He then stays in the bank for a fixed simulation time ``timeInBank``
at  #6.
This is achieved by the ``yield hold,self,timeInBank`` statement.  This is the
first of the special simulation commands that ``SimPy`` offers.

After a simulation time of ``timeInBank``, the program's execution
returns to the line after the ``yield`` statement at #6. The
customer then prints out the current simulation time and his
name at #7. This completes the declaration of the ``Customer`` class.

The call ``initialize()`` at #9 sets up the simulation
system ready to receive ``activate`` calls. At #10, we create
a customer, ``c``, with name ``Klaus``. All SimPy Processes have a
``name`` attribute. We ``activate`` ``Klaus`` at #11
specifying the object (``c``) to be activated, the call of the action
routine (``c.visit(timeInBank = 10.0)``) and that it is to be activated
at time 5 (``at = 5.0``). This will activate
``Klaus`` exactly ``5`` minutes after the current time, in this case
after the start of the simulation at ``0.0``. The call of an action
routine such as ``c.visit`` can specify the values of arguments, here
the ``timeInBank``.

Finally the call of ``simulate(until=maxTime)`` at #12 will
start the simulation. This will run until the simulation time is
``maxTime`` unless stopped beforehand either by the
``stopSimulation()`` command or by running out of events to execute
(as will happen here). ``maxTime`` was set to ``100.0`` at #8.


..
    Though we do not do it here, it is also possible to define an
    ``__init__()`` method for a ``Process`` if you need to give the
    customer any attributes.  Bear in mind that such an ``__init__``
    method must first call ``Process.__init__(self)`` and can then
    initialize any instance variables needed.


.. literalinclude:: bankprograms/bank01.py


The short trace printed out by the ``print`` statements shows the
result. The program finishes at simulation time ``15.0`` because there are
no further events to be executed. At the end of the ``visit`` routine,
the customer has no more actions and no other objects or customers are
active.

.. literalinclude:: bankprograms/bank01.out


.. rewritten section for inclusion in the main document

.. index:: bank01_OO, object-oriented style

The Bank in object-oriented style
-----------------------------------

Now look at the same model developed in  object-oriented style. As before
``Klaus`` arrives at the bank for a visit, looks around at the decor
for a time and then leaves.  There is no queueing. The arrival time
and the time he spends in the bank are fixed.

The key point is that we create a ``Simulation`` object and run
that. In the program at #1 we import a new class, ``Simulation``
together with the familiar ``Process`` class, and the ``hold``
verb. Here we are using the recommended explicit form of import rather
than the deprecated ``import *``.

Just as before, we define a ``Customer`` class, derived from the SimPy
``Process`` class, which has the required generator method (PEM), here
called ``visit``.

The customer's ``visit`` PEM models his activities.  When he arrives
at the bank Klaus will print out both the current simulation time,
``self.sim.now()``, and his name, ``self.name``. The prefix
``self.sim`` is a reference to the simulation object where this
customer exists, thus ``self.sim.now()`` refers to the clock for that
simulation object.  Every ``Process`` instance is linked to the
simulation in which it is created by assigning to its ``sim``
parameter when it is created (at #4).

Now comes the major difference from the Classical SimPy program
structure. We define a class ``BankModel`` from the ``Simulation``
class at #3.  Now any instance of ``BankModel``  is an
independent simulation with its own event list and its own time
axis. A ``BankModel``  instance can activate processes and start the
execution of a simulation on its time axis.

In the ``BankModel``  class, we define a ``run`` method which, when
executes the ``BankModel`` instance, i.e. performs a simulation
experiment. When it starts it initializes the simulation with it event
list and sets the time to 0.

#4 creates a ``Customer`` object and the parameter assignment ``sim =
self`` ties the customer instance to this and only this
simulation. The customer does not exist outside this simulation.  The
call of ``simulate(until=maxTime)``  at #5 starts the
simulation. It will run until the simulation time is ``maxTime``
unless stopped beforehand either by the ``stopSimulation()`` command
or by running out of events to execute (as will happen
here). ``maxTime`` is set to ``100.0`` at #6.

.. note::

    If model classes like the ``BankModel`` are to be given any other
    attributes, they must have an ``__init__`` method in which these
    attributes are assigned. Such an ``__init__`` method must first call
    ``Simulation.__init__(self)`` to also initialize the
    ``Simulation`` class from which the model inherits.

A new, independent simulation object, ``mymodel``, is created
at #7. Its ``run`` method is executed at #8.

.. index::
   pair: PEM; Process Execution Method


.. literalinclude:: bankprograms_OO/bank01_OO.py


The short trace printed out by the ``print`` statements shows the
result. The program finishes at simulation time ``15.0`` because there are
no further events to be executed. At the end of the ``visit`` routine,
the customer has no more actions and no other objects or customers are
active.

.. literalinclude:: bankprograms_OO/bank01_OO.out


All of The Bank programs have been written in both the procedural and
object orientated styles.


.. index:: random arrival, bank05

A customer arriving at random
-----------------------------------

Now we extend the model to allow our customer to arrive at a random
simulated time though we will keep the time in the bank at 10.0, as
before.

The change occurs at #1, #2, #3, and #4 in the program. At #1 we
import from the standard Python ``random`` module to give us
``expovariate`` to generate the random time of arrival. We also import
the ``seed`` function to initialize the random number stream to allow
control of the random numbers.  At #2 we provide an initial seed of
``99999``. An exponential random variate, ``t``, is generated
at #3. Note that the Python Random module's ``expovariate`` function
uses the average rate (that is, ``1.0/mean``) as the argument. The
generated random variate, ``t``, is used at #4 as the ``at`` argument
to the ``activate`` call.

.. literalinclude:: bankprograms/bank05.py


The result is shown below. The customer now arrives at about
0.64195, (or 10.58092 if you are not using Python 3). Changing the seed
value would change that time.

.. literalinclude:: bankprograms/bank05.out

The display looks pretty untidy. In the next example I will try and
make it tidier.

If you are not using Python 3, your output may differ.
The output for Python 2, for all examples, is given in Appendix A.


.. index:: bank02

More customers
-------------------------------------

Our simulation does little so far.  To consider a simulation with
several customers we return to the simple deterministic model and add
more ``Customers``.

The program is almost as easy as the first example (`A Customer
arriving at a fixed time`_). The main change is between
#4 to #5 where we create, name, and activate three
customers. We also increase the maximum simulation time to ``400``
(at #3 and referred to at #6). Observe that we need
only one definition of the ``Customer`` class and create several
objects of that class. These will act quite independently in this
model.

Each customer stays for a different ``timeinbank`` so, instead of
setting a common value for this we set it for each customer. The
customers are started at different times (using ``at=``). ``Tony's``
activation time occurs before ``Klaus's``, so ``Tony`` will arrive
first even though his activation statement appears later in the
script.

As promised, the print statements have been changed to use Python
string formatting (at #1 and #2). The statements look
complicated but the output is much nicer.

.. literalinclude:: bankprograms/bank02.py


The trace produced by the program is shown below.  Again the
simulation finishes before the ``400.0`` specified in the ``simulate``
call as it has run out of events.

.. literalinclude:: bankprograms/bank02.out

.. -------------------------------------------------------------

.. index:: bank03

Many customers
----------------------


Another change will allow us to have more customers. As it is
tedious to give a specially chosen name to each one, we will
call them ``Customer00, Customer01,...`` and use a separate
``Source`` class to create and activate them. To make things clearer
we do not use the random numbers in this model.

.. index::  Source of entities

The following listing shows the new program. At #1 to #4  a ``Source``
class is defined. Its PEM, here called ``generate``, is
defined between #2 to #4.  This PEM has a couple of arguments:
the ``number`` of customers to be generated and the Time Between
Arrivals, ``TBA``. It consists of a loop that creates a sequence
of numbered ``Customers`` from ``0`` to ``(number-1)``, inclusive. We
create a customer and give it a name at #3. It is
then activated at the current simulation time (the final argument of
the ``activate`` statement is missing so that the default value of
``now()`` is used as the time). We also specify how long the customer
is to stay in the bank. To keep it simple, all customers stay
exactly ``12`` minutes.  After each new customer is activated, the
``Source`` holds for a fixed time (``yield hold,self,TBA``)
before creating the next one (at #4).

A ``Source``, ``s``, is created at #5 and activated at
#6 where the number of customers to be generated is set to
``maxNumber = 5`` and the interval between customers to ``ARRint =
10.0``. Once started at time ``0.0`` it creates customers at intervals
and each customer then operates independently of the others:


.. literalinclude:: bankprograms/bank03.py


The output is:

.. literalinclude:: bankprograms/bank03.out


.. -------------------------------------------------------------

Many random customers
-----------------------------------

.. index:: bank06


We now extend this model to allow arrivals at random. In simulation this
is usually interpreted as meaning that the times between customer
arrivals are distributed as exponential random variates. There is
little change in our program, we use a ``Source`` object, as before.

The exponential random variate is generated at #1 with
``meanTBA`` as the mean Time Between Arrivals and used at
#2. Note that this parameter is not exactly intuitive. As already
mentioned, the Python ``expovariate`` method uses the *rate* of
arrivals as the parameter not the average interval between them. The
exponential delay between two arrivals gives pseudo-random
arrivals. In this model the first customer arrives at time ``0.0``.

The ``seed`` method is called to initialize the random number stream
in the ``model`` routine (at #3).  It is possible to leave this
call out but if we wish to do serious comparisons of systems, we must
have control over the random variates and therefore control over the
seeds. Then we can run identical models with different seeds or
different models with identical seeds.  We provide the seeds as
control parameters of the run. Here a seed is assigned at #3
but it is clear it could have been read in or manually entered on an
input form.


.. literalinclude:: bankprograms/bank06.py

with the following output:

.. literalinclude:: bankprograms/bank06.out

.. ---------------------------------------------------------------


.. raw:: latex

   \newpage


==================================
Service Counters
==================================
.. index::
   pair: Resource; queue

We introduce a service counter at the Bank using a SimPy Resource.

.. index:: bank07, Service counter


A service counter
-------------------

So far, the model has been more like an art gallery, the customers
entering, looking around, and leaving. Now they are going to require
service from the bank clerk. We extend the model to include a service
counter which will be modelled as an object of SimPy's ``Resource``
class with a single resource unit.  The actions of a ``Resource`` are
simple: a customer ``requests`` a unit of the resource (a clerk). If
one is free he gets service (and removes the unit). If there is no
free clerk the customer joins the queue (managed by the resource
object) until it is their turn to be served. As each customer
completes service and ``releases`` the unit, the clerk can start
serving the next in line.

The service counter is created as a ``Resource`` (``k``) in
at #8. This is provided as an argument to the ``Source`` (at #9)
which, in turn, provides it to each customer it creates and activates
(at #1).

The actions involving the service counter, ``k``, in the customer's
PEM are:

- the ``yield request`` statement at #3. If the server is
  free then the customer can start service immediately and the code
  moves on to #4. If the server is busy, the customer is
  automatically queued by the  Resource. When it eventually comes
  available the PEM moves on to #4.

- the ``yield hold`` statement at #5 where the operation of
  the service counter is modelled. Here the service time is a fixed
  ``timeInBank``.  During this period the customer is being served.

- the ``yield release`` statement at #6. The current
  customer completes service and the service counter becomes available
  for any remaining customers in the queue.

Observe that the service counter is used with the pattern (``yield request..``; ``yield hold..``; ``yield release..``).

To show the effect of the service counter on the activities of the
customers, I have added #2 to record when the customer
arrived and #4 to record the time between arrival in the
bank and starting service. #4 is *after* the ``yield
request`` command and will be reached only when the request is
satisfied. It is *before* the ``yield hold`` that corresponds to the
start of service. The variable ``wait`` will record how long the
customer waited and will be 0 if he received service at once. This
technique of saving the arrival time in a variable is common. So the
``print`` statement also prints out how long the customer waited in
the bank before starting service.


.. literalinclude:: bankprograms/bank07.py

Examining the trace we see that the first, and last, customers get instant
service but the others have to wait. We still only have five customers
(#7) so we cannot draw general conclusions.

.. literalinclude:: bankprograms/bank07.out

.. index::
   Resource, Random service time, bank08
   pair: M/M/1; queue

.. ---------------------------------------------------------------

A server with a random service time
-----------------------------------

This is a simple change to the model in that we retain the single
service counter but make the customer service time a random
variable. As is traditional in the study of simple queues we first
assume an exponential service time and set the mean to ``timeInBank``.

The service time random variable, ``tib``, is generated at
#1 and used at #2. The argument to be used in the call
of ``expovariate`` is not the mean of the distribution,
``timeInBank``, but is the rate ``1/timeInBank``.

We have also collected together a number of constants by defining a
number of appropriate variables and giving them values. These are in
lines between marks #3 and #4.

.. literalinclude:: bankprograms/bank08.py

And the output:

.. literalinclude:: bankprograms/bank08.out

This model with random arrivals and exponential service times is an
example of an M/M/1 queue and could rather easily be solved
analytically to calculate the steady-state mean waiting time and other
operating characteristics. (But not so easily solved for its transient
behavior.)

.. ---------------------------------------------------------------

Several service counters
-------------------------------------


When we introduce several counters we must decide on a queue
discipline. Are customers going to make one queue or are they going to
form separate queues in front of each counter? Then there are
complications - will they be allowed to switch lines (jockey)? We
first consider a single queue with several counters and later consider
separate isolated queues. We will not look at jockeying.

.. ---------------------------------------------------------------

.. index::  Resource, several counters, bank09


Here we model a bank whose customers arrive randomly and are to be
served at a group of counters, taking a random time for service, where
we assume that waiting customers form a single first-in first-out
queue.

The *only* difference between this model and the single-server model
is at #1. We have provided two counters by increasing the
capacity of the ``counter`` resource to 2. These *units* of the
resource correspond to the two counters. Because both clerks cannot be
called ``Karen``, we have used a general name of ``Clerk``.

.. literalinclude:: bankprograms/bank09.py

The waiting times in this model are very different from those for the
single service counter. For example, none of the customers had to
wait. But, again, we have observed too few customers to draw general
conclusions.

.. literalinclude:: bankprograms/bank09.out

.. ---------------------------------------------------------------
.. index::
   pair: Several queues; Resource
   single: bank10

Several counters with individual queues
-------------------------------------------

Each counter now has its own queue.  The programming is more
complicated because the customer has to decide which one to
join. The obvious technique is to make each counter a separate
resource and it is useful to make a list of resource objects (#7).

In practice, a customer will join the shortest queue.  So we define
a Python function, ``NoInSystem(R)`` (#1 to #2) to
return the sum of the number waiting and the number being served for
a particular counter, ``R``. This function is used at #3 to
list the numbers at each counter. It is then easy to find which
counter the arriving customer should join. We have also modified the
trace printout, #4 to display the state of the system when
the customer arrives. We choose the shortest queue at
#5 to #6 (using the variable ``choice``).

The rest of the program is the same as before.

.. literalinclude:: bankprograms/bank10.py

The results show how the customers choose the counter with the
smallest number. Unlucky ``Customer03`` who joins the wrong queue has
to wait until ``Customer01`` finishes before his service can be
started. There are, however, too few arrivals in these runs, limited
as they are to five customers, to draw any general conclusions about
the relative efficiencies of the two systems.

.. literalinclude:: bankprograms/bank10.out

.. ---------------------------------------------------------------

.. raw:: latex

   \newpage

==================================
Customer's Priority
==================================

.. index:: priority

In Many situations there is a system of priority service. Those
customers with high priority are served first, those with low
priority must wait. In some cases, preemptive priority will even allow
a high-priority customer to interrupt the service of one with a lower
priority.

Priority customers
-------------------

SimPy implements priority requests with an extra numerical priority
argument in the ``yield request`` command, higher values meaning
higher priority. For this to operate, the requested Resource must have
been defined with ``qType=PriorityQ``.

In the first example, we modify the program with random arrivals, one
counter, and a fixed service time with the addition of a high priority
customer. Warning: The ``seed()`` value has been changed to ``787878``
to make the story more exciting. To make things even more confusing,
your results may be different from those here because the ``random``
module gives different results for Python 2.x and 3.x.,

The main modifications are to the definition of the ``counter`` where
we change the ``qType`` and to the ``yield request`` command in the
``visit`` PEM of the customer. We must provide each customer with a
priority. Since the default is ``priority=0`` this is easy for most of
them.

To observe the priority in action, while all other customers have the
default priority of 0, at between #5 and #6 we create and
activate one special customer, ``Guido``, with priority 100 who
arrives at time ``23.0``.

The ``visit`` customer method has a new parameter, ``P`` (at
#3), which allows us to set the customer priority.

At #4, ``counter`` is defined with ``qType=PriorityQ`` so
that we can request it with priority (at #3) using the
statement ``yield request,self,counter,P``

At #2, we now print out the number of customers waiting when each
customer arrives.


.. literalinclude:: bankprograms/bank20.py

The resulting output is as follows. The number of customers in the
queue just as each arrives is displayed in the trace. That count does
not include any customer in service.

.. literalinclude:: bankprograms/bank20.out

.. index:: random arrival, bank20

Reading carefully one can see that when ``Guido`` arrives
``Customer00`` has been served and left at ``12.000``, ``Customer01``
is in service and Customer02 is waiting in the queue. ``Guido``
has priority over any waiting customers and is served
before the at ``24.083``. When ``Guido`` leaves at ``36.083``,
``Customer02`` starts service having waited ``15.873`` minutes.


A priority customer with preemption
-----------------------------------

.. index::
   single: priority: preemption
   single: bank23

Now we allow ``Guido`` to have preemptive priority. He will displace
any customer in service when he arrives. That customer will resume
when ``Guido`` finishes (unless higher priority customers
intervene). It requires only a change to one line of the program,
adding the argument, ``preemptable=True`` to the ``Resource``
statement at #1.

.. literalinclude:: bankprograms/bank23.py

Though ``Guido`` arrives at the same time, ``23.000``, he no longer
has to wait and immediately goes into service, displacing the
incumbent, ``Customer01``. That customer had already completed
``23.000-12.083 = 10.917`` minutes of his service. When ``Guido``
finishes at ``36.083``, ``Customer01`` resumes service and takes
``36.083-35.000 = 1.083`` minutes to finish. His total service time
is the  same as before (``12.000`` minutes).

.. literalinclude:: bankprograms/bank23.out

.. raw:: latex

   \newpage

.. index:: balking, reneging, abandoning (reneging)

==================================
Balking and Reneging Customers
==================================

Balking occurs when a customer refuses to join a queue if it is too
long. Reneging (or, better, abandonment) occurs if an impatient
customer gives up while still waiting and before being served.

Balking customers
-----------------

.. index::
   single: balking
   single: bank24

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
latter we test (at #1). If there is not enough room, we balk,
incrementing a Class variable ``Customer.numBalking`` at #2 to
get the total number balking during the run.

.. literalinclude:: bankprograms/bank24.py

The resulting output for a run of this program showing balking
occurring is given below:

.. literalinclude:: bankprograms/bank24.out

When ``Customer02`` arrives, ``Customer00`` is already in service and
``Customer01`` is waiting. There is no room so ``Customer02``
balks. In fact another customer, ``Customer03`` arrives and balks
before ``Customer00`` is finished.

The balking pattern for python 2.x is different.

.. index::
   single: reneging
   single: abandoning
   single: bank21

Reneging or abandoning
----------------------

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
``)``. In our example, this test is at #1.

.. literalinclude:: bankprograms/bank21.py



.. literalinclude:: bankprograms/bank21.out


``Customer02`` arrives at 16.016 but has only 12 minutes
patience. After that time in the queue (at time 28.016) he abandons
the queue to leave 03 to take his place. 04 also abandons.

The reneging pattern for python 2.x is different due to a different
expovariate implementation.


.. index:: Monitors, Gathering statistics, statistics

==================================
Gathering Statistics
==================================

SimPy Monitors allow statistics to be gathered and simple
summaries calculated.

The bank with a monitor
-------------------------------------

.. index::
  pair: Monitored; queue
  single: bank11

The traces of output that have been displayed so far are valuable for
checking that the simulation is operating correctly but would become
too much if we simulate a whole day. We do need to get results from
our simulation to answer the original questions. What, then, is the
best way to summarize the results?

One way is to analyze the traces elsewhere, piping the trace output,
or a modified version of it, into a *real* statistical program such as
*R* for statistical analysis, or into a file for later examination by
a spreadsheet. We do not have space to examine this thoroughly here.
Another way of presenting the results is to provide graphical
output.

SimPy offers an easy way to gather a few simple statistics such as
averages: the ``Monitor`` and ``Tally`` classes. The ``Monitor``
records the values of chosen variables as time series (but see the
comments in `Final Remarks`_).

.. index::
   single: recording average waiting times

We now demonstrate a ``Monitor`` that records the average waiting
times for our customers. We return to the system with random arrivals,
random service times and a single queue and remove the old trace
statements.  In practice, we would make the printouts controlled by a
variable, say, ``TRACE`` which is set in the experimental data (or
read in as a program option - but that is a different story). This
would aid in debugging and would not complicate the data analysis. We
will run the simulations for many more arrivals.

A Monitor, ``wM``, is created at #2. It ``observes`` and
records the waiting time mentioned at #1.  We run
``maxNumber=50`` customers (in the call of ``generate`` at
#3) and have increased ``maxTime`` to ``1000`` minutes. Brief
statistics are given by the Monitor methods ``count()`` and ``mean()``
at #4.

.. literalinclude:: bankprograms/bank11.py


The average waiting time for 50 customers in this 2-counter system is
more reliable (i.e., less subject to random simulation effects) than
the times we measured before but it is still not sufficiently reliable
for real-world decisions. We should also replicate the runs using
different random number seeds. The result of this run (using Python 3.2) is:

.. literalinclude:: bankprograms/bank11.out

Result for Python 2.x is given in Appendix A.

.. index::
   single: resource monitoring, bank15

Monitoring a resource
---------------------

Now consider observing the number of customers waiting or executing in
a Resource. Because of the need to ``observe`` the value after the
change but at the same simulation instant, it is impossible to use the
length of the Resource's ``waitQ`` directly with a Monitor defined
outside the Resource. Instead Resources can be set up with built-in
Monitors.

Here is an example using a Monitored Resource. We intend to observe
the average number waiting and active in the ``counter``
resource. ``counter`` is defined at #1 and we have set
``monitored=True``. This establishes two Monitors: ``waitMon``, to
record changes in the numbers waiting and ``actMon`` to record changes
in the numbers active in the ``counter``. We need make no further
change to the operation of the program as monitoring is then
automatic.  No ``observe`` calls are necessary.

At the end of the run in the ``model`` function, we calculate the
``timeAverage`` of both ``waitMon`` and ``actMon`` and return them
from the ``model`` call (at #2). These can then be printed at
the end of the program (at #3).

.. literalinclude:: bankprograms/bank15.py

With the following output:

.. literalinclude:: bankprograms/bank15.out

.. index::
   single: Multiple runs, replications, bank12
   single: Random Number Seed
   pair: model; function

Multiple runs
-------------

To get a number of independent measurements we must replicate the runs
using different random number seeds. Each replication must be
independent of previous ones so the Monitor and Resources must be
redefined for each run. We can no longer allow them to be global
objects as we have before.

We will define a function, ``model`` with a parameter ``runSeed`` so
that the random number seed can be different for different runs (between
between #2 and #5). The contents of the function are the same as the
``Model/Experiment`` in bank11: `The bank with a monitor`_, except for one
vital change.

This is required since the Monitor, ``wM``, is defined inside the
``model`` function (#3). A customer can no longer refer to
it. In the spirit of quality computer programming we will pass ``wM``
as a function argument. Unfortunately we have to do this in two steps,
first to the ``Source`` (#4) and then from the ``Source`` to
the ``Customer`` (#1).

``model()`` is run for four different random-number seeds to get a set
of replications (between #6 and #7).

.. literalinclude:: bankprograms/bank12.py

The results show some variation. Remember, though, that the system is still
only operating for 50 customers so the system may not be in
steady-state.

.. literalinclude:: bankprograms/bank12.out


.. index::
   GUI input, Graphical Output,Statistical Output
   Priorities and Reneging,Other forms of Resource Facilities
   Advanced synchronization/scheduling commands


==================================
Final Remarks
==================================

This introduction is too long and the examples are getting
longer. There is much more to say about simulation with *SimPy* but no
space. I finish with a list of topics for further study:

Topics not yet mentioned
------------------------

* **GUI input**. Graphical input of simulation parameters could be an
  advantage in some cases. *SimPy* allows this and programs using
  these facilities have been developed (see, for example, program
  ``MM1.py`` in the examples in the *SimPy* distribution)

* **Graphical Output**. Similarly, graphical output of results can
  also be of value, not least in debugging simulation programs and
  checking for steady-state conditions. SimPlot is useful here.

* **Statistical Output**. The ``Monitor`` class is useful in
  presenting results but more powerful methods of analysis are often
  needed. One solution is to output a trace and read that into a
  large-scale statistical system such as *R*.

* **Priorities and Reneging in queues**. *SimPy* allows processes to
  request units of resources under a priority queue discipline
  (preemptive or not). It also allows processes to renege from a queue.

* **Other forms of Resource Facilities**. *SimPy* has two other
  resource structures: ``Levels`` to hold bulk commodities, and
  ``Stores``   to contain an inventory of different object types.

* **Advanced synchronization/scheduling commands**. *SimPy* allows
  process synchronization by events and signals.



Acknowledgements
-------------------------------------

I thank Klaus Muller, Bob Helmbold, Mukhlis Matti, Karen Turner and
other developers and users of SimPy for improving this document by
sending their comments. I would be grateful for further suggestions or
corrections. Please send them to: *vignaux* at
*users.sourceforge.net*.

References
-------------------------------------

- Python website: https://www.python.org

- SimPy Classic website: https://github.com/SimPyClassic/SimPyClassic


==================================
Appendix A
==================================

With Python 3 the definition of expovariate changed. In some cases
this was back ported to some distributions of Python 2.7.
Because of this the output for the bank programs varies. This section
contains the older output produced by the original definition of expovariate.

**A Customer arriving at a fixed time**

.. literalinclude:: bankprograms/python2_out/bank01.out

**A Customer arriving at random**

.. literalinclude:: bankprograms/python2_out/bank05.out

**More Customers**

.. literalinclude:: bankprograms/python2_out/bank02.out

**Many Customers**

.. literalinclude:: bankprograms/python2_out/bank03.out

**Many Random Customers**

.. literalinclude:: bankprograms/python2_out/bank06.out

**A Service Counter**

.. literalinclude:: bankprograms/python2_out/bank07.out

**A server with a random service time**

.. literalinclude:: bankprograms/python2_out/bank08.out

**Several Counters but a Single Queue**

.. literalinclude:: bankprograms/python2_out/bank09.out

**Several Counters with individual queues**

.. literalinclude:: bankprograms/python2_out/bank10.out

**Priority Customers**

.. literalinclude:: bankprograms/python2_out/bank20.out

**A priority Customer with Preemption**

.. literalinclude:: bankprograms/python2_out/bank23.out

**Balking Customers**

.. literalinclude:: bankprograms/python2_out/bank24.out

**Reneging or Abandoning**

.. literalinclude:: bankprograms/python2_out/bank21.out

**The Bank with a Monitor**

.. literalinclude:: bankprograms/python2_out/bank11.out

**Monitoring a Resource**

.. literalinclude:: bankprograms/python2_out/bank15.out

**Multiple runs**

.. literalinclude:: bankprograms/python2_out/bank12.out


..
  ------------------------------------------------------


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
