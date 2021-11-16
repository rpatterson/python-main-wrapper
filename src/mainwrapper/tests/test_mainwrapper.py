"""
Set up global environment and run another script within, and integration tests.
"""

import sys
import site
import contextlib
import io
import subprocess
import unittest

import mainwrapper


class MainwrapperTests(unittest.TestCase):
    """
    python-main-wrapper unit and integration tests.
    """

    def test_importable(self):
        """
        The Python package is on `sys.path` and thus importable.
        """
        import_process = subprocess.run(
            [sys.executable, "-c", "import mainwrapper"],
            check=True,
        )
        self.assertEqual(
            import_process.returncode,
            0,
            "The Python package not importable",
        )

    def getCliErrorMessages(self, args):
        """
        Run the CLI script and return any error messages.
        """
        stderr_file = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr_file):
                mainwrapper.main(args=args)
        return stderr_file.getvalue()

    def test_cli_help(self):
        """
        The command line script is self-docummenting.
        """
        stdout_file = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(stdout_file):
                mainwrapper.main(args=["--help"])
        stdout = stdout_file.getvalue()
        self.assertIn(
            mainwrapper.__doc__.strip().split("\n")[0][:55],
            stdout,
            "The console script docstring missing from --help output",
        )

        wrapped_out_file = io.StringIO()
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
