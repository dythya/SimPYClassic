============================================================================
The Bank (Object Oriented version)
============================================================================

..  Tutorials/TheBankOO

.. highlight:: python
   :linenothreshold: 5

.. index::
   Simulation,Monitors, Tallys, Processes,Resources, Levels, Stores

.. :Authors: G A Vignaux, K G Muller
   :Date:  2010 April

Introduction
-------------------------------------

`SimPy`_ is used to develop a simple simulation of a bank with a
number of tellers.  This Python package provides *Processes* to model
active components such as messages, customers, trucks, and planes. It
has three classes to model facilities where congestion might occur:
*Resources* for ordinary queues, *Levels* for the supply of quantities
of material, and *Stores* for collections of individual items. Only
examples of *Resources* are described here. It also provides
*Monitors* and *Tallys* to record data like queue lengths and delay
times and to calculate simple averages.  It uses the standard Python
random package to generate random numbers.

Starting with SimPy 2.0 an object-oriented programmer's interface was
added to the package and it is this version that is described here.
It is quite compatible with the procedural approach. The object-oriented
interface, however, can support the process of developing and extending a
simulation model better than the procedural approach.


.. _`SimPy`: https://github.com/SimPyClassic/SimPyClassic


SimPy can be obtained from: https://github.com/SimPyClassic/SimPyClassic.
This tutorial is best read with the SimPy Manual and CheatsheetOO at
your side for reference.

Before attempting to use SimPy you should be familiar with the Python_
language. In particular you should be able to use *classes*. Python is
free and available for most machine types. You can find out more about
it at the `Python web site`_.  SimPy is compatible with Python version
2.3 and later.

.. _Python: https://www.python.org
.. _`Python web site`: https://www.python.org



A  single Customer
-------------------

In this tutorial we model a simple bank with customers arriving at
random. We develop the model step-by-step, starting out simply, and
producing a running program at each stage. The programs we develop are
available without line numbers and ready to go, in the
``bankprograms_OO`` directory. Please copy them, run them and improve
them - and in the tradition of open-source software suggest your
modifications to the SimPy users list. Object-orented versions of all
the models are included in the same directory.

A simulation should always be developed to answer a specific question;
in these models we investigate how changing the number of bank servers
or tellers might affect the waiting time for customers.

.. index:: bank01_OO


A Customer arriving at a fixed time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We first model a single customer who arrives at the bank for a visit,
looks around at the decor for a time and then leaves.  There is no
queueing. First we will assume his arrival time and the time he spends
in the bank are fixed.

Examine the following listing which is a complete runnable Python
script, except for the line numbers.  We use comments to divide the
script up into sections. This makes for clarity later when the
programs get more complicated.  Line 1 is a normal Python
documentation string; line 2 makes available the SimPy constructs
needed for this model: the ``Simulation`` class, the ``Process`` class,
and the ``hold`` verb.

We define a ``Customer`` class derived from the SimPy ``Process``
class. We create a ``Customer`` object, ``c`` who arrives at the bank
at simulation time ``5.0`` and leaves after a fixed time of ``10.0``
minutes. The ``Customer`` class definition, lines 5-12, defines our
customer class and has the required generator method (called
``visit``) (line 9) having a ``yield`` statement (line
11)). Such a method is called a Process Execution Method (PEM) in
SimPy.

The customer's ``visit`` PEM, lines 9-12, models his
activities.  When he arrives (it will turn out to be a 'he' in this
model), he will print out the simulation time, ``self.sim.now()``,
and his name (line 10). ``self.sim`` is a reference to the ``BankModel``
simulation object where this customer exists. Every ``Process`` instance
is linked to the simulation in which it is created by assigning to
its ``sim`` parameter when it is created (see line 19).
The method ``now()`` can be used at any
time in the simulation to find the current simulation time though it cannot be
changed by the programmer. The customer's name will be set when the
customer is created later in the script (line 19).

He then stays in the bank for a fixed simulation time ``timeInBank``
(line 11).  This is achieved by the ``yield hold,self,timeInBank`` statement.
This is the first of the special simulation commands that ``SimPy`` offers.

After a simulation time of ``timeInBank``, the program's execution
returns to the line after the ``yield`` statement, line 12. The
customer then prints out the current simulation time and his
name. This completes the declaration of the ``Customer`` class.

