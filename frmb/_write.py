import json
import logging
import shutil
from pathlib import Path

from . import FrmbFile
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


def delete_menu_file(
    menu_file: FrmbFile,
    remove_children: bool = True,
    remove_children_dir: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """
    Delete the given menu from disk.

    Args:
        menu_file: the menu to delete from disk.
        remove_children:
            True to recursively delete all children too.
        remove_children_dir:
            Only used when ``remove_children=True``.
            If True the whole file tree hosting children will be deleted, including
            non-frmb related files.
        dry_run:
            If True, no file will be deleted but those which should have been are
            still in the function return.

    Returns:
        list of filesystem path deleted from disk with no duplicates
    """
    deleted: set[Path] = set()
    if not dry_run:
        LOGGER.debug(f"[delete_menu_file] deleting {menu_file}")
        menu_file.path.unlink()
    deleted.add(menu_file.path)

    if not remove_children:
        return list(deleted)

    for child in menu_file.children:
        deleted.update(
            delete_menu_file(
                child,
                remove_children=remove_children,
                remove_children_dir=remove_children_dir,
                dry_run=dry_run,
            )
        )

    if remove_children_dir and menu_file.children_dir.is_dir():
        deleted.update(list(menu_file.children_dir.rglob("*")))
        deleted.add(menu_file.children_dir)
        if not dry_run:
            LOGGER.debug(f"[delete_menu_file] deleting {menu_file.children_dir}")
            shutil.rmtree(menu_file.children_dir)

    return list(deleted)


