# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m my_awesome_project` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `my_awesome_project.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `my_awesome_project.__main__` in `sys.modules`.
"""Module that contains the command line application."""

from __future__ import annotations

import argparse


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="my-awesome-project")


def main(args: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `my-awesome-project` or `python -m my_awesome_project`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    print(opts)  # noqa: T201
    return 0
