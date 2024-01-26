import argparse
import logging
import sys
from pathlib import Path

import frmb

LOGGER = logging.getLogger(__name__)


class CLI:
    def __init__(self, argv=None):
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
        return Path(self.parsed.root_dir)

    @property
    def debug(self) -> bool:
        return self.parsed.debug

    @property
    def target_dir(self) -> Path | None:
        return Path(self.parsed.target_dir) if self.parsed.target_dir else None

    @property
    def ignore_errors(self) -> bool:
        return self.parsed.ignore_errors
