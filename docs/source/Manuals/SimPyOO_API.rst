=============================================================
SimPy Classic's Object Oriented API
=============================================================

:Authors: - Klaus Muller <Muller@users.sourceforge.net>
:Release: |release|
:Python Version: 2.7 and later
:Date: |today|

.. contents:: Contents
   :depth: 2

.. highlight:: python
   :linenothreshold: 12

Introduction
=============

This document describes the object oriented (OO) programming
interface introduced with SimPy 2.0. This
is an add-on to the existing API, an alternative API. There is full backward compatibility:

Motivation
-------------

Many simulation languages support a procedural modelling style. Using them,
problems are decomposed into procedures (functions, subroutines) and either
represented by general components, such as queues, or represented in code
with data structures.

There are fundamental problems with using the procedural style of
modelling and simulation. Procedures do not correspond to real world
components. Instead, they correspond to methods and algorithms.
Mapping from the real (problem) world to the model and back is difficult
and not obvious, particularly for users expert in the problem domain, but
not in computer science. Perhaps the greatest limitation of the procedural
style is the lack of model extensibility. The only way in this style
to change simulation models is through functional extension. One can
add structural functionality but not alter any of its basic processes.

Right from its beginning, SimPy, on the other hand, has supported an
**object oriented approach** to simulation modelling.
In SimPy, models can be implemented as collections of autonomous,
cooperating objects.
These objects are self-sufficient and independent. The actions on these
objects are tied to the objects and their attributes. The object-oriented
capabilities of Python strongly support this encapsulation.

Why does this matter for simulation models? It helps with the mapping from
real-world objects and their activities to modelled objects and activities,
and back. This not only reduces the complexity of the models, it also
makes for easier validation of models and interpretation of simulation
results in real world terms.

The new API allows different, often more concise, cleaner program patterns.
It strongly supports the development of libraries
of model components for specific real world domains. It also supports
the re-use and extension of models when model specifications change.
In particular larger SimPy programs written with the advanced OO API should be
easier to maintain and extend. Users are advised to familiarize themselves
with this programming paradigm by reading the models in the
`SimPyModels` folder. Most of them are provided in two implementations, i.e. in the
existing and in the OO API. Similarly, the programs in the Bank tutorials
are provided with both APIs.

The advanced OO API has been developed very elegantly by Stefan Scherfke and
Ontje L |uumlaut| nsdorf, starting from SimPy 1.9. Thanks, guys, for this great job!

.. |uumlaut| unicode:: U+00FC
   :trim:

Readers of this document should be familiar with the basics of SimPy and
have read at least "Basic SimPy - Manual For First Time Users". They should
also know how subclassing is done in Python.

Basic SimPy OO API Design
==========================

A class ``Simulation`` has been added to module ``SimPy.Simulation``.
``SimulationTrace``, ``SimulationStep`` and  ``SimulationRT`` are subclasses of
``Simulation``. Multiple instances of these classes can co-exist in a SimPy program.

Backward compatibility
-----------------------------

Since SimPy 2.0, the package offers both the existing procedural API and an 
object-oriented API
where simulation capabilities are provided by instantiating ``Simulation``.
``SimulationTrace``, ``SimulationStep`` or  ``SimulationRT`` are subclasses of
``Simulation``.

Each ``SimulationXX`` instance has its own event list and therefore its own simulation time.
A ``SimulationXX`` instance can effectively be considered as a simulated, isolated parallel
world. Any *Process*, *Resource*, *Store*, *Level*, *Monitor*, *Tally* or *SimEvent*
instance belongs to one and only one world (i.e., ``Simulationxx`` instance).

The following program shows what this means for API and program structure:

.. literalinclude:: programs/SimPyOO_car.py


Using the existing API, the following program is semantically the same and also works
under the OO version:

.. literalinclude:: programs/SimPyOO_car_traditional.py


This full (backwards) compatibility is achieved by the automatic generation
of a *SimulationXX* instance "behind the scenes".

Models as SimulationXX subclasses
-----------------------------------

