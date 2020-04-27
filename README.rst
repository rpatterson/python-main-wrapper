==============================================================================
python-main-wrapper
==============================================================================
Set up global environment and run another script within, ala pdb, profile, etc
------------------------------------------------------------------------------

.. image:: https://github.com/rpatterson/python-main-wrapper/workflows/Run%20linter,%20tests%20and,%20and%20release/badge.svg

Use `main-wrapper` either as a command-line script or as a library to make `Python`_
scripts that set up or change some global Python environment and then run another script
within that environment.  It seeks to combine into one library all the gloss and polish
of other Python software that does this, such as using `python -m` with `pdb` and
`profile` in the standard library or the `coverage` package's command-line `run`
command.


Installation
============

Install using any tool for installing standard Python 3 distributions such as `pip`_::

  $ sudo pip3 install main-wrapper


Usage
=====

See the command-line help for details on options and arguments::

  $ usage: python-main-wrapper [-h]

  Set up global environment and run another script within, ala pdb, profile, etc..

  optional arguments:
    -h, --help  show this help message and exit


Motivation
==========

I found myself writing such wrapper scripts repeatedly over the years and kept
struggling to remember how I did it last time.  I made this package to capture all that
knowledge and to have one place to put improvements as I discover them.


.. _Python: https://docs.python.org/3/library/logging.html
.. _pip: https://pip.pypa.io/en/stable/installing/
