######################################
Advent of Code 2021 â Python Solutions
######################################

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Solutions for `Advent of Code <https://adventofcode.com>`_ 2021 in pure Python 3.9. ð
No dependencies, no speed hacks:
pythonic code with just the standard library. ð
Well, unless I'm too annoyed by the challenge of the day. ðĪŠ

Starting at day 5, the code includes comments on coding patterns and algorithms. ð
This should keep the code understandable even for people new to Python or
not familiar with the specific algorithm. ðĪ

Usage ððĪķ
--------

The module is directly executable from the CLI.

.. code:: bash

    # run day 3
    python3 -m aoc2021 3
    # run day 4 with example code
    python3 -m aoc2021 4 -e
    # run days 1,2,3,4,5
    python3 -m aoc2021 1 2 3 4 5
    # show available options
    python3 -m aoc2021 -h

Use the ``--data`` switch to point to a custom data location.

Running with ``aocd``
^^^^^^^^^^^^^^^^^^^^^

The module can be installed to allow running it with
`aocd <https://github.com/wimglenn/advent-of-code-data>`_.
This lets you compare its solutions against your own and others.

.. code:: bash

    # install the current directory (this repo) and aocd
    pip install . advent-of-code-data
    # export your session cookie
    export AOC_SESSION=612b7c47656....
    # run year 2021 solutions
    aoc -y 2021