The advanced OO API can be used to generate model classes which are SimulationXX subclasses.
This ties a model and a SimulationXX instance together beautifully. See the following
example:

.. literalinclude:: programs/CarModel.py


class ``Model`` here is a subclass of ``Simulation``. Every model execution, i.e. call to
``runModel``, reinitializes the simulation (creates an empty event list and sets
the time to 0) (see line 24). ``runModel`` can thus be called repeatedly for multiple runs of
the same experiment setup::

    if __name__=="__main__":

        ## Experiments ---------------------------------

        myModel = Model(name="Experiment 1", nrCars=10, spaces=5)
        for repetition in range(100):

        ## One Experiment -------------------------------

            myModel.runModel()
            print(myModel.now())

Model extension by subclassing
---------------------------------

With the advanced OO API, it is now very easy and clean to extend a model by subclassing. This
effectively allows the creation of model libraries.

For example, the model in the previous example can be extended to one in which also vans
compete for parking spaces. This is done by importing the ``CarModel`` module
and subclassing ``Model`` as follows:

.. literalinclude:: programs/CarModelExtension.py


Let's walk through this:

*Lines 9-14*:
    Addition of a ``Van`` class with a ``park`` PEM.

*Line 20*:
    Definition of a subclass ``ModelExtension`` which extends class ``Model``.

*Lines 22-23*:
    Initialization of the model class (``Model``) from which ``ModelExtension``
    is derived. When subclassing a class in Python, this is always necessary:
    Python does **not** automatically initialize the super-class.

*Lines 25-36*:
    Defines a ``runModel`` method for ``ModelExtension`` which also generates
    and activates ``Van`` objects.

API changes
============

Module ``SimPy.Simulation``
-----------------------------------

The only change to the API of module ``SimPy.Simulation``
is the addition of class ``Simulation``::

 Module SimPy.Simulation:
    ################ Unchanged ################
    ## yield-verb constants --------------------
    get
    hold
    passivate
    put
    queueevent
    release
    request
    waitevent
    waituntil
    ## version constant ------------------------
    version
    ## classes ---------------------------------
    FatalSimerror
    Simerror
    ################ Added ################
    Simulation

Thus, after the import::

   from SimPy.Simulation import *

class ``Simulation`` is available to a program.

Actually,::

   from SimPy.Simulation import Simulation

is sufficient and even clearer.

class ``Simulation``
~~~~~~~~~~~~~~~~~~~~~

The simulation capabilities of a model are provided by instantiating class
``Simulation`` like this::

  from SimPy.Simulation import *

  aSimulation = Simulation()
  ## model code follows

Better OO programming style is actually to define a model class which inherits
from ``Simulation``::

    import SimPy.Simulation as Simulation

    class MyModel(Simulation.Simulation):
        def run(self):
            self.initialize()
            ## model code follows

    myMo = MyModel()
    myMo.run()

The ``self.initialize()`` is not really necessary, as the ``Simulation`` instance is
initialized at generation time. If method ``run`` for a model (here ``myMo`` ) is
executed more than once, e.g. for running a simulation repeatedly, ``self.initialize()``
resets the model to an empty event list and simulation time 0.

Methods of class Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ``Simulation`` has these methods::

  class Simulation:
    ## Methods ----------------------------------
    __init__(self)
    initialize(self)
    now(self)
    stopSimulation(self)
    allEventNotices(self)
    allEventTimes(self)
    activate(self, obj, process, at='undefined', delay='undefined', prior=False)
    reactivate(self, obj, at='undefined', delay='undefined', prior=False)
    startCollection(self, when=0.0, monitors=None, tallies=None)
    simulate(self, until=0)

The semantics and parameters (except for ``self``) of the methods are identical to those of the non-OO
``SimPy.Simulation`` functions of the same name. For example, to get the current
simulation time of a Simulation object ``so``, the call is::

  tcurrent = so.now()

