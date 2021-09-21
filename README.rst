==============================================================================
python-main-wrapper
==============================================================================
Set up global environment and run another script within, ala pdb, profile, etc
------------------------------------------------------------------------------

.. image:: https://github.com/rpatterson/python-main-wrapper/workflows/Run%20linter,%20tests%20and,%20and%20release/badge.svg

Use ``main-wrapper`` either as a command-line script or as a library to make `Python`_
scripts that set up or change some global Python environment and then run another script
within that environment.  It seeks to combine into one library all the gloss and polish
of other Python software that does this, such as using ``python -m`` with ``pdb`` and
``profile`` in the standard library or the ``coverage`` package's command-line ``run``
command.


Installation
============

Install using any tool for installing standard Python 3 distributions such as `pip`_::

  $ sudo pip3 install main-wrapper


Usage
=====

You may use this package either as a library in your code that needs to wrap another
script or as a command-line script.

To use as a library, use the provided decorator to wrap your function that sets up the
global environment you need the script to be run in::

  import logging
  import argparse

  import mainwrapper

  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--level",
      default="INFO",
      help="The level of messages to log at or above",
  )

  @mainwrapper.wrap_main(parser)
  def main(level=parser.get_default("level")):
      """
      As an example, this function will set up logging at level INFO.
      """
      logging.basicConfig(level=getattr(logging, level))

The changes to Python's global execution environment that support running the wrapper
function and the final script are also cleaned up upon completion, so it should be
possible to use this library to execute multiple scripts in the same process as if they
were run independently.

See the command-line help for details the options and arguments for using this package
as a command-line script::

  $ usage: python-main-wrapper [-h] wrapper script

  Set up global environment and run another script within, ala pdb, profile, etc..  Both
  script arguments may either be a path to a Python script, a Python module or package
  to be run in the same manner as Python's `-m` option, or a setuptools
  `path.to.import:callable` entry-point.

  positional arguments:
    wrapper     A Python script that sets up the environment
    script      The Python script to run within the wrapper's environment

  optional arguments:
    -h, --help  show this help message and exit

Note that this package uses `argparse.ArgumentParser.parse_known_args`_ under the hood
and as such be sure to use it's support for the ``--`` convention to separate arguments
and options to be passed to the wrapped script::

  $ python-main-wrapper site site:_script --help
  ...
  site.py [--user-base] [--user-site]

  Without arguments print some useful information
  With arguments print the value of USER_BASE and/or USER_SITE separated
  by ':'.

  Exit codes with --user-base or --user-site:
    0 - user site directory is enabled
    1 - user site directory is disabled by user
    2 - user site directory is disabled by super user
        or for security reasons
   >2 - unknown error


Motivation
==========

I found myself writing such wrapper scripts repeatedly over the years and kept
struggling to remember how I did it last time.  I made this package to capture all that
knowledge and to have one place to put improvements as I discover them.


.. _Python: https://docs.python.org/3/library/logging.html
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _argparse.ArgumentParser.parse_known_args: https://docs.python.org/dev/library/argparse.html#argparse.ArgumentParser.parse_known_args
