.. highlight:: python
   :linenothreshold: 5

========================================================
Publication-quality plot production with **matplotlib**
========================================================

This document deals with producing production-quality plots from SimPy
simulation  output using the **matplotlib** library. matplotlib is known to
work on Linux, Unix,  MS Windows and OS X platforms. This library is not part
of the SimPy distribution  and has to be downloaded and installed separately.

Simulation programs normally produce large quantities of output which needs to
be  visualized, e.g. by plotting. These plots can help with aggregating data,
e.g. for  detecting trends over time, frequency distributions or determining
the warm-up period  of a simulation model experiment.

SimPy's SimPlot plotting package is an easy to use, out-of-the-box capability
which can produce a full range of plot graphs on the screen and in PostScript
format. After installing SimPy, it can be used without installing any other
software. It is tightly integrated with SimPy, e.g. its Monitor data collection
class.

The SimPlot library is not intended to produce publication-quality plots. If
you want to publish your plots in a report or on the web, consider using an
external plotting library which can be called rom Python.


About matplotlib
====================

A very popular plotting library for Python is matplotlib. Its capabilities far
exceed those of SimPy's SimPlot. This is how matplotlib is described on its
home page:

    *"matplotlib is a python 2D plotting library which produces publication
    quality figures in a variety of hardcopy formats and interactive
    environments across platforms. matplotlib can be used in python scripts,
    the python and ipython shell (a la matlab or mathematica), web application
    servers, and six graphical user interface toolkits."*

The matplotlib screenshots (with Python code) at
https://matplotlib.org/gallery/index.html show the great range
of quality displays the library can produce with little coding. For the
investment in time in downloading, installing and learning matplotlib, the
SimPy user is rewarded with a powerful plotting capability.


Downloading matplotlib
--------------------------

Extensive installation instructions are provided at
https://matplotlib.org/users/installing.html


matplotlib input data
----------------------

matplotlib takes separate sequences (lists, tuples, arrays) for x- and
y-values. SimPlot, on the other hand, plots Monitor instances, i.e., lists of
[x,y] lists.

This difference in data structures is easy to overcome in SimPy by using the
Monitor functions ``yseries`` (returning the list of y-data) and ``tseries``
(returning the list of time- or x-data).


An example from the Bank Tutorial
-------------------------------------

As an example of how to use matplotlib with SimPy, a modified version of
bank12.py from the Bank Tutorial is used here. It produces a line plot of the
counter's queue length and a histogram of the customer wait times::

    #! /usr/local/bin/python
    """ Based on bank12.py in Bank Tutorial.
       This program uses matplotlib. It produces two plots:
       - Queue length over time
       - Histogram of queue length
    """
    from SimPy.Simulation import *
    import pylab as pyl
    from random import Random
    ## Model components
    class Source(Process):
        """ Source generates customers randomly"""
        def __init__(self,seed=333):
            Process.__init__(self)
            self.SEED = seed
        def generate(self,number,interval):
            rv = Random(self.SEED)
            for i in range(number):
                c = Customer(name = "Customer%02d"%(i,))
                activate(c,c.visit(timeInBank=12.0))
                t = rv.expovariate(1.0/interval)
                yield hold,self,t
    class Customer(Process):
        """ Customer arrives, is served and leaves """
        def __init__(self,name):
            Process.__init__(self)
            self.name = name
        def visit(self,timeInBank=0):
            arrive=now()
            yield request,self,counter
            wait=now()-arrive
            wate.observe(y=wait)
            tib = counterRV.expovariate(1.0/timeInBank)
            yield hold,self,tib
            yield release,self,counter
    class Observer(Process):
        def __init__(self):
            Process.__init__(self)
        def observe(self):
            while True:
                yield hold,self,5
                qu.observe(y=len(counter.waitQ))
    ## Model
    def model(counterseed=3939393):
        global counter,counterRV,waitMonitor
        counter = Resource(name="Clerk",capacity = 1)
        counterRV = Random(counterseed)
        waitMonitor = Monitor()
        initialize()
        sourceseed=1133
        source = Source(seed = sourceseed)
        activate(source,source.generate(100,10.0))
        ob=Observer()
        activate(ob,ob.observe())
        simulate(until=2000.0)
    qu=Monitor(name="Queue length")
    wate=Monitor(name="Wait time")
    ## Experiment data
    sourceSeed=333
    ## Experiment
    model()
    ## Output
    pyl.figure(figsize=(5.5,4))
    pyl.plot(qu.tseries(),qu.yseries())
    pyl.title("Bank12: queue length over time",
              fontsize=12,fontweight="bold")
    pyl.xlabel("time",fontsize=9,fontweight="bold")
    pyl.ylabel("queue length before counter",fontsize=9,fontweight="bold")
    pyl.grid(True)
    pyl.savefig(r".\bank12.png")

    pyl.clf()
    n, bins, patches = pyl.hist(qu.yseries(), 10, normed=True)
    pyl.title("Bank12: Frequency of counter queue length",
              fontsize=12,fontweight="bold")
    pyl.xlabel("queuelength",fontsize=9,fontweight="bold")
    pyl.ylabel("frequency",fontsize=9,fontweight="bold")
    pyl.grid(True)
    pyl.xlim(0,30)
    pyl.savefig(r".\bank12histo.png")

Here is the explanation of this program:

**Line number and explanation**

01
    Imports the matplotlib **pylab** module (this import form is needed to avoid
    namespace clashes with SimPy).

63
    Sets the size of the figures following to a width of 5.5 and a height of 4 inches.

64
    Plots the series of queue-length values (qu.yseries()) over their observation
    times series (qu.tseries()).

65
    Sets the figure title, its font size, and its font weight.

67
    Sets the x-axis label, its font size, and its font weight.

68
    Sets the y-axis label, its font size, and its font weight.

69
    Gives the graph a grid.

70
    Saves the plot under the given name.

72 	Clears the current figure (e.g., resets the axes values from the previous plot).

73
    Makes a histogram of the queue-length series (qu.series()) with 10 bins. The *normed*
    parameter makes the frequency counts relative to 1.

74
    Sets the title etc.

76
    Sets the x-axis label etc.

77
    Sets the y-axis label etc.

78
    Gives the graph a grid.

79
    Limits the x-axis to the range[0..30].

80
    Saves the plot under the given name.

Running the program above results in two PNG files. The first (``bank12.png``)
shows the queue length over time:

.. image:: /_static/images/matplotlib/bank12.png

The second output file (``bank12histo.png``) is a histogram of the customer
queue length at the counter:

.. image:: /_static/images/matplotlib/bank12histo.png


Conclusion
==============

The small example above already shows the power, flexibility and quality of the
graphics capabilities provided by matplotlib. Almost anything (fonts, graph
sizes, line types, number of series in one plot, number of subplots in a plot,
...) is under user control by setting parameters or calling functions.
Admittedly, it initially takes a lot of reading in the extensive documentation
and some experimentation, but the results are definitely worth the effort!