..
    New classes
    ------------

    class ``Simulation``
    ~~~~~~~~~~~~~~~~~~~~~

    The simulation capabilities are provided by instantiating class ``Simulation``. The three
    other SimPy run modes (``SimulationTrace``, ``SimulationRT`` and ``SimulationStep``) are
    subclasses of ``Simulation``.

    Methods of class ``Simulation``
    ++++++++++++++++++++++++++++++++

    The semantics and parameters of the methods are identical to those of the non-OO
    ``SimPy.Simulation`` functions of the same name.

    - *initialize*

    - *activate*

    - *reactivate*

    - *simulate*

    - *now*

    - *stopSimulation*

    - *startCollection*

    - *allEventNotices*

    - *allEventTimes*

    Example calls (snippet)::

       from SimPy.Simulation import *
       s = Simulation()
       s.initialize()
       s.simulate(until=100)

Module ``SimPy.SimulationTrace``
----------------------------------------------

The only change to the API of module ``SimPy.SimulationTrace``
is the addition of class ``SimulationTrace``::

  Module SimPy.SimulationTrace:
    ################ Unchanged ################
    ## yield-verb constants --------------------
    get
    hold
    passivate
    put
    queueevent
    release
    request
    waitevent
    waituntil
    ## version constant ------------------------
    version
    ## classes ---------------------------------
    FatalSimerror
    Simerror
    Trace
    ################ Added ################
    SimulationTrace


class ``SimulationTrace``
~~~~~~~~~~~~~~~~~~~~~~~~~

The simulation capabilities of a model with tracing are provided by instantiating class
``SimulationTrace`` like this::

  from SimPy.SimulationTrace import SimulationTrace

  aSimulation = SimulationTrace()
  ## model code follows

Again, better OO programming style is actually to define a model class which inherits
from Simulation::

    from SimPy.SimulationTrace import SimulationTrace

    class MyModel(SimulationTrace):
        def run(self):
            self.initialize()
            # model code follows

    myMo = MyModel()
    myMo.run()

class ``SimulationTrace`` is a subclass of ``Simulation`` and thus
provides the same methods, albeit with tracing added.

The semantics and parameters of the methods are identical to those of the non-OO
``SimPy.SimulationTrace`` functions of the same name.

Methods and attributes of class SimulationTrace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  class SimulationTrace:
     ## Methods ----------------------------------
     __init__(self)
     initialize(self)
     now(self)
     stopSimulation(self)
     allEventNotices(self)
     allEventTimes(self)
     activate(self, obj, process, at='undefined', delay='undefined', prior=False)
     reactivate(self, obj, at='undefined', delay='undefined', prior=False)
     startCollection(self, when=0.0, monitors=None, tallies=None)
     simulate(self, until=0)
     ## trace attribute ---------------------------
     trace

Attribute ``trace``
++++++++++++++++++++

An initialization of class ``SimulationTrace`` generates an instance of
class ``Trace``. This becomes an attribute ``trace`` of the ``SimulationTrace``
instance.

``Trace`` methods
+++++++++++++++++++++

The semantics and parameters of the ``Trace`` methods are identical to those of
the non-OO ``SimPy.SimulationTrace`` ``trace`` instance of the same name.

- trace.start(self)

Example::

    s.trace.start()

- trace.stop(self)

- trace.treset(self)

- trace.tchange(self, \*\*kmvar)

- trace.ttext(self,par)

Example calls (snippet)::

   from SimPy.SimulationTrace import SimulationTrace
   s = SimulationTrace()
   s.initialize()
   s.trace.ttext("Here we go")

Again, note that you have to qualify the ``trace`` instance (see e.g. the last line
of the snippet) with the ``SimulationTrace`` instance, here ``s``.

Module ``SimPy.SimulationRT``
----------------------------------------------

class ``SimulationRT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simulation capabilities plus real time  synchronization are provided by instantiating
class ``SimulationRT``.

Methods of class ``SimulationRT``
+++++++++++++++++++++++++++++++++++++++

The ``SimulationRT`` subclass adds two methods to those inherited
from ``Simulation``.

The semantics and parameters of the methods are identical to those of the non-OO
``SimPy.SimulationRT`` functions of the same name.

