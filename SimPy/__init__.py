#!/usr / bin / env python
# $Revision$ $Date$
"""
SimPy a process - based simulation package in Python

LICENSE:
Copyright (C) 2002, 2004, 2005, 2006, 2007, 2008, 2009 Klaus G. Muller, Tony Vignaux
mailto: kgmuller@xs4all.nl and Tony.Vignaux@vuw.ac.nz

    This library is free software; you can redistribute it and / or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111 - 1307  USA
END OF LICENSE

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
Recording - module containing SimPy classes for recording results (Monitor, Tally)
Globals - module providing global Simulation object and the global 
          simulation methods

__version__ = '$Revision$ $Date$ kgm'
"""

__SimPyVersion__ = '2.0.1'
