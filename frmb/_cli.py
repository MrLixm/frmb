import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

import frmb

LOGGER = logging.getLogger(__name__)


class CLI:
    """
    "Command line interface".

    Parse user arguments and retrieve their value as a more convenient python object.

    Args:
        argv: command line arguments. Default uses ``sys.argv``.
    """

    def __init__(self, argv: Sequence[str] | None = None):
        argv = argv or sys.argv[1:]
        self.parser = argparse.ArgumentParser(
            frmb.__name__,
            description="Convert file structures to right-click context menu for Windows.",
        )
        self.parser.add_argument(
            "root_dir",
            type=str,
            help="Path to an existing directory containing context-menu entries.",
        )
        self.parser.add_argument(
            "--target-dir",
            type=str,
            default="",
            help="Path to an existing directory where the reg file must be created. Default is root-dir.",
        )
        self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Output debug logging.",
        )
        # intention for this flag are mainly for unittesting
        self.parser.add_argument(
            "--ignore-errors",
            action="store_true",
            help="Doesn't raise when errors are found. Use at your own risk.",
        )
        self.parsed = self.parser.parse_args(argv)

    @property
    def root_dir(self) -> Path:
        """
        Filesystem path to an existing directory, root of the context-menu hierarchy.
        """
        return Path(self.parsed.root_dir)

    @property
    def debug(self) -> bool:
        """
        True to log debug messages.
        """
        return self.parsed.debug

    @property
    def target_dir(self) -> Path | None:
        """
        Filesystem path to an existing directory, used to create the reg files.
        """
        return Path(self.parsed.target_dir) if self.parsed.target_dir else None

    @property
    def ignore_errors(self) -> bool:
        """
        If True, does not stop (raise) when errors are found in the hierarchy.
        """
        return self.parsed.ignore_errors