- rtnow

- rtset

Example calls (snippet)::

   from SimPy.SimulationRT import Process, hold
   class Car(Process):
      def __init__(self):
         Process.__init__(self, sim=self.sim)
      def run(self):
         print(self.sim.rtnow())
         yield hold, self, 10


class ``SimulationStep``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simulation capabilities plus event stepping are provided by instantiating
class ``SimulationStep``.

Methods of class ``SimulationStep``
+++++++++++++++++++++++++++++++++++++++

The ``SimulationStep`` subclass adds three methods to those inherited
from ``Simulation``.

The semantics and parameters of the methods are identical to those of the non-OO
``SimPy.SimulationStep`` functions of the same name.

- startStepping

- stopStepping

- simulateStep

Example call (snippet)::

   from SimPy.SimulationStep import *
   s = SimulationStep()
   s.initialize()
   s.simulateStep(until=100, callback=myCallBack)


Classes with a ``SimulationXX`` attribute
------------------------------------------

All SimPy entity (*Process*, *Resource*, *Store*, *Level*, *SimEvent*)
and monitoring (*Monitor*, *Tally*) classes have time-related functions.
In the OO-API of SimPy, they therefore have a ``.sim`` attribute which is a
reference to the *SimulationXX* instance to which they belong. This association
is made by providing that reference as a parameter to the constructor of the class.

.. Important::
   **All class instances instances must refer to the same SimulationXX instance,
   i.e., their .sim attributes must have the same value. That value must be the
   reference to the SimulationXX instance.** Any deviation from this will
   lead to strange mis-functioning of a SimPy script.

The constructor calls (signatures) for the classes in question thus change as follows:

class ``Process``
~~~~~~~~~~~~~~~~~~

::

  Process.__init__(self, name = 'a_process', sim = None)

Example 1 (snippet)::

  class Car(Process):
      def drive(self):
         yield hold, self, 10
         print("Arrived at", self.sim.now())

  aSim = Simulation()
  aSim.initialize()
  c=Car(name="Mine", sim=aSim)

Example 2, with an ``__init__`` method (snippet)::

  class Car(Process):
     def __init__(self, name):
         Process.__init__(self, name=name, sim=self.sim)

  aSim = Simulation()
  aSim.initialize()
  c=Car(name="Mine", whichSim=aSim)

class ``Resource``
~~~~~~~~~~~~~~~~~~~~~

::

    Resource.__init__(self, capacity=1, name='a_resource',
                      unitName='units',
                      qType=FIFO, preemptable=0, monitored=False,
                      monitorType=Monitor, sim=None)

Example (snippet)::

  aSim = Simulation()
  aSim.initialize()
  res = Resource(name="Server", sim=aSim)

classes ``Store`` and ``Level``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store::

    Store.__init__(self, name=None, capacity='unbounded', unitName='units',
                   putQType=FIFO, getQType=FIFO,
                   monitored=False, monitorType=Monitor, initialBuffered=None,
                   sim=None)

Level::

    Level.__init__(self, name=None, capacity='unbounded', unitName='units',
                   putQType=FIFO, getQType=FIFO,
                   monitored=False, monitorType=Monitor, initialBuffered=None,
                   sim=None)

Example (snippet)::

  aSim = Simulation()
  aSim.initialize()
  buffer = Store(name="Parts", sim=aSim)

class ``SimEvent``
~~~~~~~~~~~~~~~~~~~~~~

::

  SimEvent.__init__(self, name='a_SimEvent', sim=None)

Example (snippet)::

  aSim = Simulation()
  aSim.initialize()
  evt = SimEvent("Boing!", sim=aSim)

classes ``Monitor`` and ``Tally``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor::

    Monitor.__init__(self, name='a_Monitor', ylab='y', tlab='t', sim=None)

Tally::

    Tally.__init__(self, name='a_Tally', ylab='y', tlab='t', sim=None)

Example (snippet)::

  aSim = Simulation()
  aSim.initialize()
  myMoni = Monitor(name="Counting cars", sim=aSim)
