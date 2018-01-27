=============================================================
Running SimPy on Multiple Processors with **Parallel Python**
=============================================================

.. contents:: Contents
   :depth: 2

Introduction
=============

With SimPy 2.0, you can easily increase the performance of your simulation by
using `Parallel Python`_ if you have a larger number of independent processors
(multiple CPUs or cores). *Parallel Python* can distribute the execution of
your SimPy processes to all cores of your CPU and even to other computers. You
should read the PP documentation for further information on how this works.

.. _`Parallel Python`: https://www.parallelpython.com/

Please, note that *Parallel Python* is not included in the SimPy  distribution
and needs to be `downloaded <https://www.parallelpython.com/>` and installed
separately.

Examples
=============

Example #1
-----------------

The files PPExample.txt_ and PPExampleProcess.txt_ contain a small example
with several car processes. It is important, that processes etc.are not
defined in the file that starts the PP job server and executes the jobs,
since ``ppserver.submit()`` only takes functions defined in the same file and
module names to import, but no classes.

PPExample.py::

    """
    Example for SimPy with Parallel Python.
    """

    import PPExampleProcess
    from SimPy.Simulation import *
    import pp


    def runSimulation(jobNum, numCars):
        sim = SimPy.Simulation.Simulation()
        cars = []
        for i in range(numCars):
            car = PPExampleProcess.Car(sim, i * jobNum + i)
            sim.activate(car, car.run(), at = 0)
            cars.append(car)
        sim.simulate(until = 30)


    server = pp.Server(ppservers = ())
    for i in range(4):
        job = server.submit(
                            runSimulation,
                            (i, 2),
                            (),
                            ('SimPy.Simulation', 'PPExampleProcess'))
        job()

PPExampleProcess.py::

    from SimPy.Simulation import *

    class Car(Process):

        def __init__(self, sim, id):
            Process.__init__(self, sim = sim)
            self.id = id

        def run(self):
            while True:
                yield hold, self, 10
                print 'Car #%i at t = %i' % (self.id, self.sim.now())

.. _PPExample.txt: ../../../_static/PPExample.txt
.. _PPExampleProcess.txt: ../../../_static/PPExampleProcess.txt

The simulated process in this case is a simple car, that holds for ten steps
and then prints the current simulation time. Obviously, each car process is
independent from the other ones. Thus if we want to simulate a great number of
cars, we can easily distribute the processes to many CPU cores and others
computers in our network.

PP pickles everything it sends to other cores/computers. Since SimPy is
currently not pickleable, you cannot submit ``Simulation.simulate()`` to the
PPServer. In this example ``runSimulation`` is defined and submitted to the
server. The code within it will be executed on each core/computer. In the
example we create four simulation jobs with two cars for each job.

Run PPExample.py to execute the example.

Example #2
------------

Files simulator.txt_ and processes.txt_ contain an example that
simulates refrigerators in single-thread and in parallel simulation mode.

Class ``Simulator`` simulates a number of fridges and gets the resulting data.

Class ``ParallelSimulator`` simulates a number of fridges and gets the resulting data.
A number of jobs will be created that use all available
CPU cores or even other computers.

To use clustering, ParallelPython needs to be installed on all computers
and the server demon "ppserver.py" must be started. The list of the servers'
IP addresses must then be passed to the constructor of this class.

Run ``simulator.py`` to execute this example.

.. _simulator.txt: ../../../_static/simulator.txt
.. _processes.txt: ../../../_static/processes.txt

