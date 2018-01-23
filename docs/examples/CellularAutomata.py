from SimPy.Simulation import *
"""CellularAutomata.py
Simulation of two-dimensional cellular automata. Plays game of Life.
"""


class Autom(Process):
    def __init__(self, coords):
        Process.__init__(self)
        self.x = coords[0]
        self.y = coords[1]
        self.state = False

    def nrActiveNeighbours(self, x, y):
        nr = 0
        coords = [(xco + x, yco + y) for xco in (-1, 0, 1)
                  for yco in (-1, 0, 1) if not (xco == 0 and yco == 0)]

        for a_coord in coords:
            try:
                if cells[a_coord].state:
                    nr += 1
            except KeyError:
                # wrap around
                nux = divmod(a_coord[0], size)[1]
                nuy = divmod(a_coord[1], size)[1]
                if cells[(nux, nuy)].state:
                    nr += 1
        return nr

    def decide(self, nrActive):
        return (self.state and (nrActive == 2 or nrActive == 3) or
                               (nrActive == 3))

    def celllife(self):
        while True:
            # calculate next state
            temp = self.decide(self.nrActiveNeighbours(self.x, self.y))
            yield hold, self, 0.5
            # set next state
            self.state = temp
            yield hold, self, 0.5


class Show(Process):
    def __init__(self):
        Process.__init__(self)

    def picture(self):
        while True:
            print("Generation {0}".format(now()))
            for i in range(size):
                cls = " "
                for j in range(size):
                    if cells[(i, j)].state:
                        cls += " *"
                    else:
                        cls += " ."
                print(cls)
            print("")
            yield hold, self, 1


size = 20
cells = {}
initialize()
for i in range(size):
    for j in range(size):
        a = cells[(i, j)] = Autom((i, j))
        activate(a, a.celllife())

# R-pentomino
cells[(9, 3)].state = True
cells[(10, 3)].state = True
cells[(9, 4)].state = True
cells[(8, 4)].state = True
cells[(9, 5)].state = True

cells[(5, 5)].state = True
cells[(5, 6)].state = True
cells[(4, 5)].state = True
cells[(4, 6)].state = True
cells[(4, 7)].state = True
cells[(10, 10)].state = True
cells[(10, 11)].state = True
cells[(10, 12)].state = True
cells[(10, 13)].state = True
cells[(11, 10)].state = True
cells[(11, 11)].state = True
cells[(11, 12)].state = True
cells[(11, 13)].state = True

print('CellularAutomata')
s = Show()
whenToStartShowing = 10
activate(s, s.picture(), delay=whenToStartShowing)
nrGenerations = 30
simulate(until=nrGenerations)
