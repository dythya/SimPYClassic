from __future__ import print_function
import sys
from SimPy.SimulationStep import *
try:  # Python 3
    from tkinter import *
except:
    from Tkinter import *

import SimPy.SimulationStep, GUIDebug


import warnings
warnings.warn('This module be removed in SimPy 3.', DeprecationWarning)


# global variables
_breakpoints = []
_until = 0
_callback = None
_lastCommandIssued = ""
_simStarted = False
_registeredClasses = []
_runMode = None

# run modes
STEP = 1
NO_STEP = 2

# register new object for windowing
def register(obj,hook=lambda :"",name=None):

    global _registeredClasses

    # if process subclass is given register it
    if type(obj) == TypeType and issubclass(obj, Process):
        _registeredClasses += [(obj,name,hook)]

    # if instance of process is given register it
    elif issubclass(type(obj), Process):
        _guiCtrl.addNewProcess(obj,name,hook)

    # if instance of Resource is given register it
    elif issubclass(type(obj), Resource):
        _guiCtrl.addNewResource(obj,name,hook)

    # else create a generic window with hook
    else:
        _guiCtrl.addNewWindow(obj,name,hook)

# override activate to catch registered class instances
def activate(obj,process,at="undefined",delay="undefined",prior=False):

    global _registeredClasses

    SimPy.SimulationStep.activate(obj,process,at,delay,prior)

    # if obj is instance of the class register it
    for c,n,h in _registeredClasses:
        if isinstance(obj, c):
            _guiCtrl.addNewProcess(obj,n,h)

# add to breakpoints
def newBreakpoint(newBpt):

    global _breakpoints
    _breakpoints.append(newBpt)
    _breakpoints.sort()

# set the current run mode of simulation
def setRunMode(runMode):

    global _runMode
    _runMode = runMode

# initialize the simulation and the GUI
def initialize():

    SimPy.SimulationStep.initialize()

    # create gui controller
    global _guiCtrl
    _guiCtrl = GUIDebug.GUIController()

    # initialize run mode if not already set
    global _runMode
    if not _runMode:
        _runMode = STEP

# simulation function
def simulate(callback=lambda :None, until=0):

    global _runMode

    # print usage
    if( _runMode == STEP ):
        print("Breakpoint Usage:")
        print("  [c]   Continue simulation")
        print("  [s]   Step to next event")
        print("  [b #] Add new breakpoint")
        print()
        print("  [q]   Quit debugger")
        print()

    # set global variables
    global _until
    _until = until

    global _callback
    _callback = callback

    # initialize to step command
    global _lastCommandIssued
    _lastCommandIssued = "s"

    # only prompt user if we are in STEP mode
    if( _runMode == STEP): promptUser()

    # quit if user entered 'q'
    if( _lastCommandIssued == 'q'):
        return

    # begin simulation
    global _simStarted
    _simStarted = True
    startStepping()
    SimPy.SimulationStep.simulate(callback=callbackFunction,until=_until)

# check for breakpoints
def callbackFunction():

    global _breakpoints,_runMode,_guiCtrl

    # NO_STEP mode means we update windows and take no breaks
    # this is used for compatibility with REAL debuggers
    if( _runMode == NO_STEP ):
        _guiCtrl.updateAllWindows()
        return

    if( 0 == len(_breakpoints) ):
        return

    # this is a breakpoint
    if( now() >= _breakpoints[0] ):

        # update gui
        _guiCtrl.updateAllWindows()

        # remove past times from breakpoints list
        while( 0 != len(_breakpoints) and now() >= _breakpoints[0] ):
            _breakpoints.pop(0)

        # call user's callback function
        global _callback
        _callback()

        promptUser()

# prompt user for next command
def promptUser():

    global _simStarted

    # set prompt text
    prompt = '(SimDB) > '

    # pause for breakpoint
    while( 1 ):
        if sys.version_info.major == 2:
            input = raw_input
        user_input = input( prompt )

        # take a look at the last command issued
        global _lastCommandIssued

        if 0 == len(user_input):
            user_input = _lastCommandIssued

        _lastCommandIssued = user_input

        # continue
        if( "c" == user_input ):
            break

        # step
        elif( "s" == user_input ):
            global _breakpoints
            _breakpoints.insert(0,0)
            break

        # add breakpoint
        elif( 0 == user_input.find("b")):
            try:
                for i in eval( user_input[1:] + "," ):
                    newBreakpoint( int(i) )
            except SyntaxError:
                print("missing breakpoint values")

        # quit
        elif( "q" == user_input ):
            SimPy.SimulationStep.stopSimulation()
            return

        else:
            print("  unknown command")


