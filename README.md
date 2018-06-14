Pipeline Simulation
===================

This repo lets you play with different pipeline designs and lets you come up with scenarios 
for how the pipeline could be used. Work in progress.

Installation
------------

The project uses python3 needs a few, dataclasses, numpy and pytest python packages.
If you don't have them already in you python environment or like to work in isolation
you can set up a virtualenv for it with the following commands:

    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt


Usage
-----

Run the self tests with (py.test)[http://pytest.org]

Run the various simulations to create sample pipeline data

    python3 src/simulation1.py

Todo
----
- manual testers test at specific times similar to how deploys are done
- bugs in production and recovery
- timer pipeline triggers
- commit frequency increasing towards deadline then dropping
- realistic pipeline simulation examples
- metrics cheat

