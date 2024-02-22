import difflib
import logging
import sys
from pathlib import Path
from typing import Sequence

import frmb

LOGGER = logging.getLogger(__name__)


def increment_path(path: Path) -> Path:
    """
    Increment a path based on version already existing on disk.

    The given path must be the base path without any increment.

    Can handle increment when not all the first versions exists on disk.
    """
    increment = 1

    existing_versions = sorted(list(path.parent.glob(f"{path.stem}.????{path.suffix}")))
    if existing_versions:
        last_version = "".join(
            [
                char.lstrip("+ ")
                for char in difflib.ndiff(str(path), str(existing_versions[-1]))
                if char.startswith("+")
            ]
        )
        last_version = last_version.strip(".")
        increment = int(last_version) + 1

    new_path = path.with_suffix(f".{increment:0>4}{path.suffix}")
    return new_path


def execute_cli(argv: Sequence[str] | None = None):
    """
    Run the CLI using user-provided arguments.

    Args:
        argv: user command line arguments
    """
    cli = frmb.CLI(argv=argv)

    logging.basicConfig(
        level=logging.DEBUG if cli.debug else logging.INFO,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )

    root_dir = cli.root_dir.resolve()
    target_dir = cli.target_dir or root_dir
    target_dir = target_dir.resolve()

    LOGGER.info(f"starting {frmb.__name__} v{frmb.__version__}")

    if not root_dir.exists():
        raise FileNotFoundError(f"root_dir provided doesn't exist on disk: {root_dir}")

    if not target_dir.exists():
        raise FileNotFoundError(
            f"target_dir provided doesn't exist on disk: {target_dir}"
        )

    LOGGER.info(f"reading {root_dir}")
    hierarchy: list[frmb.FrmbMenuItem] = frmb.read_menu_hierarchy(root_dir)

    # // validate data read from disk

    errors, warnings = frmb.validate_menu_hierarchy(hierarchy)

    sep = "\n  "
    warning_message = "\n".join(
        [
            f"- {entity}:{sep}{sep.join(messages)}"
            for entity, messages in warnings.items()
        ]
    )
    if warning_message:
        LOGGER.warning(warning_message)

    error_message = "\n".join(
        [f"- {entity}:{sep}{sep.join(messages)}" for entity, messages in errors.items()]
    )
    if error_message:
        LOGGER.error(error_message)
        if not cli.ignore_errors:
            raise RuntimeError(f"Parsed hierarchy has issues:\n{error_message}")

    # // generate reg file

    comments = [f"generated from {root_dir}"]
    reg_content_add = frmb.generate_reg_from_hierarchy(
        hierarchy,
        header_comments=comments,
        add_keys=True,
    )
    reg_content_remove = frmb.generate_reg_from_hierarchy(
        hierarchy,
        header_comments=comments,
        add_keys=False,
    )

    # // write files to disk

    target_reg_add = increment_path(target_dir / "install.reg")
    LOGGER.info(f"writing {target_reg_add}")
    target_reg_add.write_text("\n".join(reg_content_add), encoding="utf-8")

    target_reg_remove = increment_path(target_dir / "uninstall.reg")
    LOGGER.info(f"writing {target_reg_remove}")
    target_reg_remove.write_text("\n".join(reg_content_remove), encoding="utf-8")


if __name__ == "__main__":
    execute_cli()
