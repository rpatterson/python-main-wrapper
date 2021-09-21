"""
Set up global environment and run another script within, and integration tests.
"""

import site
import unittest

# BBB: Python 2 compatibility
try:
    import contextlib2 as contextlib
except ImportError:  # pragma: no cover
    import contextlib

import six

import mainwrapper


class MainwrapperTests(unittest.TestCase):
    """
    python-main-wrapper unit and integration tests.
    """

    def getCliErrorMessages(self, args):
        """
        Run the CLI script and return any error messages.
        """
        stderr_file = six.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr_file):
                mainwrapper.main(args=args)
        return stderr_file.getvalue()

    def test_cli_help(self):
        """
        The command line script is self-docummenting.
        """
        stdout_file = six.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(stdout_file):
                mainwrapper.main(args=["--help"])
        stdout = stdout_file.getvalue()
        self.assertIn(
            mainwrapper.__doc__.strip().split("\n")[0][:55],
            stdout,
            "The console script docstring missing from --help output",
        )

        wrapped_out_file = six.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(wrapped_out_file):
                mainwrapper.main(args=["site", "site:_script", "--", "--help"])
        wrapped_out = wrapped_out_file.getvalue()
        self.assertNotIn(
            mainwrapper.__doc__.strip().split("\n")[0][:55],
            wrapped_out,
            "The console script docstring included in wrapped --help output",
        )

    def test_cli_options(self):
        """
        The command line script accepts options controlling behavior.
        """
        with self.assertRaises(SystemExit):
            mainwrapper.main(args=[site.__file__, "site"])
        with self.assertRaises(SystemExit):
            mainwrapper.main(args=["site", "site:_script"])
        with self.assertRaises(SystemExit):
            mainwrapper.main(args=["_=site:_script", "site"])

    def test_cli_option_errors(self):
        """
        The command line script displays useful messages for invalid option values.
        """
        stderr = self.getCliErrorMessages(
            args=["__non_existent_wrapper__", "__non_existent_script__"]
        )
        self.assertIn(
            "Could not resolve '__non_existent_wrapper__'",
            stderr,
            "Wrong invalid option message",
        )
