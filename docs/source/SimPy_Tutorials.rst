=======================
SimPy Classic Tutorials
=======================

There are two styles of modelling using SimPy. The first, which we
call the Classical style, uses user-defined Process objects each
representing an active entity of the simulation.  The simulation is
started by creating one or more entities, activating their Process
Execution Methods and then, in a main block of the program, calling
the ``simulate()`` function to start the simulation. This simpler
style seems to be more acceptable to many users.

In the second style, referred to as the OO Style, a user-defined
object of a Simulation class is created and executed. This object
executes the whole simulation. This is particularly suitable for
running replications of the simulation and the execution of a
simulation object is independent of others.

.. toctree::
   :maxdepth: 1

   Tutorials/TheBank
   Tutorials/TheBank2
   Tutorials/TheBankOO
   Tutorials/TheBank2OO
   OnLineSimPyCourse

