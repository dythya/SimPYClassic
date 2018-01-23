"""Movie_renege.py

Demo program to show event-based reneging by
'yield (request,self,res),(waitevent,self,evt)'.

Scenario:
A movie theatre has one ticket counter selling tickets for
three movies (next show only). When a movie is sold out, all
people waiting to buy ticket for that movie renege (leave queue).
"""
from SimPy.Simulation import *
from random import *

# Model components ------------------------


class MovieGoer(Process):
    def getTickets(self, whichMovie, nrTickets):
        yield ((request, self, self.sim.ticketCounter),
               (waitevent, self, self.sim.soldOut[whichMovie]))
        if self.acquired(self.sim.ticketCounter):
            if self.sim.available[whichMovie] >= nrTickets:
                self.sim.available[whichMovie] -= nrTickets
                if self.sim.available[whichMovie] < 2:
                    self.sim.soldOut[whichMovie].signal()
                    self.sim.whenSoldOut[whichMovie] = self.sim.now()
                    self.sim.available[whichMovie] = 0
                yield hold, self, 1
            else:
                yield hold, self, 0.5
            yield release, self, self.sim.ticketCounter
        else:
            self.sim.nrRenegers[whichMovie] += 1


class CustomerArrivals(Process):
    def traffic(self):
        while self.sim.now() < 120:
            yield hold, self, expovariate(1 / 0.5)
            movieChoice = choice(movies)
            nrTickets = randint(1, 6)
            if self.sim.available[movieChoice]:
                m = MovieGoer(sim=self.sim)
                self.sim.activate(m, m.getTickets(
                    whichMovie=movieChoice, nrTickets=nrTickets))


# Experiment data -------------------------
seed(111333555)
movies = ["Gone with the Windows", "Hard Core Dump", "Modern CPU Times"]

# Model -----------------------------------


class MovieRenegeModel(Simulation):
    def run(self):
        print('Movie_renege')
        self.initialize()
        self.available = {}
        self.soldOut = {}
        self.nrRenegers = {}
        self.whenSoldOut = {}
        for film in movies:
            self.available[film] = 50
            self.soldOut[film] = SimEvent(film, sim=self)
            self.nrRenegers[film] = 0
        self.ticketCounter = Resource(capacity=1, sim=self)
        c = CustomerArrivals(sim=self)
        self.activate(c, c.traffic())
        self.simulate(until=120)


# Experiment ------------------------------
model = MovieRenegeModel()
model.run()

# Analysis/output -------------------------
for f in movies:
    if model.soldOut[f]:
        FMT = ("Movie '{0}' sold out {1:.0f} minutes after ticket counter "
               "opening.")
        print(FMT.format(f, int(model.whenSoldOut[f])))
        FMT = "\tNr people leaving queue when film '{0}' sold out: {1}"
        print(FMT.format(f, model.nrRenegers[f]))
