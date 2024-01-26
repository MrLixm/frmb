import pytest

from frmb.__main__ import main


def test__main__errors(tmp_path, data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"

    arguments = [
        str(structure1_studio_dir),
        "--target-dir",
        str(tmp_path),
    ]
    with pytest.raises(RuntimeError):
        main(argv=arguments)

    arguments = [
        str("I:/doesnt/exists"),
        "--target-dir",
        str(tmp_path),
    ]
    with pytest.raises(FileNotFoundError):
        main(argv=arguments)


def test__main(tmp_path, data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"

    arguments = [
        str(structure1_studio_dir),
        "--target-dir",
        str(tmp_path),
        "--ignore-errors",
    ]
    main(argv=arguments)

    assert tmp_path.joinpath("install.reg").exists()
    assert tmp_path.joinpath("uninstall.reg").exists()