Though we do not do it here, it is also possible to define an
``__init__()`` method for a ``Process`` if you need to give the
customer any attributes.  Bear in mind that such an ``__init__``
method must first call ``Process.__init__(self)`` and can then
initialize any instance variables needed.

..
  01 1
  02 2
  05 3
  06 4
  09 5
  10 6
  11 7
  12 8
  17 9
  18 10
  19 11
  20
  21
  24
  25
  32


Lines 6 to 21 define a class ``BankModel``, composing a model of a bank from
the ``Simulation`` class, a ``Customer`` class and the global experiment data.
The definition ``class BankModel(Simulation)`` gives an instance of a
``BankModel`` all the attributes of class ``Simulation``. (In OO terms,
``BankModel`` *inherits* from ``Simulation``.) Any instance of ``BankModel``
*is* a ``Simulation`` instance. This gives a ``BankModel`` its own event list
and thus its own time axis. Also, it allows a ``BankModel`` instance to
activate processes and to start the execution of a simulation on its time axis.

Lines 17 to 21 define a ``run`` method; when called, it results in the
execution of a ``BankModel`` instance, i.e. the performance of a
simulation experiment. Line 18 initializes this simulation, i.e. it
creates a new event list. L.19 creates a ``Customer`` object. The
parameter assignment ``sim = self`` ties the customer instance to this
and only this simulation. The customer does not exist outside this
simulation. L.20 activates the customer's ``visit`` process (PEM).
Finally the call of ``simulate(until=maxTime)`` in line 24 starts the
simulation. It will run until the simulation time is ``maxTime``
unless stopped beforehand either by the ``stopSimulation()`` command
or by running out of events to execute (as will happen
here). ``maxTime`` was set to ``100.0`` in line 25.

.. note::

    If model classes like the``BankModel`` are to be given any other
    attributes, they must have an ``__init__`` method in which these
    attributes are assigned with the syntax ``self.attrib1 =
    . . .``. Such an ``__init__`` method must first call
    ``Simulation.__init__(self)`` to also initialize the
    ``Simulation`` class from which the model inherits.

The simulation model is executed by line 32. ``BankModel()`` constructs the
model, and ``.run()`` executes it. This is just a short form of::

    bM = BankModel()
    bM.run()

.. index::
   pair: PEM; Process Execution Method


.. literalinclude:: bankprograms_OO/bank01_OO.py


The short trace printed out by the ``print`` statements shows the
result. The program finishes at simulation time ``15.0`` because there are
no further events to be executed. At the end of the ``visit`` routine,
the customer has no more actions and no other objects or customers are
active.

.. literalinclude:: bankprograms/bank01.out


.. index:: random arrival, bank05_OO

A Customer arriving at random
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we extend the model to allow our customer to arrive at a random
simulated time though we will keep the time in the bank at 10.0, as
before.


The change occurs in line 3 of the program and in lines 19, 21,
23, 31 and 35. In line 3 we import from the standard
Python ``random`` module to give us ``expovariate`` to generate the
random time of arrival. We also import the ``seed`` function to
initialize the random number stream to allow control of the random
numbers.  The  ``run`` method is given a parameter ``aseed`` for the
initial seed (line 19) .In line 31 we provide an initial seed of
``99999``. An exponential random variate, ``t``, is generated in line 23. Note
that the Python Random module's ``expovariate`` function uses the rate
(here, ``1.0/tMeanArrival``) as the argument. The generated random variate,
``t``, is used in line 24 as the ``at`` argument to the
``activate`` call. ``tMeanArrival`` is assigned a value of ``5.0`` minutes
at line 31.

In line 35, the ``BankModel`` entity is generated and its ``run`` function
called with parameter assignment ``aseed=seedVal``.

..
    The change occurs in line 3 of the program and in lines 22,
    25, and 26. In line 3 we import from the standard
    Python ``random`` module to give us ``expovariate`` to generate the
    random time of arrival. We also import the ``seed`` function to
    initialize the random number stream to allow control of the random
    numbers.  In line 22 we provide an initial seed of ``99999``. An
    exponential random variate, ``t``, is generated in line 25. Note
    that the Python Random module's ``expovariate`` function uses the rate
    (that is, ``1.0/mean``) as the argument. The generated random variate,
    ``t``, is used in Line 26 as the ``at`` argument to the
    ``activate`` call.


.. literalinclude:: bankprograms_OO/bank05_OO.py


