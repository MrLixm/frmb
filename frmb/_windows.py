import logging
import subprocess
from pathlib import Path
from typing import Iterable

import frmb

LOGGER = logging.getLogger(__name__)


def escape_windows_path(path: Path) -> str:
    return str(path).replace("\\", "\\\\")


def escape_windows_command(command: Iterable[str]) -> str:
    return subprocess.list2cmdline(command)


def _generate_reg_from_entry(
    entry: frmb.FrmbFormat,
    parent_path: str,
    add_keys: bool = True,
) -> list[str]:
    """
    Actual logic to convert a :class:`FrmbFormat` instance to reg syntax.

    Recursive function that process the Frmb instance children.
    """
    output = []
    path_prefix = "" if add_keys else "-"
    full_path = f"{parent_path}\\shell\\{entry.identifier}"

    if entry.children:
        output += [f"; {entry.name}"]

    output += [
        f"[{path_prefix}{full_path}]",
        f'"MUIVerb"="{entry.name}"',
    ]
    if entry.icon:
        output += [f'"icon"="{escape_windows_path(entry.icon)}"']

    if entry.children:
        output += ['"subCommands"=""']
        for child in entry.children:
            output += [""]
            output += _generate_reg_from_entry(child, parent_path=full_path)
    else:
        output += [
            f"[{path_prefix}{full_path}\\command]",
            f'@="{escape_windows_command(entry.command)}"',
        ]

    return output


def generate_reg_from_hierarchy(
    hierachy: list[frmb.FrmbFormat],
    header_comments: list[str] | None = None,
    add_keys: bool = True,
) -> list[str]:
    """
    Generate a valid reg file from the given hierarchy of Frmb instances.

    Args:
        hierachy:
            content of the reg file as list of root keys.
        header_comments:
            list of line that should be added in the header comment section
        add_keys:
            True to create a reg file to install, False to create the inverse that uninstall.

    Returns:
        a reg file as a list of line
    """
    output = [
        "Windows Registry Editor Version 5.00",
        "",
        f"; File auto-generated from {frmb.__name__} v{frmb.__version__}.",
    ]
    header_comments = header_comments or []
    output += [
        comment if comment.startswith(";") else "; " + comment
        for comment in header_comments
    ]
    output += [""]

    for root_entry in hierachy:
        for registry_path in root_entry.paths:
            output += [""]
            output += _generate_reg_from_entry(
                root_entry,
                parent_path=registry_path,
                add_keys=add_keys,
            )

    return output
