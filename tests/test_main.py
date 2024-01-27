import pytest

from frmb.__main__ import main
from frmb.__main__ import increment_path


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

    assert tmp_path.joinpath("install.0001.reg").exists()
    assert tmp_path.joinpath("uninstall.0001.reg").exists()


def test__increment_path__1(tmp_path):

    src_path = tmp_path / "great file.txt"
    increment1_path = tmp_path / "great file.0001.txt"
    increment1_path.write_text("beaufort")
    increment2_path = tmp_path / "great file.0002.txt"
    increment2_path.write_text("beaufort")

    expected = tmp_path / "great file.0003.txt"
    result = increment_path(src_path)
    assert result == expected


def test__increment_path__2(tmp_path):

    src_path = tmp_path / "file.txt"
    increment1_path = tmp_path / "file.0010.txt"
    increment1_path.write_text("beaufort")
    increment2_path = tmp_path / "file.0012.txt"
    increment2_path.write_text("beaufort")

    expected = tmp_path / "file.0013.txt"
    result = increment_path(src_path)
    assert result == expected
