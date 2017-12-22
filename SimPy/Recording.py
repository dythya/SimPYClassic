# coding=utf-8
"""
This file contains the classes for recording simulation results, Histogram,
Monitor and Tally.

"""
from __future__ import division
# Required for backward compatibility
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import SimPy.Globals as Globals


class Histogram(list):
    """ A histogram gathering and sampling class"""

    def __init__(self, name = '', low = 0.0, high = 100.0, nbins = 10):
        list.__init__(self)
        self.name  = name
        self.low   = float(low)
        self.high  = float(high)
        self.nbins = nbins
        self.binsize = old_div((self.high - self.low), nbins)
        self._nrObs = 0
        self._sum = 0
        self[:] = [[low + (i - 1) * self.binsize, 0] for i in range(self.nbins + 2)]

    def addIn(self, y):
        """ add a value into the correct bin"""
        self._nrObs += 1
        self._sum += y
        b = int(old_div((y - self.low + self.binsize), self.binsize))
        if b < 0: b = 0
        if b > self.nbins + 1: b = self.nbins + 1
        assert 0 <= b <=self.nbins + 1, 'Histogram.addIn: b out of range: %s'%b
        self[b][1] += 1

    def __str__(self):
        histo = self
        ylab = 'value'
        nrObs = self._nrObs
        width = len(str(nrObs))
        res = []
        res.append(' < Histogram %s:'%self.name)
        res.append('\nNumber of observations: %s'%nrObs)
        if nrObs:
            su = self._sum
            cum = histo[0][1]
            fmt = '%s'
            line = '\n%s <= %s < %s: %s (cum: %s/%s%s)'\
                 %(fmt, '%s', fmt, '%s', '%s', '%5.1f', '%s')
            line1 = '\n%s%s < %s: %s (cum: %s/%s%s)'\
                 %('%s', '%s', fmt, '%s', '%s', '%5.1f', '%s')
            l1width = len(('%s <= '%fmt)%histo[1][0])
            res.append(line1\
                       %(' ' * l1width, ylab, histo[1][0], str(histo[0][1]).rjust(width),\
                         str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                      )
            for i in range(1, len(histo) - 1):
                cum += histo[i][1]
                res.append(line\
                       %(histo[i][0], ylab, histo[i + 1][0], str(histo[i][1]).rjust(width),\
                         str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                          )
            cum += histo[-1][1]
            linen = '\n%s <= %s %s : %s (cum: %s/%s%s)'\
                  %(fmt, '%s', '%s', '%s', '%s', '%5.1f', '%s')
            lnwidth = len(('<%s'%fmt)%histo[1][0])
            res.append(linen\
                       %(histo[-1][0], ylab, ' ' * lnwidth, str(histo[-1][1]).rjust(width),\
                       str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                       )
        res.append('\n > ')
        return ' '.join(res)


class Monitor(list):
    """ Monitored variables

    A Class for monitored variables, that is, variables that allow one
    to gather simple statistics.  A Monitor is a subclass of list and
    list operations can be performed on it. An object is established
    using m = Monitor(name = '..'). It can be given a
    unique name for use in debugging and in tracing and ylab and tlab
    strings for labelling graphs.
    """
    def __init__(self, name = 'a_Monitor', ylab = 'y', tlab = 't', sim = None):
        list.__init__(self)
        if not sim: sim = Globals.sim # Use global simulation if sim is None
        self.sim = sim
        self.startTime = 0.0
        self.name = name
        self.ylab = ylab
        self.tlab = tlab
        self.sim.allMonitors.append(self)

    def setHistogram(self, name = '', low = 0.0, high = 100.0, nbins = 10):
        """Sets histogram parameters.
        Must be called before call to getHistogram"""
        if name == '':
            histname = self.name
        else:
            histname = name
        self.histo = Histogram(name = histname, low = low, high = high, nbins = nbins)

    def observe(self, y,t = None):
        """record y and t"""
        if t is  None: t = self.sim.now()
        self.append([t, y])

    def tally(self, y):
        """ deprecated: tally for backward compatibility"""
        self.observe(y, 0)

    def accum(self, y,t = None):
        """ deprecated:  accum for backward compatibility"""
        self.observe(y, t)

    def reset(self, t = None):
        """reset the sums and counts for the monitored variable """
        self[:] = []
        if t is None: t = self.sim.now()
        self.startTime = t

    def tseries(self):
        """ the series of measured times"""
        return list(zip(*self))[0]

    def yseries(self):
        """ the series of measured values"""
        return list(zip(*self))[1]

    def count(self):
        """ deprecated: the number of observations made """
        return self.__len__()

    def total(self):
        """ the sum of the y"""
        if self.__len__() == 0:  return 0
        else:
            sum = 0.0
            for i in range(self.__len__()):
                sum += self[i][1]
            return sum # replace by sum() later

    def mean(self):
        """ the simple average of the monitored variable"""
        try:
            return 1.0 * self.total() / self.__len__()
        except ZeroDivisionError:
            raise ZeroDivisionError('SimPy: No observations for mean')

    def var(self):
        """ the sample variance of the monitored variable """
        n = len(self)
        tot = self.total()
        ssq = 0.0
        for i in range(self.__len__()):
            ssq += self[i][1] ** 2 # replace by sum() eventually
        try:
            return old_div((ssq - old_div(float(tot * tot), n)), n)
        except:
            raise ZeroDivisionError(
                    'SimPy: No observations for sample variance')

    def timeAverage(self, t = None):
        """
        The time-weighted average of the monitored variable.

        If t is used it is assumed to be the current time,
        otherwise t =  self.sim.now()

        """
        N = self.__len__()
        if N  == 0:
            return None

        if t is None: t = self.sim.now()
        sum = 0.0
        tlast = self[0][0]
        ylast = self[0][1]
        for i in range(N):
            ti, yi = self[i]
            sum += ylast * (ti - tlast)
            tlast = ti
            ylast = yi
        sum += ylast * (t - tlast)
        T = t - self[0][0]
        if T == 0:
             return None
        return old_div(sum, float(T))

    def timeVariance(self, t = None):
        """ the time - weighted Variance of the monitored variable.

            If t is used it is assumed to be the current time,
            otherwise t =  self.sim.now()
        """
        N = self.__len__()
        if N  == 0:
            return None
        if t is None: t = self.sim.now()
        sm = 0.0
        ssq = 0.0
        tlast = self[0][0]
        # print 'DEBUG: 1 twVar ', t, tlast
        ylast = self[0][1]
        for i in range(N):
            ti, yi = self[i]
            sm  += ylast * (ti - tlast)
            ssq += ylast * ylast * (ti - tlast)
            tlast = ti
            ylast = yi
        sm  += ylast * (t - tlast)
        ssq += ylast * ylast * (t - tlast)
        T = t - self[0][0]
        if T == 0:
             return None
        mn = old_div(sm, float(T))
        return old_div(ssq, float(T)) - mn * mn


    def histogram(self, low = 0.0, high = 100.0, nbins = 10):
        """ A histogram of the monitored y data values.
        """
        h = Histogram(name = self.name, low = low, high = high, nbins = nbins)
        ys = self.yseries()
        for y in ys: h.addIn(y)
        return h

    def getHistogram(self):
        """Returns a histogram based on the parameters provided in
        preceding call to setHistogram.
        """
        ys = self.yseries()
        h = self.histo
        for y in ys: h.addIn(y)
        return h

    def printHistogram(self, fmt = '%s'):
        """Returns formatted frequency distribution table string from Monitor.
        Precondition: setHistogram must have been called.
        fmt == format of bin range values
        """
        try:
            histo = self.getHistogram()
        except:
            raise FatalSimerror('histogramTable: call setHistogram first'\
                                ' for Monitor %s'%self.name)
        ylab = self.ylab
        nrObs = self.count()
        width = len(str(nrObs))
        res = []
        res.append('\nHistogram for %s:'%histo.name)
        res.append('\nNumber of observations: %s'%nrObs)
        su = sum(self.yseries())
        cum = histo[0][1]
        line = '\n%s <= %s < %s: %s (cum: %s/%s%s)'\
             %(fmt, '%s', fmt, '%s', '%s', '%5.1f', '%s')
        line1 = '\n%s%s < %s: %s (cum: %s/%s%s)'\
             %('%s', '%s', fmt, '%s', '%s', '%5.1f', '%s')
        l1width = len(('%s <= '%fmt)%histo[1][0])
        res.append(line1\
                   %(' ' * l1width, ylab, histo[1][0], str(histo[0][1]).rjust(width),\
                     str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                  )
        for i in range(1, len(histo) - 1):
            cum += histo[i][1]
            res.append(line\
                   %(histo[i][0], ylab, histo[i + 1][0], str(histo[i][1]).rjust(width),\
                     str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                      )
        cum += histo[-1][1]
        linen = '\n%s <= %s %s : %s (cum: %s/%s%s)'\
              %(fmt, '%s', '%s', '%s', '%s', '%5.1f', '%s')
        lnwidth = len(('<%s'%fmt)%histo[1][0])
        res.append(linen\
                   %(histo[-1][0], ylab, ' ' * lnwidth, str(histo[-1][1]).rjust(width),\
                   str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                   )
        return ' '.join(res)

class Tally(object):
    def __init__(self, name = 'a_Tally', ylab = 'y', tlab = 't', sim = None):
        if not sim: sim = Globals.sim # use global simulation if sim is None
        self.sim = sim
        self.name = name
        self.ylab = ylab
        self.tlab = tlab
        self.reset()
        self.startTime = 0.0
        self.histo = None
        self.sum = 0.0
        self._sum_of_squares = 0
        self._integral = 0.0    # time - weighted sum
        self._integral2 = 0.0   # time - weighted sum of squares
        self.sim.allTallies.append(self)

    def setHistogram(self, name = '', low = 0.0, high = 100.0, nbins = 10):
        """Sets histogram parameters.
        Must be called to prior to observations initiate data collection
        for histogram.
        """
        if name == '':
            hname = self.name
        else:
            hname = name
        self.histo = Histogram(name = hname, low = low, high = high, nbins = nbins)

    def observe(self, y, t = None):
        if t is None:
            t = self.sim.now()
        self._integral += (t - self._last_timestamp) * self._last_observation
        yy =  self._last_observation * self._last_observation
        self._integral2 += (t - self._last_timestamp) * yy
        self._last_timestamp = t
        self._last_observation = y
        self._total += y
        self._count += 1
        self._sum += y
        self._sum_of_squares += y * y
        if self.histo:
            self.histo.addIn(y)

    def reset(self, t = None):
        if t is None:
            t = self.sim.now()
        self.startTime = t
        self._last_timestamp = t
        self._last_observation = 0.0
        self._count = 0
        self._total = 0.0
        self._integral = 0.0
        self._integral2 = 0.0
        self._sum = 0.0
        self._sum_of_squares = 0.0

    def count(self):
        return self._count

    def total(self):
        return self._total

    def mean(self):
        return 1.0 * self._total / self._count

    def timeAverage(self, t = None):
        if t is None:
            t = self.sim.now()
        integ = self._integral + (t - self._last_timestamp) * self._last_observation
        if (t > self.startTime):
            return 1.0 * integ / (t - self.startTime)
        else:
            return None

    def var(self):
        return 1.0 * (self._sum_of_squares - (1.0 * (self._sum * self._sum)\
               / self._count)) / (self._count)

    def timeVariance(self, t = None):
        """ the time - weighted Variance of the Tallied variable.

            If t is used it is assumed to be the current time,
            otherwise t =  self.sim.now()
        """
        if t is None:
            t = self.sim.now()
        twAve = self.timeAverage(t)
        #print 'Tally timeVariance DEBUG: twave:', twAve
        last =  self._last_observation
        twinteg2 = self._integral2 + (t - self._last_timestamp) * last * last
        #print 'Tally timeVariance DEBUG:tinteg2:', twinteg2
        if (t > self.startTime):
            return 1.0 * twinteg2 / (t - self.startTime) - twAve * twAve
        else:
            return None



    def __len__(self):
        return self._count

    def __eq__(self, l):
        return len(l) == self._count

    def getHistogram(self):
        return self.histo

    def printHistogram(self, fmt = '%s'):
        """Returns formatted frequency distribution table string from Tally.
        Precondition: setHistogram must have been called.
        fmt == format of bin range values
        """
        try:
            histo = self.getHistogram()
        except:
            raise FatalSimerror('histogramTable: call setHistogram first'\
                                ' for Tally %s'%self.name)
        ylab = self.ylab
        nrObs = self.count()
        width = len(str(nrObs))
        res = []
        res.append('\nHistogram for %s:'%histo.name)
        res.append('\nNumber of observations: %s'%nrObs)
        su = self.total()
        cum = histo[0][1]
        line = '\n%s <= %s < %s: %s (cum: %s/%s%s)'\
             %(fmt, '%s', fmt, '%s', '%s', '%5.1f', '%s')
        line1 = '\n%s%s < %s: %s (cum: %s/%s%s)'\
             %('%s', '%s', fmt, '%s', '%s', '%5.1f', '%s')
        l1width = len(('%s <= '%fmt)%histo[1][0])
        res.append(line1\
                   %(' ' * l1width, ylab, histo[1][0], str(histo[0][1]).rjust(width),\
                     str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                  )
        for i in range(1, len(histo) - 1):
            cum += histo[i][1]
            res.append(line\
                   %(histo[i][0], ylab, histo[i + 1][0], str(histo[i][1]).rjust(width),\
                     str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                      )
        cum += histo[-1][1]
        linen = '\n%s <= %s %s : %s (cum: %s/%s%s)'\
              %(fmt, '%s', '%s', '%s', '%s', '%5.1f', '%s')
        lnwidth = len(('<%s'%fmt)%histo[1][0])
        res.append(linen\
                   %(histo[-1][0], ylab, ' ' * lnwidth, str(histo[-1][1]).rjust(width),\
                   str(cum).rjust(width),(old_div(float(cum), nrObs)) * 100, '%')
                   )
        return ' '.join(res)