The result is shown below. The customer now arrives at time
10.5809. Changing the seed value would change that time.

.. literalinclude:: bankprograms/bank05.out


The display looks pretty untidy. In the next example I will try and
make it tidier.


.. index:: bank02_OO

More Customers
-------------------------------------

Our simulation does little so far.  To consider a simulation with
several customers we return to the simple deterministic model and add
more ``Customers``.

The program is almost as easy as the first example (`A Customer
arriving at a fixed time`_). The main change is in lines
19-24 where we create, name, and activate three
customers. We also increase the maximum simulation time to ``400``
(line 29 and referred to in line 25). Observe that we need
only one definition of the ``Customer`` class and create several
objects of that class. These will act quite independently in this
model.

Each customer stays for a different ``timeInBank`` so, instead of
setting a common value for this we set it for each customer. The
customers are started at different times (using ``at=``). ``Tony's``
activation time occurs before ``Klaus's``, so ``Tony`` will arrive
first even though his activation statement appears later in the
script.

As promised, the print statements have been changed to use Python
string formatting (lines 10 and 12). The statements look
complicated but the output is much nicer.


..
 The program is almost as easy as the first example (`A Customer
 arriving at a fixed time`_). The main change is in lines
 22-27 where we create, name, and activate three
 customers. We also increase the maximum simulation time to ``400``
 (line 16 and referred to in line 29). Observe that we need
 only one definition of the ``Customer`` class and create several
 objects of that class. These will act quite independently in this
 model.

 Each customer stays for a different ``timeInBank`` so, instead of
 setting a common value for this we set it for each customer. The
 customers are started at different times (using ``at=``). ``Tony's``
 activation time occurs before ``Klaus's``, so ``Tony`` will arrive
 first even though his activation statement appears later in the
 script.

 As promised, the print statements have been changed to use Python
 string formatting (lines 10 and 12). The statements look
 complicated but the output is much nicer.


.. literalinclude:: bankprograms_OO/bank02_OO.py


The trace produced by the program is shown below.  Again the
simulation finishes before the ``400.0`` specified in the ``simulate``
call.

.. literalinclude:: bankprograms/bank02.out


.. -------------------------------------------------------------

.. index:: bank03_OO

Many Customers
~~~~~~~~~~~~~~~~~~~


Another change will allow us to have more customers. As it is
tedious to give a specially chosen name to each one, we will
call them ``Customer00, Customer01,...`` and use a separate
``Source`` class to create and activate them. To make things clearer
we do not use the random numbers in this model.

.. index::  Source of entities

The following listing shows the new program. Lines 6-13
define a ``Source`` class. Its PEM, here called ``generate``, is
defined in lines 9-13.  This PEM has a couple of arguments:
the ``number`` of customers to be generated and the Time Between
Arrivals, ``TBA``. It consists of a loop that creates a stream
of numbered ``Customers`` from ``0`` to ``(number-1)``, inclusive. We
create a customer and give it a name in line 11. The parameter
assignment ``sim = self.sim`` ties the customers to the ``BankModel``
to which the ``Source`` belongs. The customer is
then activated at the current simulation time (the final argument of
the ``activate`` statement is missing so that the default value of
``self.sim.now()``, the current simulation time for the instance of
``BankModel``, is used as the time; here, it is ``0.0``). We also specify
how long the customer
is to stay in the bank. To keep it simple, all customers stay
exactly ``12`` minutes.  After each new customer is activated, the
``Source`` holds for a fixed time (``yield hold,self,TBA``)
before creating the next one (line 13).

``class BankModel(Simulation)`` (line 24) provides a ``run`` method
which executes this model consisting of a customer source and the global data.
As ``BankModel`` inherits from ``Simulation``, it has its own event list which gets
initialized as empty in line 26.

A ``Source``, ``s``, is created in line 27 and activated at line
28 where the number of customers to be generated is set to
``maxNumber = 5`` and the interval between customers to ``ARRint = 10.0``.
The parameter assignment ``sim = self`` links the ``Source`` process
to this ``BankModel`` instance. Once started at time ``0.0``, ``s``  creates
customers at intervals and each customer then operates independently of the others.

In line 40, a ``BankModel`` object is created and its ``run`` method executed:

