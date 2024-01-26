from frmb import read_hierarchy_from_root
from frmb._windows import generate_reg_from_hierarchy


def test__generate_reg_from_hierarchy(data_dir):

    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"
    hierarchy = read_hierarchy_from_root(structure1_studio_dir)

    reg_content = generate_reg_from_hierarchy(hierarchy)
    assert "\n".join(reg_content) != "", print("\n".join(reg_content))


def test__generate_reg_from_hierarchy__comments(data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"
    hierarchy = read_hierarchy_from_root(structure1_studio_dir)

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
