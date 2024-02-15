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
