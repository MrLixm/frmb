import pytest

from frmb import read_menu_hierarchy
from frmb._windows import generate_reg_from_hierarchy
from frmb._windows import get_key_path_for_file_association


def test__generate_reg_from_hierarchy(data_dir):

    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"
    hierarchy = read_menu_hierarchy(structure1_studio_dir)

    reg_content = generate_reg_from_hierarchy(hierarchy)
    assert "\n".join(reg_content) != "", print("\n".join(reg_content))


def test__generate_reg_from_hierarchy__comments(data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"
    hierarchy = read_menu_hierarchy(structure1_studio_dir)

    header_comments = [";;some comment", "; wow much fun"]
    reg_content = generate_reg_from_hierarchy(
        hierarchy, header_comments=header_comments
    )
    result = [line for line in reg_content if line in header_comments]
    assert result == header_comments

    header_comments = ["some comment", "wow much fun"]
    reg_content = generate_reg_from_hierarchy(
        hierarchy, header_comments=header_comments
    )
    result = [line for line in reg_content if line.lstrip("; ") in header_comments]
    assert len(result) == len(header_comments)


def test__get_key_path_for_file_association():
    expected = "HKEY_CURRENT_USER\\Software\\Classes\\*\\shell"
    result = get_key_path_for_file_association("*")
    assert result == expected

    expected = "HKEY_LOCAL_MACHINE\\Software\\Classes\\*\\shell"
    result = get_key_path_for_file_association("*", False)
    assert result == expected

    expected = "HKEY_LOCAL_MACHINE\\Software\\Classes\\Directory\\shell"
    result = get_key_path_for_file_association("directory", False)
    assert result == expected

    expected = (
        "HKEY_LOCAL_MACHINE\\Software\\Classes\\SystemFileAssociations\\.abc\\shell"
    )
    result = get_key_path_for_file_association(".abc", False)
    assert result == expected

    with pytest.raises(ValueError):
        get_key_path_for_file_association("abc", False)

    expected = "HKEY_CURRENT_USER\\Software\\Classes\\Drive\\shell"
    result = get_key_path_for_file_association("drive", True)
    assert result == expected

    expected = "HKEY_LOCAL_MACHINE\\Software\\Classes\\Directory\\Background\\shell"
    result = get_key_path_for_file_association("directory_background", False)
    assert result == expected
