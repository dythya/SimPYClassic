from SimPy.Simulation import *


class Wait_Or_Queue(Process):
    def waitup(self, myEvent):      # PEM illustrating "waitevent"
                                    # wait for "myEvent" to occur
        yield waitevent, self, myEvent
        print('At %s, some SimEvent(s) occurred that activated object %s.' %
              (now(), self.name))
        print('   The activating event(s) were %s' %
              ([x.name for x in self.eventsFired]))

    def queueup(self, myEvent):     # PEM illustrating "queueevent"
                                    # queue up for "myEvent" to occur
        yield queueevent, self, myEvent
        print('At %s, some SimEvent(s) occurred that activated object %s.' %
              (now(), self.name))
        print('   The activating event(s) were %s' %
              ([x.name for x in self.eventsFired]))


class Signaller(Process):
    # here we just schedule some events to fire
    def sendSignals(self):
        yield hold, self, 2
        event1.signal()        # fire "event1" at time 2
        yield hold, self, 8
        event2.signal()        # fire "event2" at time 10
        yield hold, self, 5
        event1.signal()        # fire all four events at time 15
        event2.signal()
        event3.signal()
        event4.signal()
        yield hold, self, 5
        event4.signal()        # event4 recurs at time 20


initialize()

# Now create each SimEvent and give it a name
event1 = SimEvent('Event-1')
event2 = SimEvent('Event-2')
event3 = SimEvent('Event-3')
event4 = SimEvent('Event-4')
Event_list = [event3, event4]   # define an event list

s = Signaller()
# Activate Signaller "s" *after* events created
activate(s, s.sendSignals())

w0 = Wait_Or_Queue('W-0')
# create object named "W-0", and set it to
# "waitup" for SimEvent "event1" to occur
activate(w0, w0.waitup(event1))
w1 = Wait_Or_Queue('W-1')
activate(w1, w1.waitup(event2))
w2 = Wait_Or_Queue('W-2')
activate(w2, w2.waitup(Event_list))
q1 = Wait_Or_Queue('Q-1')
# create object named "Q-1", and put it to be first
# in the queue for Event_list to occur
activate(q1, q1.queueup(Event_list))
q2 = Wait_Or_Queue('Q-2')
# create object named "Q-2", and append it to
# the queue for Event_list to occur
activate(q2, q2.queueup(Event_list))

simulate(until=50)
