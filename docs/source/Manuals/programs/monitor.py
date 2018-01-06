from SimPy.Simulation import Monitor
from random import expovariate

m = Monitor()        # define the Monitor object, m

for i in range(1000):    # make the observations
    y = expovariate(0.1)
    m.observe(y)

# set up and return the completed histogram
h = m.histogram(low=0.0, high=20, nbins=30)
