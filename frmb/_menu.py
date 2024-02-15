import dataclasses
import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class FrmbMenuItem:
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

    children: tuple["FrmbMenuItem"]
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
        children: list["FrmbMenuItem"] = None,
    ) -> "FrmbMenuItem":
        """
        Get an instance from a serialized file on disk.

        Args:
            path: filesystem path to an existing file, expected to be in the json format.
            children: child instance the new instanc emust be parent of
        """

        content = json.load(path.open("r"))

        icon_path = content.get("icon", None)
        icon_path = Path(icon_path) if icon_path else None

        return cls(
            name=content["name"],
            identifier=path.stem,
            icon=icon_path,
            command=tuple(content.get("command", [])),
            paths=tuple(content.get("paths", [])),
            children=tuple(children or []),
            enabled=content.get("enabled", True),
        )

    def to_file(self, directory: Path, write_children: bool = True):
        """
        Serialize this instance to disk.

        If the file already exists its content is overwritten.

        Args:
            directory: filesystem path to an existing directory
            write_children: True to also write all its childre to disk
        """
        content = {
            "name": self.name,
            "command": self.command,
            "paths": self.paths,
            "enabled": self.enabled,
        }
        if self.icon:
            content["icon"] = str(self.icon)

        dst_path = directory / (self.identifier + ".frmb")
        json.dump(content, dst_path.open("w"), indent=4)

        if not write_children:
            return

        for child in self.children:
            child_dir = directory / self.identifier
            child_dir.mkdir(exist_ok=True)
            child.to_file(directory=child_dir)