..
    The following listing shows the new program. Lines 6-13
    define a ``Source`` class. Its PEM, here called ``generate``, is
    defined in lines 9-13.  This PEM has a couple of arguments:
    the ``number`` of customers to be generated and the Time Between
    Arrivals, ``TBA``. It consists of a loop that creates a sequence
    of numbered ``Customers`` from ``0`` to ``(number-1)``, inclusive. We
    create a customer and give it a name in line 11. It is
    then activated at the current simulation time (the final argument of
    the ``activate`` statement is missing so that the default value of
    ``now()`` is used as the time). We also specify how long the customer
    is to stay in the bank. To keep it simple, all customers stay
    exactly ``12`` minutes.  After each new customer is activated, the
    ``Source`` holds for a fixed time (``yield hold,self,TBA``)
    before creating the next one (line 13).

    A ``Source``, ``s``, is created in line 32 and activated at line
    33 where the number of customers to be generated is set to
    ``maxNumber = 5`` and the interval between customers to ``ARRint =
    10.0``. Once started at time ``0.0`` it creates customers at intervals
    and each customer then operates independently of the others:


.. literalinclude:: bankprograms_OO/bank03_OO.py


The output is:

.. literalinclude:: bankprograms/bank03.out


.. -------------------------------------------------------------

Many Random Customers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. index:: bank06_OO


We now extend this model to allow arrivals at random. In simulation this
is usually interpreted as meaning that the times between customer
arrivals are distributed as exponential random variates. There is
little change in our program, we use a ``Source`` object, as before.

The exponential random variate is generated in line 14 with
``meanTBA`` as the mean Time Between Arrivals and used in line
15. Note that this parameter is not exactly intuitive. As already
mentioned, the Python ``expovariate`` method uses the *rate* of
arrivals as the parameter not the average interval between them. The
exponential delay between two arrivals gives pseudo-random
arrivals. In this model the first customer arrives at time ``0.0``.

The ``seed`` method is called to initialize the random number stream
in the ``run`` routine of ``BankModel`` (line 30). It uses the value
provided by parameter ``aseed``. It is possible to leave this
call out but if we wish to do serious comparisons of systems, we must
have control over the random variates and therefore control over the
seeds. Then we can run identical models with different seeds or
different models with identical seeds.  We provide the seeds as
control parameters of the run. Here a seed is assigned in line 41
but it is clear it could have been read in or manually entered on an
input form.

The ``BankModel`` is generated in line 45 and its ``run`` method called with
the seed value as parameter.

..
    We now extend this model to allow arrivals at random. In simulation this
    is usually interpreted as meaning that the times between customer
    arrivals are distributed as exponential random variates. There is
    little change in our program, we use a ``Source`` object, as before.

    The exponential random variate is generated in line 14 with
    ``meanTBA`` as the mean Time Between Arrivals and used in line
    15. Note that this parameter is not exactly intuitive. As already
    mentioned, the Python ``expovariate`` method uses the *rate* of
    arrivals as the parameter not the average interval between them. The
    exponential delay between two arrivals gives pseudo-random
    arrivals. In this model the first customer arrives at time ``0.0``.

    The ``seed`` method is called to initialize the random number stream
    in the ``model`` routine (line 33).  It is possible to leave this
    call out but if we wish to do serious comparisons of systems, we must
    have control over the random variates and therefore control over the
    seeds. Then we can run identical models with different seeds or
    different models with identical seeds.  We provide the seeds as
    control parameters of the run. Here a seed is assigned in line 33
    but it is clear it could have been read in or manually entered on an
    input form.


.. literalinclude:: bankprograms_OO/bank06_OO.py



This generates the following output:

.. literalinclude:: bankprograms/bank06.out


.. ---------------------------------------------------------------

.. index::
   pair: Resource; queue


A Service counter
------------------


So far, the model bank has been more like an art gallery, the customers
entering, looking around, and leaving. Now they are going to require
service from the bank clerk. We extend the model to include a service
counter which will be modelled as an object of SimPy's ``Resource``
class with a single resource unit.  The actions of a ``Resource`` are
simple: a customer ``requests`` a unit of the resource (a clerk). If
one is free he gets service (and removes the unit, i.e., makes it busy).
If there is no
free clerk the customer joins the queue (managed by the resource
object) until it is his turn to be served. As each customer
completes service and ``releases`` the unit, the clerk automatically
starts serving the next in line. This is done by reactivating that customer's
process where it had been blocked.


.. ---------------------------------------------------------------

.. index:: bank07_OO, Service counter

One Service counter
~~~~~~~~~~~~~~~~~~~~~~~~~~

