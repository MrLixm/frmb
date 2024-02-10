import dataclasses
import json
import logging
import os
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
    """
    Describe the content of the Frmb file format.

    This object has no concept of a filesystem. Use [FrmbFile][frmb.FrmbFile] if you
    wish to preserve that information.

    An instance is considered immutable. This allows hashing it, which could be used
    to compare if 2 hierarchies of FrmbFormat are equal.
    """

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

    enabled: bool = True
    """
    Set to False to specify the menu and its children is not intended to be displayed.
    
    Note that its children might still have the ``enabled`` attribute set to True.
    It is up to the consumer process to determine that children have their parent disabled.
    """

    def __str__(self):
        return (
            f'<{self.__class__.__name__} "{self.name}": {len(self.children)} children>'
        )

    @classmethod
    def from_file(
        cls,
        path: Path,
        root_dir: Path,
        children: list["FrmbFormat"] = None,
    ) -> "FrmbFormat":
        """
        Get an instance from a serialized file on disk.

        Args:
            path: filesystem path to an existing file, expected to be in the json format.
            root_dir: filesystem path to an existing directory, that is the root of the hierarchy.
            children:
        """

        def _resolve(s: str):
            return resolve_tokens(
                s,
                cwd=str(path.parent).replace("\\", "\\\\"),
                root=str(root_dir).replace("\\", "\\\\"),
            )

        content = json.load(path.open("r"))

        icon_path = content.get("icon", None)
        icon_path = Path(_resolve(icon_path)) if icon_path else None

        return cls(
            name=content["name"],
            identifier=path.stem,
            icon=icon_path,
            command=tuple(_resolve(arg) for arg in content.get("command", [])),
            paths=tuple(content.get("paths", [])),
            children=tuple(children or []),
            enabled=content.get("enabled", True),
        )


@dataclasses.dataclass(frozen=True)
class FrmbFile:
    """
    A dataclass for a Frmb file existing on disk.

    An instance is considered immutable. This allows hashing it, which could be used
    to compare if 2 hierarchies of FrmbFormat are equal.
    """

    path: Path
    """
    Filesystem path to an existing .frmb file.
    """

    root_dir: Path
    """
    The hierarchy root directory this file was extracted from.
    """

    children: tuple["FrmbFile"]
    """
    Other frmb file that are children of this one in the global hierarchy.
    """

    @property
    def content(self) -> FrmbFormat:
        """
        The content of the file in the Frmb format.
        """
        return FrmbFormat.from_file(
            path=self.path,
            root_dir=self.root_dir,
            children=[file.content for file in self.children],
        )


def read_menu_hierarchy_as_file(
    root_dir: Path,
    __initial_root: Path | None = None,
) -> list[FrmbFile]:
    """
    Parse the given directory to build a hierarchy of Frmb objects that represent
    the context-menu.

    Only the root object are returned, which can be parsed recursively using their
    ``children`` attribute.

    Args:
        root_dir: directory representing the start of the context-menu hierarchy.
        __initial_root: private. Used to track the root dir in recursive calls.

    Returns:
        list of Frmb files found at root.
    """
    frmb_paths = root_dir.glob("*.frmb")
    output: list[FrmbFile] = []
    __initial_root = __initial_root or root_dir

    for frmb_path in frmb_paths:
        children = None

        frmb_dir = frmb_path.with_suffix("")
        if frmb_dir.is_dir():
            children = read_menu_hierarchy_as_file(
                frmb_dir, __initial_root=__initial_root
            )

        frmb_obj = FrmbFile(
            path=frmb_path,
            root_dir=__initial_root,
            children=tuple(children) if children else tuple(),
        )
        output.append(frmb_obj)

    return output


def read_menu_hierarchy(root_dir: Path) -> list[FrmbFormat]:
    """
    Parse the given directory to build a hierarchy of Frmb objects that represent
    the context-menu.

    Only the root object are returned, which can be parsed recursively using their
    ``children`` attribute.

    The object returned have no concept of the original filesystem structure and
    simply represent the context-menu structure. Use
    [`read_menu_hierarchy_as_file`][frmb.read_menu_hierarchy_as_file]
    if you need to preserve the filesystem structure information.

    Args:
        root_dir: directory representing the start of the context-menu hierarchy.

    Returns:
        list of Frmb file content found at root.
    """
    hierarchy = read_menu_hierarchy_as_file(root_dir)
    return [file.content for file in hierarchy]


def validate_menu_hierarchy(
    hierarchy: Iterable[FrmbFormat],
    __child_number: int = 0,
) -> tuple[dict[FrmbFormat, list[str]], dict[FrmbFormat, list[str]]]:
    """
    Return issues the given menu hierarchy might have.

    Recursive function.

    Example of use:

    ```python
    import frmb
    hierarchy = frmb.read_menu_hierarchy(".")
    errors, warnings = frmb.validate_menu_hierarchy(hierarchy)
    ```

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

        if entry.icon and os.sep in str(entry.icon) and not entry.icon.is_file():
            warnings.setdefault(entry, []).append(
                f"icon path doesn't exist on disk: got {entry.icon}, expected to be an existing file."
            )

        child_errors, child_warnings = validate_menu_hierarchy(
            entry.children,
            __child_number=__child_number if __child_number else 1,
        )
        errors.update(child_errors)
        warnings.update(child_warnings)

    return errors, warnings
