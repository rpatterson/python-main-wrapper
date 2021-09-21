"""
Set up global environment and run another script within, ala pdb, profile, etc..

Both script arguments may either be a path to a Python script, a Python module or
package to be run in the same manner as Python's `-m` option, or a setuptools
`path.to.import:callable` entry-point.
"""

import sys
import runpy
import types
import logging
import argparse

import pkg_resources

# BBB: Python 2 compatibility
try:
    import pathlib
except ImportError:  # pragma: no cover
    import pathlib2 as pathlib

import six

# Manage version through the VCS CI/CD process
try:
    from . import version
except ImportError:  # pragma: no cover
    version = None
if version is not None:  # pragma: no cover
    __version__ = version.version

logger = logging.getLogger(__name__)


def main_type(arg):
    """
    Lookup a Python callable, either a script, module/package, or entry-point.
    """
    module_spec = None

    # If the argument is a readable file-system path, assume it's a script.
    path = pathlib.Path(arg)
    try:
        source = path.read_text()
    except (OSError, IOError):
        logging.debug(
            "Could not open %r as a file path, "
            "assuming the argument is a module/package or an entry-point.",
            arg,
            exc_info=True,
        )
        source = None
    code = None
    if source is not None:
        code = compile(source, str(path), "exec")
        return module_spec, code

    entry_point = None
    if ":" in arg:
        entry_point_src = arg
        if "=" not in entry_point_src:
            entry_point_src = "_={}".format(entry_point_src)
        entry_point = pkg_resources.EntryPoint.parse(entry_point_src)
        return None, entry_point.resolve()

    try:
        _, module_spec, code = runpy._get_module_details(arg)
    except ImportError:
        logging.debug(
            "Could not import %r as module/package, "
            "assuming the argument is a script or an entry-point.",
            arg,
            exc_info=True,
        )
        code = None
    if code is not None:
        return module_spec, code

    raise argparse.ArgumentTypeError(
        (
            "Could not resolve {!r} "
            "as either a script, module/package or entry point."
        ).format(arg)
    )


# Define command line options and arguments

script_parser = argparse.ArgumentParser(
    description=__doc__.strip(),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
script_arg_kwargs = dict(
    type=main_type,
    help="The Python script to run within the wrapper's environment",
)
script_parser.add_argument("script", **script_arg_kwargs)
cli_parser = argparse.ArgumentParser(
    description=__doc__.strip(),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
cli_parser.add_argument(
    "wrapper",
    type=main_type,
    help="A Python script that sets up the environment",
)
cli_parser.add_argument("script", **script_arg_kwargs)


def exec_main(module_spec, code, *args):
    """
    Patch Python's global execution environment and execute the code, cleaning up after.
    """

    import __main__

    orig_main = vars(__main__).copy()
    __builtins__ = __main__.__dict__["__builtins__"]
    orig_argv = list(sys.argv)

    if isinstance(code, types.FunctionType):
        code_path = pathlib.Path(code.__code__.co_filename)
    else:
        code_path = pathlib.Path(code.co_filename)
    globals_ = vars(__main__)
    try:
        globals_.clear()
        globals_.update(
            dict(
                __name__="__main__",
                __file__=str(code_path),
                __cached__=None,
                __builtins__=__builtins__,
            )
        )
        if module_spec is not None:
            globals_.update(
                dict(
                    __package__=module_spec.parent,
                    __loader__=module_spec.loader,
                    __spec__=module_spec,
                )
            )

        sys.argv[0] = code_path.name
        sys.argv[1:] = args

        if isinstance(code, types.FunctionType):  # pragma: no cover
            return code()
        else:
            return six.exec_(code, globals_, globals_)  # pragma: no cover

    finally:
        sys.argv[:] = orig_argv

        globals_.clear()
        globals_.update(orig_main)


class wrap_main(object):  # pragma: no cover
    """
    Run the wrapped function and then call the script/module/entry-point.
    """

    def __init__(self, parser):
        """
        Capture an argparse.ArgumentParser for parsing the function's arguments.
        """
        self.parser = parser

    def __call__(self, wrapped_func):
        """
        Wrap the function and call it with the appropriate parsed arguments.
        """

        def wrapper(args=None):
            """
            Parse the function's arguments and invoke it, then invoke the script.
            """
            args, remaining = self.parser.parse_known_args(args)
            wrapped_func(**vars(args))

            script_args, script_remaining = script_parser.parse_known_args(remaining)
            module_spec, code = script_args.script
            return exec_main(module_spec, code, *remaining)

        return wrapper


def main(args=None):
    args, remaining = cli_parser.parse_known_args(args)

    wrapper_module_spec, wrapper_code = args.wrapper
    try:
        exec_main(wrapper_module_spec, wrapper_code)
    except SystemExit:
        # Tolerate the wrapper script using the common `sys.exit(main())` pattern.
        # Note that wrapper scripts should *not* do this.
        pass

    module_spec, code = args.script  # pragma: no cover
    return exec_main(module_spec, code, *remaining)  # pragma: no cover


main.__doc__ = __doc__
