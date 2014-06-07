from __future__ import print_function
from setuptools import Command, setup

"""
Graffiti
--------

A library for declarative computation

Intro
`````

.. code:: python

    from graffiti import Graph
    description = {
        "a": lambda n: n + 1,
        "b": lambda a: a * 10
    }

    graph = Graph(description)
    graph({ "n": 10 })
    #=> { "n": 10, "a": 11, "b": 110 }

Installation
````````````

.. code:: bash

    $ pip install graffiti
    $ python mygraph.py

Links
`````

* `website <https://github.com/SegFaultAX/graffiti>`_

"""

class run_audit(Command):
    """Audits source code using PyFlakes for following issues:
        - Names which are used but not defined or used before they are defined.
        - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os, sys
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print("Audit requires PyFlakes installed in your system.")
            sys.exit(-1)

        warns = 0
        # Define top-level directories
        dirs = ('graffiti',)
        for dir in dirs:
            for root, _, files in os.walk(dir):
                for file in files:
                    if file.endswith('.py') :
                        warns += flakes.checkPath(os.path.join(root, file))
        if warns > 0:
            print("Audit finished with total %d warnings." % warns)
        else:
            print("No problems found in sourcecode.")

setup(
    name='graffiti',
    version='0.1.0',
    url='https://github.com/SegFaultAX/graffiti',
    license='MIT',
    author='Michael-Keith Bernard',
    author_email='mkbernard.dev@gmail.com',
    description='A library for declarative computation.',
    long_description=__doc__,
    packages=['graffiti'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries"
    ],
    cmdclass={'audit': run_audit}
)