As this model is built with the ``Resource`` class from ``SimPy.Simulation``,
it and the related ``request`` and ``release`` verbs are mported, in addition
to the imports made in the previous programs
(line 2).

The service counter is created as a ``Resource`` attribute ``self.k``
of the ``BankModel`` (line 39). The resource exists in the ``BankModel``,
and this is indicated by the parameter assignment ``sim = self``.
The ``Source`` PEM ``generate`` can access this attribute by
``self.sim.k``, its ``BankModel``'s resource attribute (line 14).

The actions involving the ``Counter`` referred to by the parameter
``res`` in the customer's PEM are:

- the ``yield request`` statement in line 25. If the server is
  free then the customer can start service immediately and the code
  moves on to line  26. If the server is busy, the customer is
  automatically queued by the Resource. When it eventually comes
  available the PEM moves on to line 26.

- the ``yield hold`` statement in line 28 where the operation of
  the service counter is modelled. Here the service time is a fixed
  ``timeInBank``.  During this period the customer is being served
  and the resource (the counter) is busy.

- the ``yield release`` statement in line 29. The current
  customer completes service and the service counter becomes available
  for any remaining customers in the queue.

Observe that the service counter is used with the pattern (``yield
request..``; ``yield hold..``; ``yield release..``).

To show the effect of the service counter on the activities of the
customers, I have added line 22 to record when the customer
arrived and line 26 to record the time between arrival in the
bank and starting service. Line 26 is *after* the ``yield
request`` command and will be reached only when the request is
satisfied. It is *before* the ``yield hold`` that corresponds to the
start of service. The variable ``wait`` will record how long the
customer waited and will be 0 if he received service at once. This
technique of saving the arrival time in a variable is common. So the
``print`` statement also prints out how long the customer waited in
the bank before starting service.

..
    The service counter is created as a ``Resource`` (``k``) in line
    38. This is provided as an argument to the ``Source`` (line
    45) which, in turn, provides it to each customer it creates and
    activates (line 14).

    The actions involving the ``counter`` in the customer's PEM are:

    - the ``yield request`` statement in line 25. If the server is
      free then the customer can start service immediately and the code
      moves on to line  26. If the server is busy, the customer is
      automatically queued by the  Resource. When it eventually comes
      available the PEM moves on to line 26.

    - the ``yield hold`` statement in line 28 where the operation of
      the service counter is modelled. Here the service time is a fixed
      ``timeInBank``.  During this period the customer is being served.

    - the ``yield release`` statement in line 29. The current
      customer completes service and the service counter becomes available
      for any remaining customers in the queue.

    Observe that the service counter is used with the pattern (``yield
    request..``; ``yield hold..``; ``yield release..``).

    To show the effect of the service counter on the activities of the
    customers, I have added line 22 to record when the customer
    arrived and line 26 to record the time between arrival in the
    bank and starting service. Line 26 is *after* the ``yield
    request`` command and will be reached only when the request is
    satisfied. It is *before* the ``yield hold`` that corresponds to the
    start of service. The variable ``wait`` will record how long the
    customer waited and will be 0 if he received service at once. This
    technique of saving the arrival time in a variable is common. So the
    ``print`` statement also prints out how long the customer waited in
    the bank before starting service.


.. literalinclude:: bankprograms_OO/bank07_OO.py



Examining the trace we see that the first two customers get instant service but the others
have to wait. We still only have five customers (line 44) so we
cannot draw general conclusions.

.. literalinclude:: bankprograms/bank07.out



.. index::
   Resource, Random service time, bank08_OO
   pair: M/M/1; queue

.. ---------------------------------------------------------------

A server with a random service time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a simple change to the model in that we retain the single
service counter but make the customer service time a random variable. As
is traditional in the study of simple queues we first assume an exponential service
time and set the mean to ``timeInBank``.

The service time random variable, ``tib``, is generated in line
26 and used in line 27. The argument to be used in the call
of ``expovariate`` is not the mean of the distribution,
``timeInBank``, but is the rate ``1.0/timeInBank``.

We have put together the exeriment data by defining a
number of appropriate variables and giving them values. These are in
lines 44 to 48.

