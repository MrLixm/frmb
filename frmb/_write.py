import json
import logging
from pathlib import Path

from ._menu import FrmbMenuItem

LOGGER = logging.getLogger(__name__)


def write_menu_item_to_file(
    menu_item: FrmbMenuItem,
    directory: Path,
    write_children: bool = True,
) -> Path:
    """
    Serialize a FrmbMenuItem instance to disk.

    If the file already exists its content is overwritten.

    Args:
        menu_item:
        directory: filesystem path to an existing directory
        write_children: True to also write all its childre to disk

    Returns:
        filesystem path to the .frmb file written on disk. other childen files might have been written.
    """
    content = {
        "name": menu_item.name,
        "command": menu_item.command,
        "paths": menu_item.paths,
        "enabled": menu_item.enabled,
    }
    if menu_item.icon:
        content["icon"] = str(menu_item.icon)

    dst_path = directory / (menu_item.identifier + ".frmb")
    json.dump(content, dst_path.open("w"), indent=4)

    if not write_children:
        return dst_path

    for child in menu_item.children:
        child_dir = directory / menu_item.identifier
        child_dir.mkdir(exist_ok=True)
        write_menu_item_to_file(menu_item=child, directory=child_dir)

    return dst_path
