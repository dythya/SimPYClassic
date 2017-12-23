from setuptools import setup

import SimPy


setup(
    name='SimPy',
    version=SimPy.__version__,
    author='Klaus Muller, Tony Vignaux, Ontje Lünsdorf, Stefan Scherfke',
    author_email=('vignaux at user.sourceforge.net; '
        'kgmuller at users.sourceforge.net; '
        'the_com at gmx.de; '
        'stefan at sofa-rockers.org'),
    description='Event discrete, process based simulation for Python.',
    long_description=open('README.txt').read(),
    url='https://github.com/SimPyClassic/SimPyClassic',
    download_url='https://github.com/SimPyClassic/SimPyClassic/releases',
    license='GNU LGPL',
    packages=[
        'SimPy',
        'SimPy.test',
    ],
    package_data={},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Library or Lesser General Public ' + \
                'License (LGPL)',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
)
