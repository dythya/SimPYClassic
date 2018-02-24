# coding=utf-8
"""
SimPy, a process - based simulation package in Python

Contains the following modules:
Lib - module with all base classes of SimPy
Globals - module providing a global Simulation object
Simulation - module implementing processes and resources
Monitor - dummy module for backward compatibility
SimulationTrace - module implementing event tracing
SimulationRT - module for simulation speed control
SimulationStep - module for stepping through simulation event by event
SimPlot - Tk - based plotting module
SimGui - Tk - based SimPy GUI module
Lister - module for prettyprinting class instances
Lib - module containing SimPy entity classes (Process etc.)
Recording - module containing SimPy classes for recording results (Monitor,
        Tally)
Globals - module providing global Simulation object and the global
        simulation methods
stepping - a simple interactive debugger

"""
__version__ = '2.3.4'


def test():
    import os.path
    try:
        import pytest
    except ImportError:
        print('You need pytest and mock to run the tests. '
              'Try "pip install pytest mock".')
    else:
        pytest.main([os.path.dirname(__file__)])
