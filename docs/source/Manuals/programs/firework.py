from SimPy.Simulation import Process, activate, initialize, hold, now, simulate


class Firework(Process):

    def execute(self):
        print('%s firework launched' % now())
        yield hold, self, 10.0  # wait 10.0 time units
        for i in range(10):
            yield hold, self, 1.0
            print('%s tick' % now())
        yield hold, self, 10.0  # wait another 10.0 time units
        print('%s Boom!!' % now())


initialize()
f = Firework()  # create a Firework object, and
# activate it (with some default parameters)
activate(f, f.execute(), at=0.0)
simulate(until=100)
