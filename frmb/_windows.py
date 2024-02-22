import logging
import subprocess
from pathlib import Path
from typing import Iterable
from typing import Literal

import frmb

LOGGER = logging.getLogger(__name__)


def escape_windows_path(path: Path) -> str:
    return str(path).replace("\\", "\\\\")


def escape_windows_command(command: Iterable[str]) -> str:
    return subprocess.list2cmdline(command)


def _generate_reg_from_entry(
    entry: frmb.FrmbMenuItem,
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
            output += _generate_reg_from_entry(
                child,
                parent_path=full_path,
                add_keys=add_keys,
            )
    else:
        output += [
            f"[{path_prefix}{full_path}\\command]",
            f'@="{escape_windows_command(entry.command)}"',
        ]

    return output


def generate_reg_from_hierarchy(
    hierachy: list[frmb.FrmbMenuItem],
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


FileAssociationType = Literal["*", "directory", "directory_background", "drive"] | str
"""
types that are considered "file associations" and can be used with function using them.
"""


def get_key_path_for_file_association(
    target_file_type: FileAssociationType,
    user_only: bool = True,
) -> str:
    """
    Return a root registry key path to register a new context menu for the given file type.

    Args:
        target_file_type:
            the targeted filesystem object type OR any file extension (prefixed with a dot)
        user_only: False to "install" for ALL users, True only for the current user.

    Returns:
        A registry key path ending by ``\\shell``.
            Example: ``HKEY_CURRENT_USER\\Software\\Classes\\*\\shell``
    """

    root = "HKEY_CURRENT_USER" if user_only else "HKEY_LOCAL_MACHINE"

    if target_file_type == "*":
        return f"{root}\\Software\\Classes\\*\\shell"
    if target_file_type.lower() == "directory":
        return f"{root}\\Software\\Classes\\Directory\\shell"
    if target_file_type.lower() == "directory_background":
        return f"{root}\\Software\\Classes\\Directory\\Background\\shell"
    if target_file_type.lower() == "drive":
        return f"{root}\\Software\\Classes\\Drive\\shell"
    if target_file_type.startswith(".", 0, 1):
        return f"{root}\\Software\\Classes\\SystemFileAssociations\\{target_file_type}\\shell"

    raise ValueError(f"Unsupported file type {target_file_type}")


def get_file_association_for_key_path(
    key_path: str,
) -> tuple[FileAssociationType, bool]:
    """
    Return a file association corresponding to the given registry path.

    To use with [`get_key_path_for_file_association`][frmb.get_key_path_for_file_association].

    Args:
        key_path: a Windows registry key path

    Returns:
         the file association as string, True if the key is applie at user level else False
    """
    user_only = key_path.startswith("HKEY_CURRENT_USER")
    intermediate_path = key_path.split("\\", 1)[-1]

    if not intermediate_path.startswith("Software\\Classes"):
        raise ValueError(f"Unsupported key root {key_path}")

    intermediate_path = intermediate_path.split("\\", 2)[-1]

    if intermediate_path.startswith("*\\"):
        return "*", user_only
    if intermediate_path.startswith("Directory\\Background"):
        return "directory_background", user_only
    if intermediate_path.startswith("Directory\\"):
        return "directory", user_only
    if intermediate_path.startswith("Drive\\"):
        return "drive", user_only
    if intermediate_path.startswith("SystemFileAssociations\\."):
        return intermediate_path.split("\\")[1], user_only

    raise ValueError(f"Unknown key path {key_path}")