..
    This is a simple change to the model in that we retain the single
    service counter but make the customer service time a random variable. As
    is traditional in the study of simple queues we first assume an exponential service
    time and set the mean to ``timeInBank``.

    The service time random variable, ``tib``, is generated in line
    26 and used in line 27. The argument to be used in the call
    of ``expovariate`` is not the mean of the distribution,
    ``timeInBank``, but is the rate ``1/timeInBank``.

    We have also collected together a number of constants by defining a
    number of appropriate variables and giving them values. These are in
    lines 31 to 42.


.. literalinclude:: bankprograms_OO/bank08_OO.py


And the output:

.. literalinclude:: bankprograms/bank08.out


This model with random arrivals and exponential service times is an
example of an M/M/1 queue and could rather easily be solved
analytically to calculate the steady-state mean waiting time and other
operating characteristics. (But not so easily solved for its transient
behavior.)

.. ---------------------------------------------------------------

Several Service Counters
-------------------------------------


When we introduce several counters we must decide on a queue
discipline. Are customers going to make one queue or are they going to
form separate queues in front of each counter? Then there are
complications - will they be allowed to switch lines (jockey)? We
first consider a single queue with several counters and later consider
separate isolated queues. We will not look at jockeying.



.. ---------------------------------------------------------------

.. index::  Resource, several counters, bank09_OO

Several Counters but a Single Queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Here we model a bank whose customers arrive randomly and are to be
served at a group of counters, taking a random time for service, where
we assume that waiting customers form a single first-in first-out
queue.

The *only* difference between this model and the single-server model
is in line 37. We have provided two counters by increasing the
capacity of the ``counter`` resource to 2. This value is set in line 50
(``Nc = 2``). These *units* of the
resource correspond to the two counters. Because both clerks cannot be
called ``Karen``, we have used a general name of ``Clerk`` as resource
unit.

..
    The *only* difference between this model and the single-server model
    is in line 42. We have provided two counters by increasing the
    capacity of the ``counter`` resource to 2. These *units* of the
    resource correspond to the two counters. Because both clerks cannot be
    called ``Karen``, we have used a general name of ``Clerk``.


.. literalinclude:: bankprograms_OO/bank09_OO.py


The waiting times in this model are much shorter than those for the
single service counter. For example, the waiting time for
``Customer02`` has been reduced from ``51.213`` to ``12.581``
minutes. Again we have too few customers processed to draw general
conclusions.

.. literalinclude:: bankprograms/bank09.out



.. ---------------------------------------------------------------
.. index::
   pair: Several queues; Resource
   single: bank10_OO

Several Counters with individual queues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each counter is now assumed to have its own queue.  The programming is
more complicated because the customer has to decide which queue to
join. The obvious technique is to make each counter a separate
resource and it is useful to make a list of resource objects (line
56).

In practice, a customer will join the shortest queue.  So we define
the Python function, ``NoInSystem(R)`` (lines 17-19) which
returns the sum of the number waiting and the number being served for
a particular counter, ``R``. This function is used in line 28 to
list the numbers at each counter. It is then easy to find which
counter the arriving customer should join. We have also modified the
trace printout, line 29 to display the state of the system when
the customer arrives. We choose the shortest queue in lines
30-33 (the variable ``choice``).

The rest of the program is the same as before.

..
    Each counter is now assumed to have its own queue.  The programming is
    more complicated because the customer has to decide which queue to
    join. The obvious technique is to make each counter a separate
    resource and it is useful to make a list of resource objects (line
    56).

    In practice, a customer will join the shortest queue.  So we define
    the Python function, ``NoInSystem(R)`` (lines 17-19) which
    returns the sum of the number waiting and the number being served for
    a particular counter, ``R``. This function is used in line 28 to
    list the numbers at each counter. It is then easy to find which
    counter the arriving customer should join. We have also modified the
    trace printout, line 29 to display the state of the system when
    the customer arrives. We choose the shortest queue in lines
    30-32 (the variable ``choice``).

    The rest of the program is the same as before.



.. literalinclude:: bankprograms_OO/bank10_OO.py


The results show how the customers choose the counter with the
smallest number. Unlucky ``Customer02`` who joins the wrong queue has
to wait until ``Customer00`` finishes at time ``55.067``. There are,
however, too few arrivals in these runs, limited as they are to five
customers, to draw any general conclusions about the relative
efficiencies of the two systems.

.. literalinclude:: bankprograms/bank10.out


.. ---------------------------------------------------------------

.. index:: Monitors, Gathering statistics, statistics


