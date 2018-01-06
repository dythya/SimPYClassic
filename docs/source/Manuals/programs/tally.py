from SimPy.Simulation import Tally
import random as r

t = Tally(name="myTally", ylab="wait time (sec)")
t.setHistogram(low=0.0, high=1.0, nbins=10)
for i in range(100000):
    t.observe(y=r.random())
print(t.printHistogram(fmt="%6.4f"))
