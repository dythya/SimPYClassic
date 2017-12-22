# coding=utf-8

from __future__ import print_function
from SimPy.Simulation import *
from random import *


class Thing(Process):
   """ Thing process for testing Monitors in simulation"""
   def __init__(self, M = None, name = 'Thing',sim=None):
        Process.__init__(self,name=name,sim=sim)
        self.y = 0.0
        self.M = M

   def execute(self):
        DEBUG = 0
        self.y = 0.0
        if DEBUG:
            print(self.name, self.sim.now(),self.y)
        self.M.observe(self.y)

        yield hold, self, 10.0
        self.y = 10
        if DEBUG:
            print(self.name, self.sim.now(),self.y)
        self.M.observe(self.y)

        yield hold, self, 10.0
        self.y = 5
        if DEBUG:
            print(self.name, self.sim.now(),self.y)
        self.M.observe(self.y)


# Monitor tests
# -------------

def test_observe():
    """Tests Monitor.observe"""
    m = Monitor(name = 'First')
    for i in range(10):
        m.observe(2 * i, i)

    assert m == [[i, 2 * i] for i in range(10)],'series wrong'
    assert m.name == 'First', 'name wrong'
    assert m.tseries() == tuple(range(10)),'tseries wrong:%s' % (m.tseries(),)
    assert m.yseries() == tuple(2 * i for i in range(10)),'yseries wrong:%s' % (m.yseries(),)
    assert m.total() == 90, 'total wrong:%s'%m.total()
    assert m.mean() == 9.0, 'mean wrong:%s'%m.mean()
    assert m.var() == (4 * 285.-(90 * 90 / 10.0)) / 10.0, 'sample var wrong: %s' % (m.var(),)


def test_observe_no_time():
    """Observe with time being picked up from now()"""
    s = Simulation()
    s.initialize()
    m = Monitor(name = 'No time',sim=s)
    t = Thing(m,sim=s)
    s.activate(t, t.execute(),0.0)
    s.simulate(until = 20.0)
    assert m.yseries() == (0, 10, 5),'yseries wrong:%s' % (m.yseries(),)
    assert m.tseries() == (0, 10, 20),'tseries wrong:%s' % (m.tseries(),)
    assert m.total() == 15, 'total wrong:%s'%m.total()
    assert m.timeAverage(10.0) == 5.0, 'time average is wrong: %s'%m.timeAverage(10.0)


def test_observe_tally():
    """Tally.observe without time values"""
    m = Tally(name = 'tallier')
    for i in range(10):
       m.observe(2 * i)
    assert m == [[0, 2 * i] for i in range(10)],'series wrong'
    assert m.total() == 90, 'total wrong:%s'%m.total()
    assert m.mean() == 9.0, 'mean wrong:%s'%m.mean()
    assert m.var() == (4 * 285.-(90 * 90 / 10.0)) / 10.0, 'sample var wrong: %s' % (m.var(),)


def test_time_average():
    """Tests time averages"""
    # old version
    m = Monitor(name = 'First')
    for i in range(10):
        m.observe(2 * i, i)

    assert m == [[i, 2 * i] for i in range(10)],'series wrong'
    assert m.timeAverage(10.0) == 9.0, 'time average is wrong: %s'%m.timeAverage(10)

    m2 = Monitor(name = 'second')
    T = [0, 1,4, 5]
    Y = [1, 2,1, 0]
    for t, y in zip(T, Y):
       m2.observe(y, t)
    assert m2.timeAverage(5.0) == 8.0 / 5, 'm2 time average is wrong: %s'%m2.timeAverage(5)
    # now the new recursive version
    #m = self.M
    #assert m.newtimeAverage(10.0) == 9.0, 'm1: new time average wrong: %s'%m.newtimeAverage(10)
    #m2 = self.M2
    #assert m2.newtimeAverage(5.0) == 8.0 / 5, 'm2: new time average wrong: %s'%m2.newtimeAverage(5.0)


