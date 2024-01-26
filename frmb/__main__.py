import logging
import sys

import frmb

LOGGER = logging.getLogger(__name__)


def main(argv=None):
    cli = frmb.CLI(argv=argv)

    logging.basicConfig(
        level=logging.DEBUG if cli.debug else logging.INFO,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )

    LOGGER.info(f"starting {frmb.__name__} v{frmb.__version__}")

    if not cli.root_dir.exists():
        raise FileNotFoundError(
            f"root_dir provided doesn't exist on disk: {cli.root_dir}"
        )

    LOGGER.info(f"reading {cli.root_dir}")
    hierarchy = frmb.read_hierarchy_from_root(cli.root_dir)

    # // validate data read from disk

    errors, warnings = frmb.validate_entry_hierarchy(hierarchy)

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

    comments = [f"generated from {cli.root_dir}"]
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

    target_dir = cli.target_dir or cli.root_dir

    target_reg_add = target_dir / "install.reg"
    LOGGER.info(f"writing {target_reg_add}")
    target_reg_add.write_text("\n".join(reg_content_add), encoding="utf-8")

    target_reg_remove = target_dir / "uninstall.reg"
    LOGGER.info(f"writing {target_reg_remove}")
    target_reg_remove.write_text("\n".join(reg_content_remove), encoding="utf-8")


if __name__ == "__main__":
    main()
