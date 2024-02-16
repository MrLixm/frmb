import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import Iterable

from ._menu import FrmbMenuItem
from ._tokens import FrmbTokenResolver

LOGGER = logging.getLogger(__name__)


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

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"path=.../{self.path.parent.name}/{self.path.name}, "
            f"{len(self.children)}children>"
        )

    def at_root(self) -> bool:
        """
        Return True if this file is located at the root of the hierarchy.
        """
        return self.path.parent == self.root_dir

    def content(self, resolve_tokens: bool = True) -> FrmbMenuItem:
        """
        The content of the file in the Frmb format.
        """
        instance = read_menu_item_from_file(
            path=self.path,
            children=[
                file.content(resolve_tokens=resolve_tokens) for file in self.children
            ],
        )

        if resolve_tokens:
            resolver = FrmbTokenResolver(
                CWD=str(self.path.parent).replace("\\", "\\\\"),
                ROOT=str(self.root_dir).replace("\\", "\\\\"),
            )

            new_icon = resolver.resolve(str(instance.icon)) if instance.icon else None
            new_icon = Path(new_icon) if new_icon else None

            new_command = tuple(resolver.resolve(arg) for arg in instance.command)

            instance = dataclasses.replace(
                instance,
                icon=new_icon,
                command=new_command,
            )

        return instance


def read_menu_item_from_file(
    path: Path,
    children: list[FrmbMenuItem] = None,
) -> FrmbMenuItem:
    """
    Get an FrmbMenuItem instance from a serialized file on disk.

    Args:
        path: filesystem path to an existing file, expected to be in the json format.
        children: child instance the new instance must be parent of
    """

    content = json.load(path.open("r"))

    icon_path = content.get("icon", None)
    icon_path = Path(icon_path) if icon_path else None

    return FrmbMenuItem(
        name=content["name"],
        identifier=path.stem,
        icon=icon_path,
        command=tuple(content.get("command", [])),
        paths=tuple(content.get("paths", [])),
        children=tuple(children or []),
        enabled=content.get("enabled", True),
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


def read_menu_hierarchy(
    root_dir: Path,
    resolve_tokens: bool = True,
) -> list[FrmbMenuItem]:
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
        resolve_tokens: False to not resolve tokens in some strings attributes.

    Returns:
        list of Frmb file content found at root.
    """
    hierarchy = read_menu_hierarchy_as_file(root_dir)
    return [file.content(resolve_tokens=resolve_tokens) for file in hierarchy]


def validate_menu_hierarchy(
    hierarchy: Iterable[FrmbMenuItem],
    __child_number: int = 0,
) -> tuple[dict[FrmbMenuItem, list[str]], dict[FrmbMenuItem, list[str]]]:
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
