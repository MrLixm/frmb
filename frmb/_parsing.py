import dataclasses
import json
import logging
import re
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


def resolve_tokens(source: str, **kwargs) -> str:
    """
    Replace all tokens in the given string with their intended value.

    tokens starts with a ``@`` and are followed by the token name. Example: ``@FILE``.

    Args:
        source: a string that might contains tokens
        **kwargs:
            dict of token with their associated values.
            tokens name can be uppercase or lowercase.

    Returns:
        source string with token replaced
    """
    resolved = source.replace("@@", "%%TMP%%")

    for token_name, token_value in kwargs.items():
        resolved = re.sub(
            rf"@{token_name.upper()}",
            # avoid re to interpret replacement tokens
            token_value.replace("\\", "\\\\"),
            resolved,
        )

    resolved = resolved.replace("%%TMP%%", "@")
    return resolved


@dataclasses.dataclass(frozen=True)
class FrmbFormat:
    name: str
    """
    Label displayed in the GUI
    """

    identifier: str
    """
    Unique identifier used to store the key in the registry.
    """

    icon: Path | None
    """
    Absolute path to an .ico file.
    """

    command: tuple[str]
    """
    Command to call when clicking the entry. As list of arguments.
    """

    paths: tuple[str]
    """
    Only for root entries. Registry paths that must have this entry.
    """

    children: tuple["FrmbFormat"]
    """
    Nested entries.
    """

    def __str__(self):
        return (
            f'<{self.__class__.__name__} "{self.name}": {len(self.children)} children>'
        )

    @classmethod
    def from_file(cls, path: Path, children: list["FrmbFormat"] = None):
        """
        Get an instance from a serialized file on disk.

        Args:
            path: filesystem path to an existing file, expected to be in the json format.
            children:
        """

        def _resolve(s: str):
            return resolve_tokens(s, cwd=str(path.parent))

        content = json.load(path.open("r"))

        icon_path = content.get("icon", None)
        icon_path = Path(_resolve(icon_path)) if icon_path else None
        if icon_path and not icon_path.is_absolute():
            icon_path = path.parent / icon_path
            icon_path = icon_path.resolve()

        return cls(
            name=content["name"],
            identifier=path.stem,
            icon=icon_path,
            command=tuple(_resolve(arg) for arg in content.get("command", [])),
            paths=tuple(content.get("paths", [])),
            children=tuple(children or []),
        )


def read_hierarchy_from_root(root_dir: Path) -> list[FrmbFormat]:
    """

    Args:
        root_dir: directory reprensenting teh start of the context-menu entries hierarchy.

    Returns:
        list of Frmb file found at this root.
    """
    frmb_paths = root_dir.glob("*.frmb")
    output: list[FrmbFormat] = []

    for frmb_path in frmb_paths:
        children = None

        frmb_dir = frmb_path.with_suffix("")
        if frmb_dir.is_dir():
            children = read_hierarchy_from_root(frmb_dir)

        frmb_obj = FrmbFormat.from_file(frmb_path, children=children)
        output.append(frmb_obj)

    return output


def validate_entry_hierarchy(
    hierarchy: Iterable[FrmbFormat],
    __child_number=0,
) -> tuple[dict[FrmbFormat, list[str]], dict[FrmbFormat, list[str]]]:
    """
    Return issues the given hierarchy might have.

    Recursive function.

    Args:
        hierarchy: a list of FrmbFormat that correspond to the root entries of a context menu.
        __child_number: private, number of nested entry we currently have for a root entry.

    Returns:
        tuple of errors["frmb instance", "list of errors"], warnings["frmb instance", "list of warnings"]
    """
    errors = {}
    warnings = {}

    for entry in hierarchy:

        if __child_number:
            __child_number += 1

        if __child_number > 16:
            errors.setdefault(entry, []).append(
                f"maximum number of 16 nested entry reached with {entry}"
            )

        if not __child_number and not entry.paths:
            errors.setdefault(entry, []).append(
                f"no paths specified for root entry {entry}"
            )

        if entry.children and entry.command:
            warnings.setdefault(entry, []).append(
                f"Entry {entry} is specifying both a command and children."
            )

        if entry.icon and not entry.icon.is_file():
            errors.setdefault(entry, []).append(
                f"icon path doesn't exist on disk: got {entry.icon}, expected to be an existing file."
            )

        child_errors, child_warnings = validate_entry_hierarchy(
            entry.children,
            __child_number=__child_number if __child_number else 1,
        )
        errors.update(child_errors)
        warnings.update(child_warnings)

    return errors, warnings
