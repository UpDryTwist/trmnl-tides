# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m trmnl_tides` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `trmnl_tides.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `trmnl_tides.__main__` in `sys.modules`.
"""Module that contains the command line application."""

from __future__ import annotations

import argparse
import sys

from .tides_data import NoaaTideData


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="trmnl-tides")


def main(args: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `trmnl_tides` or `python -m trmnl_tides`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    _opts = parser.parse_args(args=args)
    tides = NoaaTideData("9447130")
    tides.read_data()
    print(tides)  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