Monitors and Gathering Statistics
-------------------------------------


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
records the values of chosen variables as time series.
(but see the comments in `Final Remarks`_).



.. -------------------------------------------------------------

.. index::
   pair: Monitored; queue
   single: bank11_OO

The Bank with a Monitor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We now demonstrate a ``Monitor`` that records the average waiting
times for our customers. We return to the system with random arrivals,
random service times and a single queue and remove the old trace
statements.  In practice, we would make the printouts controlled by a
variable, say, ``TRACE`` which is set in the experimental data (or
read in as a program option - but that is a different story). This
would aid in debugging and would not complicate the data analysis. We
will run the simulations for many more arrivals.

In addition to the imports in the programs shown before, we now have
to import the ``Monitor`` class (line 2).

A Monitor, ``wM``, is created in line 37. We make the monitor an
attribute of the ``BankModel`` by the assignment to ``self.wM``.
The monitor ``observes`` the
waiting time mentioned in line 25. As the monitor is an attribute
of the ``BankModel`` to which the customer belongs,
``self.sim.wM`` can refere to it. We run
``maxNumber = 50`` customers (in the call of ``generate`` in line
39) and have increased ``maxTime`` to ``1000.0`` minutes.

..
    A Monitor, ``wM``, is created in line 42. It ``observes`` the
    waiting time mentioned in line 24.  We run
    ``maxNumber=50`` customers (in the call of ``generate`` in line
    45) and have increased ``maxTime`` to ``1000`` minutes.


.. literalinclude:: bankprograms_OO/bank11_OO.py

In previous programs, we have generated the ``BankModel``
anonymously. Here, we do it differently: we assign the ``BankModel``
object to the variable ``experi`` (line 53). This way,
we can reference its monitor attribute by ``experi.wM`` (line 58).
The average waiting time for 50 customers in this 2-counter system is
more reliable (i.e., less subject to random simulation effects) than
the times we measured before but it is still not sufficiently reliable for
real-world decisions. We should also replicate the runs using different
random number seeds. The result of this run is:

.. literalinclude:: bankprograms/bank11.out



.. -------------------------------------------------------------

.. index::
   single: Multiple runs, replications, bank12_OO
   single: Random Number Seed
   pair: model; function

Multiple runs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates the power of the object-oriented
approach. To get a number of independent measurements we must
replicate the runs using different random number seeds. Each
replication must be independent of previous ones both in the random
numbers and in the data collection so capability of creating
independent simulation models within one program is useful.

We do a standard ``from SimPy.Simulation import ...`` at #1. We define
``Source`` and  ``Customer`` as subclasses of ```Process``. These
differ in detail from the way they are defined in the classic
procedure-oriented version of SimPy. Each must refer to the simulation
environment it is running in, here the ``sim`` argument. Thus the
current time is returned by the ``self.sim.now()`` method (at #5

We define a ``BankModel`` as a sub-class of ``Simulation`` (at #8) and
create an object, ``mymodel``, of that class (at #14). A ``BankModel``
object has a ``run`` method and this is used for each independent
replication (at #16). Note that the ``BankModel`` is only generated
once (line 54). This is sufficient, as the ``run`` method freshly
generates an empty event list, a new counter resource, a new monitor,
and a new source. This way, all iterations are independent of each
other.

The random number seeds are stored in a list, ``seedVals`` and the
``for`` loop walks through this list and executes ``mymodel``'s
``run`` method for each entry to get a set of replications.

.. literalinclude:: bankprograms_OO/bank12_OO.py

The results show some variation. Remember, though, that the system is still
only operating for 50 customers so the system may not be in
steady-state.

.. literalinclude:: bankprograms/bank12.out


.. index::
   GUI input, Graphical Output,Statistical Output
   Priorities and Reneging,Other forms of Resource Facilities
   Advanced synchronization/scheduling commands


Final Remarks
-------------------------------------

This introduction is too long and the examples are getting
longer. There is much more to say about simulation with *SimPy* but no
space. I finish with a list of topics for further study:

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

I thank Klaus Muller, Bob Helmbold, Mukhlis Matti and other developers
and users of SimPy for improving this document by sending their
comments. I would be grateful for further suggestions or
corrections. Please send them to: *vignaux* at
*users.sourceforge.net*.

References
-------------------------------------

- Python website: https://www.python.org

- SimPy website: https://github.com/SimPyClassic/SimPyClassic


..
  ------------------------------------------------------


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
