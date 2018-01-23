"""
Movie_renege

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
        yield ((request, self, ticketCounter),
               (waitevent, self, soldOut[whichMovie]))
        if self.acquired(ticketCounter):
            if available[whichMovie] >= nrTickets:
                available[whichMovie] -= nrTickets
                if available[whichMovie] < 2:
                    soldOut[whichMovie].signal()
                    whenSoldOut[whichMovie] = now()
                    available[whichMovie] = 0
                yield hold, self, 1
            else:
                yield hold, self, 0.5
            yield release, self, ticketCounter
        else:
            nrRenegers[whichMovie] += 1


class CustomerArrivals(Process):
    def traffic(self):
        while now() < 120:
            yield hold, self, expovariate(1 / 0.5)
            movieChoice = choice(movies)
            nrTickets = randint(1, 6)
            if available[movieChoice]:
                m = MovieGoer()
                activate(m, m.getTickets(
                    whichMovie=movieChoice, nrTickets=nrTickets))


# Experiment data -------------------------
seed(111333555)
movies = ["Gone with the Windows", "Hard Core Dump", "Modern CPU Times"]

available = {}
soldOut = {}
nrRenegers = {}
whenSoldOut = {}
for film in movies:
    available[film] = 50
    soldOut[film] = SimEvent(film)
    nrRenegers[film] = 0
ticketCounter = Resource(capacity=1)

# Model/Experiment ------------------------------
print('Movie_renege')
initialize()
c = CustomerArrivals()
activate(c, c.traffic())
simulate(until=120)

for f in movies:
    if soldOut[f]:
        FMT = ("Movie '{0}' sold out {1:.0f} minutes after ticket counter "
               "opening.")
        print(FMT.format(f, int(whenSoldOut[f])))
        FMT = "\tNr people leaving queue when film '{0}' sold out: {1}"
        print(FMT.format(f, nrRenegers[f]))
