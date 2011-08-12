#! /usr/bin/env python
from distutils.core import setup
import sys
reload(sys).setdefaultencoding('Utf-8')


setup(
    name='SimPy',
    version='2.1.0',
    author='Klaus Muller, Tony Vignaux, Ontje Lünsdorf, Stefan Scherfke',
    author_email=('vignaux at user.sourceforge.net; '
        'kgmuller at users.sourceforge.net; '
        'the_com at gmx.de; '
        'stefan at sofa-rockers.org'),
    description='Event discrete, process based simulation for Python.',
    long_description=open('README.txt').read(),
    url='http://simpy.sourceforge.net/',
    download_url='https://sourceforge.net/projects/simpy/files/',
    license='GNU LGPL',
    packages=[
        'SimPy',
    ],
    package_data=[],
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
)
