from SimPy.Simulation import Tally
from random import expovariate

r = Tally('Tally')  # define a tally object, r
r.setHistogram(name='exponential',
               low=0.0, high=20.0, nbins=30)  # set before observations

for i in range(1000):    # make the observations
    y = expovariate(0.1)
    r.observe(y)

h = r.getHistogram()     # return the completed histogram
print(h)