File simulator.py::

    # coding=utf8
    """
    The fridge simulation

    @author: Stefan Scherfke
    @contact: stefan.scherfke at uni-oldenburg.de
    """

    from time import clock
    import logging

    from SimPy.Simulation import Simulation, activate, initialize, simulate
    import pp

    from processes import Fridge, FridgeObserver

    log = logging.getLogger('Simulator')

    class Simulator(object):
        """
        This class simulates a number of fridges and gets the resulting data.
        """

        def __init__(self, numFridges, tau, aggSteps, duration):
            """
            Setup the simulation with the specified number of fridges.

            Tau specifies the simulation step for each frige. Furthermore the
            observer will collect data each tau. Collected data
            will be aggregated at the end of each aggSteps simulation steps.

            @param numFridges: The number of simulated fridges
            @type numFridges:  unsigned int
            @param tau: simulation step size for collecting data and simulating
                        the fridge
            @type tau:  float
            @param aggSteps: Collected data will be aggregated each aggSteps
                             simulation steps. Signals interval will be
                             tau * aggSteps
            @type aggSteps:  unsigned int
            @param duration: Duration of the simulation in hours
            @type duration:  unsigned int
            """
            log.info('Initializing simulator ...')
            self.simEnd = duration
            self.sim = Simulation()

            fridgeProperties = {'tau': tau}
            self._fridges = []
            for i in range(numFridges):
                fridge = Fridge(self.sim, **fridgeProperties)
                self._fridges.append(fridge)
            self._observer = FridgeObserver(self.sim, self._fridges, tau, aggSteps)

        def simulate(self):
            """
            Initialize the system, start the simulation and return the collected
            data.

            @return: The fridgerators consumption after each aggregation
            """
            log.info('Running simulation ...')
            self.sim.initialize()
            for fridge in self._fridges:
                self.sim.activate(fridge, fridge.run(), at = 0)
            self.sim.activate(self._observer, self._observer.run(), at = 0)
            self.sim.simulate(until = self.simEnd)

            log.info('Simulation run finished.')
            return self._observer.getData()


    class ParallelSimulator(object):
        """
        This class simulates a number of fridges and gets the resulting data.
        Unlike simulator, a number of jobs will be created that use all availale
        CPU cores or even other computers.

        To use clustering, ParallelPython needs to be installed on all computers
        and the server demon "ppserver.py" must be started. The list of the server's
        IPs must then be passed to the constructor of this class.
        """

        def __init__(self, numFridges, tau, aggSteps, duration,
                jobSize = 100, servers = ()):
            """
            Setup the simulation with the specified number of fridges. It will be
            split up in several parallel jobs, each with the specified number of
            jobs.

            Tau specifies the simulation step for each frige. Furthermore the
            observer will collect data each tau. Collected data
            will be aggregated at the end of each aggSteps simulation steps.

            @param numFridges: The number of simulated fridges
            @type numFridges:  unsigned int
            @param tau: simulation step size for collecting data and simulating
            the fridge
            @type tau:  float
            @param aggSteps: Collected data will be aggregated each aggSteps
            simulation steps. Signals interval will be
            tau * aggSteps
            @type aggSteps:  unsigned int
            @param duration: Duration of the simulation
            @type duration:  unsigned int
            @param jobSize: The number of friges per job, defaults to 100.
            @type jobSize: unsigned int
            @param servers: A list of IPs from on which the simulation shall be
                            executed. Defaults to "()" (use only SMP)
            @type servers:  tuple of string
            """
            log.info('Initializing prallel simulation ...')

            self._jobSize = jobSize
            self._servers = servers
            self._numFridges = numFridges
            self._tau = tau
            self._aggSteps = aggSteps
            self.simEnd = duration

        def simulate(self):
            """
            Create some simulation jobs, run them and retrieve their results.

            @return: The fridgerators consumption after each aggregation
            """
            log.info('Running parallel simulation ...')
            oldLevel = log.getEffectiveLevel() # pp changes the log level :(
            jobServer = pp.Server(ppservers = self._servers)

            # Start the jobs
            remainingFridges = self._numFridges
            jobs = []
            while remainingFridges > 0:
                jobs.append(jobServer.submit(self.runSimulation,
                        (min(self._jobSize, remainingFridges),),
                        (),
                        ("logging", "SimPy.Simulation", "processes")))
                remainingFridges -= self._jobSize
            log.info('Number of jobs for simulation: %d' % len(jobs))

            # Add each job's data
            pSum = [0] * int((60 / self._aggSteps) * self.simEnd)
            for job in jobs:
                data = job()
                for i in range(len(data)):
                    pSum[i] += data[i]
            for s in pSum:
                s /= len(jobs)

            log.setLevel(oldLevel)
            log.info('Parallel simulation finished.')
            return pSum

        def runSimulation(self, numFridges):
            """
            Create a job with the specified number of fridges and controllers and
            one observer. Simulate this and return the results.

            @param numFridges: The number of fridges to use for this job
            @type numFridges:  unsigned int
            @return: A list with the aggregated fridge consumption
            """
            sim = SimPy.Simulation.Simulation()
            sim.initialize()

            fridgeProperties = {'tau': self._tau}
            fridges = []
            for i in range(numFridges):
                fridge = processes.Fridge(sim, **fridgeProperties)
                fridges.append(fridge)
                sim.activate(fridge, fridge.run(), at = 0)
            observer = processes.FridgeObserver(sim,
                    fridges, self._tau, self._aggSteps)
            sim.activate(observer, observer.run(), at = 0)

            sim.simulate(until = self.simEnd)
            return observer.getData()


    if __name__ == '__main__':
        logging.basicConfig(
                level = logging.INFO,
                format = '%(asctime)s %(levelname)8s: %(name)s: %(message)s')

        numFridges = 5000
        tau = 1./60
        aggStep = 15
        duration = 4 + tau

        sim = Simulator(numFridges, tau, aggStep, duration)
        data = sim.simulate()
        log.info('Results: ' + str(data))

        servers = ()
        sim = ParallelSimulator(numFridges, tau, aggStep, duration, 100, servers)
        data = sim.simulate()
        log.info('Results: ' + str(data))

