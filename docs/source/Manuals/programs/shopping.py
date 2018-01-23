from SimPy.Simulation import Process, activate, hold, initialize, simulate


class Customer(Process):
    def buy(self, budget=0):
        print('Here I am at the shops %s' % self.name)
        t = 5.0
        for i in range(4):
            yield hold, self, t
            # executed 4 times at intervals of t time units
            print('I just bought something %s' % self.name)
            budget -= 10.00
        print('All I have left is %s I am going home %s' % (budget, self.name))


initialize()

# create a customer named "Evelyn",
C = Customer(name='Evelyn')

# and activate her with a budget of 100
activate(C, C.buy(budget=100), at=10.0)

simulate(until=100.0)