def test_time_variance():
    """test time - weighted variance"""
    m = Monitor(name = 'First')
    for i in range(10):
        m.observe(2 * i, i)
    assert m == [[i, 2 * i] for i in range(10)],'series wrong'
    assert abs(m.timeVariance(10.0) - 33) < 0.0001, 'time - weighted variance is wrong: %s'%m.timeVariance(10.0)

    m2 = Monitor(name = 'second')
    T = [0, 1,4, 5]
    Y = [1, 2,1, 0]
    for t, y in zip(T, Y):
       m2.observe(y, t)
    assert abs(m2.timeVariance(5) - 6.0 / 25) < 0.0001, 'time - weighted variance is wrong: %s'%m2.timeVariance(5)


def test_reset():
    """test time averages"""
    m = Monitor(name = 'First')
    for i in range(10):
        m.observe(2 * i, i)
    m.reset(t = 10.0)
    assert m.startTime == 10.0, 'reset time  wrong'
    assert m == [],'reset series wrong: %s' % (m,)


def test_tally():
    """Tests the tally function of monitor"""
    m = Monitor(name = 'First')
    S = []
    for i in range(10):
        m.tally(i)
        S.append([0, i])
    assert m == S, 'Stored series is wrong: %s' % (m,)
    assert m.name == 'First', 'Tally name wrong'
    assert m.total() == 45, 'Tally total wrong'
    assert m.mean() == 4.5, 'Tally mean wrong'
    assert m.var()  == (285 - (45 * 45 / 10.0)) / 10.0, 'Tally sample var wrong %s' % (m.var(),)


def test_accumulate():
    """Tests the accumulation function of monitor"""
    m2 = Monitor(name = 'Second')
    assert m2.startTime == 0, 'accum startTime wrong'
    for i in range(5):
        m2.accum(10, i)  # this is (y, t)
    assert m2.total() == 50, 'accum total wrong:%s' % (m2.total(),)
    assert m2.startTime == 0, 'accum startTime wrong'
    assert m2.timeAverage(5.0) == 10.0, 'accum timeAverage wrong:%s' % (m2.timeAverage(10.0),)
    ## test reset
    m2.reset(10)
    assert m2 == [],'accum reset list wrong:%s' % (m2,)
    assert m2.total() == 0.0, 'accum reset total wrong'
    assert m2.startTime == 10, 'accum startTime wrong'


def test_accumulate_in_time():
    """Tests accumulation over simulation time"""
    s=Simulation()
    s.initialize()
    m3 = Monitor(name = 'third',sim=s)
    T3 = Thing(name = 'Job', M = m3,sim=s)
    assert m3.startTime == 0, 'Accumulate startTime wrong'
    s.activate(T3, T3.execute(),0.0)
    s.simulate(until = 30.0)
    assert m3.startTime == 0, 'Accumulate startTime wrong'


def test_list_stuff():
    """Test some Monitor list operations"""
    m = Monitor(name = 'First')
    for i in range(10):
        m.observe(2 * i, i)
    shouldBe = [[i, 2 * i] for i in range(10)]
    assert shouldBe == m, 'M list is wrong'
    assert [2, 4] == m[2], 'indexing wrong:%s' % (m[2],)
    m[0] = [10, 10]
    assert [10, 10] == m[0], 'item replacement wrong:%s' % (m[0],)
    m.reverse()
    assert [10, 10] == m[-1], 'list reverse wrong:%s' % (m[-1],)
    m.sort()
    assert [1, 2] == m[0], 'list sort wrong:%s' % (m[0],)
    assert 10 == len(m), 'list length wrong'
    assert [2, 4] in m, 'item in list wrong'


def test_histogram():
    """Test Monitor histogram"""
    m = Monitor(name = 'First')
    for y in [-5, 0, 5, 15, 99, 105, 120]:m.observe(y)
    h = m.histogram(low = 0.0, high = 100.0, nbins = 10)
    shouldBe = list(zip(*h))[1]
    assert shouldBe == (1, 2,1, 0,0, 0,0, 0,0, 0,1, 2), 'm histogram is wrong: %s' % (shouldBe,)