File process.py::

    # coding=utf8
    """
    This file contains classes for simulating, controlling and observing a fridge.

    @author: Stefan Scherfke
    @contact: stefan.scherfke at uni-oldenburg.de
    """

    from math import exp
    import logging
    import random

    from SimPy.Simulation import Process, Simulation, \
            activate, hold, initialize, now, simulate

    log = logging.getLogger('Processes')

    class Fridge(Process):
        """
        This class represents a simulated fridge.

        It's temperature T for and equidistant series of time steps is computed by
        $T_{i+1} = \epsilon \cdot T_i + (1 - \epsilon) \cdot \left(T^O - \eta
        \cdot \frac{q_i}{A}\right)$ with $\epsilon = e^{-\frac{\tau A}{m_c}}$.
        """

        def __init__(self, sim, T_O = 20.0, A = 3.21, m_c = 15.97, tau = 1.0/60,
                      eta = 3.0, q_i = 0.0, q_max = 70.0,
                      T_i = 5.0, T_range = [5.0, 8.0], noise = False):
            """
            Init all required variables.

            @param sim:       The SimPy simulation this process belongs to
            @type sim:        SimPy.Simulation
            @param T_O:       Outside temperature
            @param A:         Insulation
            @param m_c:       Thermal mass/thermal storage capacity
            @param tau:       Time span between t_i and t_{i+1}
            @param eta:       Efficiency of the cooling device
            @param q_i:       Initial/current electrical power
            @param q_max:     Power required during cool-down
            @param T_i:       Initial/current temperature
            @param T_range:   Allowed range for T_i
            @param noise:     Add noise to the fridge's parameters, if True
            @type noise:      bool
            """
            Process.__init__(self, sim = sim)
            self.T_O = T_O
            self.A = A
            self.m_c = random.normalvariate(20, 4.5) if noise else m_c
            self.tau = tau
            self.eta = eta
            self.q_i = q_i
            self.q_max = q_max
            self.T_i = random.uniform(T_range[0], T_range[1]) if noise else T_i
            self.T_range = T_range

        def run(self):
            """
            Calculate the fridge's temperature for the current time step.
            """
            while True:
                epsilon = exp(-(self.tau * self.A) / self.m_c)
                self.T_i = epsilon * self.T_i + (1 - epsilon) \
                        * (self.T_O - self.eta * (self.q_i / self.A))
                if self.T_i >= self.T_range[1]:
                    self.q_i = self.q_max         # Cool down
                elif self.T_i <= self.T_range[0]:
                    self.q_i = 0.0                # Stop cooling
                log.debug('T_i: %2.2f°C at %.2f' % (self.T_i, self.sim.now()))
                yield hold, self, self.tau

        def coolDown(self):
            """
            Start cooling down now!
            """
            self.q_i = self.q_max


    class FridgeObserver(Process):
        """
        This process observes the temperature and power consumption of a set of
        fridges.
        """

        def __init__(self, sim, fridges, tau, aggSteps):
            """
            Init the observer.

            @param sim: The SimPy simulation this process belongs to
            @type sim:  SimPy.Simulation
            @param fridges: A list of fridges to be observed
            @type fridges: tuple of Fridge
            @param tau: Time interval for observations
            @type tau: float
            @param aggSteps: Specifies after how many timesteps tau the collected
                             data is aggregated and stored.
            @type aggSteps: int
            """
            Process.__init__(self, sim = sim)
            self._fridges = fridges
            self._tau = tau
            self._aggSteps = aggSteps
            self._data = []

        def run(self):
            """
            Start observation
            """
            aggSteps = 0
            consumption = 0
            lastProgUpdate = 0
            while True:
                prog = self.sim.now() * 100 / self.sim._endtime
                if int(prog) > lastProgUpdate:
                    log.info('Progress: %d%%' % prog)
                    lastProgUpdate = prog
                if (aggSteps >= self._aggSteps):
                    log.debug('Aggregating at %.2f' % self.sim.now())
                    self._data.append(consumption/self._aggSteps)
                    consumption = 0
                    aggSteps = 0

                for fridge in self._fridges:
                    consumption += fridge.q_i
                aggSteps += 1
                yield hold, self, self._tau

        def getData(self):
            """
            Return the collected data

            @return: a list with the collected data
            """
            return self._data


    if __name__ == '__main__':
        logging.basicConfig(
                level = logging.DEBUG,
                format = '%(levelname)-8s %(asctime)s %(name)s: %(message)s')

        tau = 1./60 # Step size 1min
        aggSteps = 15 # Aggregate consumption in 15min blocks
        params = {'tau': tau}

        sim = Simulation()

        fridge = Fridge(sim, **params)
        observer = FridgeObserver(sim, [fridge], tau, aggSteps)

        sim.activate(fridge, fridge.run(), at = 0)
        sim.activate(observer, observer.run(), at = 0)
        sim.simulate(until = 4 + tau)
        print observer.getData()
