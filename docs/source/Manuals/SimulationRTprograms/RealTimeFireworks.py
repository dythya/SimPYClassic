""" RealTimeFireworks.py """
from SimPy.SimulationRT  import *
from random import *
import time
## Model components -----------------------------------------------------------
class Launcher(Process):
	def launch(self):
		while True:
			print("Launch at %2.2f; wallclock: %2.2f"%(now(),time.clock()-startTime))
			yield hold,self,uniform(1,maxFlightTime)
			print("Boom!!! Aaaah!! at %2.2f; wallclock: %2.2f"\
			       %(now(),time.clock()-startTime))
def model():
	initialize()
	for i in range(nrLaunchers):
		lau=Launcher()
		activate(lau,lau.launch())
	simulate(real_time=True,rel_speed=1,until=20) ##unit sim time = 1 sec clock
## Experiment data  -----------------------------------------------------------   
nrLaunchers=2
maxFlightTime=5.0 
startTime=time.clock()
seed(1234567)
## Experiment ----------------------------------------------------------------- 
model()
