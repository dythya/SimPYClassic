============
Installation
============

This file describes the installation of SimPy |release|.

#. Check that you have Python 2.7 or above.

#. You can install SimPy easily via `PIP <https://pypi.python.org/pypi/pip>`_
   ::

    $ pip install SimPy

   If SimPy is already installed, use the *-U* option for pip to
   upgrade::

    $ pip install -U SimPy

   Remember, on Linux/MacOS/Unix you may need *root* privileges to install
   SimPy. This also applies to the installing SimPy manually, as described
   below.

#. To manually install a SimPy tarball, or to execute the examples, download
   and unpack the SimPy archive into a folder (using option "Use folder names"
   in WinZip, "Re-create folders" in Linux Archive Manager, or similar option
   in your unpacker). This will create a SimPy-|release| folder with all source
   code and documentation.

   Open a terminal, *cd* to the SimPy folder and execute *setup.py* or
   *pip install .*::

    $ cd where/you/put/simpy/SimPy-x.y
    $ python setup.py install
    $ # or
    $ pip install .

   If you do not have permissions to perform the installation as root, you can
   install SimPy into a non-standard folder::

    $ cd where/you/put/simpy/SimPy-x.y
    $ python setup.py install --home <dir>

#. Run one or more of the programs under *docs/examples* to see
   whether Python finds the SimPy module. If you get an error message
   like *ImportError: No module named SimPy*, move the SimPy folder
   into a directory which you know to be on the Python module search
   path (like /Lib/site-packages).

#. The tutorial and manuals are in the *docs/html* folder. Many users have
   commented that the Bank tutorials are valuable in getting users started on
   building their own simple models. Even a few lines of Python and SimPy can
   model significant real systems.

For more help, contact the `SimPy-Users mailing list
<mailto:simpy-users@lists.sourceforge.net>`_. SimPy users are pretty helpful.


Enjoy simulation programming in SimPy!
