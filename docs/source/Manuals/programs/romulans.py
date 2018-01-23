from SimPy.Simulation import (Process, initialize, activate, simulate,
                              hold, now, waituntil, stopSimulation)
import random


class Player(Process):

    def __init__(self, lives=1, name='ImaTarget'):
        Process.__init__(self, name)
        self.lives = lives
        # provide Player objects with a "damage" property
        self.damage = 0

    def life(self):
        self.message = 'Drat! Some %s survived Federation attack!' % \
            (target.name)

        def killed():     # function testing for "damage > 5"
            return self.damage > 5

        while True:
            yield waituntil, self, killed
            self.lives -= 1
            self.damage = 0
            if self.lives == 0:
                self.message = '%s wiped out by Federation at \
                time %s!' % (target.name, now())
                stopSimulation()


class Federation(Process):

    def fight(self):                # simulate Federation operations
        print('Three %s attempting to escape!' % (target.name))
        while True:
            if random.randint(0, 10) < 2:  # check for hit on player
                target.damage += 1         # hit! increment damage to player
                if target.damage <= 5:     # target survives
                    print('Ha! %s hit! Damage= %i' %
                          (target.name, target.damage))
                else:
                    if (target.lives - 1) == 0:
                        print('No more %s left!' % (target.name))
                    else:
                        print('Now only %i %s left!' % (target.lives - 1,
                                                        target.name))

            yield hold, self, 1


initialize()
gameOver = 100
# create a Player object named "Romulans"
target = Player(lives=3, name='Romulans')
activate(target, target.life())
# create a Federation object
shooter = Federation()
activate(shooter, shooter.fight())
simulate(until=gameOver)
print(target.message)
