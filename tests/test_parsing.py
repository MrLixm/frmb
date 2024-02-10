from pathlib import Path

from frmb._parsing import FrmbFormat
from frmb._parsing import read_hierarchy_from_root
from frmb._parsing import validate_entry_hierarchy
from frmb._parsing import resolve_tokens


def test__read_hierarchy_from_root__studio(data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"

    hierarchy = read_hierarchy_from_root(structure1_studio_dir)
    assert len(hierarchy) == 2

    # files should be parsed in alphabetical order
    assert hierarchy[0].name == "Ffmpeg"
    assert hierarchy[0].icon == structure1_studio_dir / "ffmpeg.ico"
    assert hierarchy[0].identifier == "FFMPEG"
    assert hierarchy[1].name == "OIIO Tool"
    assert hierarchy[1].icon == Path("oiiotool.ico")
    assert hierarchy[1].paths == ("HKEY_CURRENT_USER\\Software\\Classes\\*",)
    assert hierarchy[1].identifier == "OIIO Tool"

    children = hierarchy[0].children
    assert len(children) == 2

    assert children[0].name == "convert video to .gif - interactive"
    assert children[0].icon is None
    prepath = str(structure1_studio_dir / "FFMPEG").replace("\\", "\\\\")
    assert children[0].command == (
        "cmd",
        "/k",
        f'"{prepath}\\ffmpeg-togif.bat"',
        "%1",
        "1",
    )

    assert len(children[1].children) == 2
    assert children[1].command != []

    children = hierarchy[1].children
    assert len(children) == 1


def test__validate_entry_hierarchy__studio(data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_studio_dir = structure1_dir / "studio"

    hierarchy = read_hierarchy_from_root(structure1_studio_dir)
    errors, warnings = validate_entry_hierarchy(hierarchy)
    assert len(errors) == 0
    assert len(warnings) == 2


def test__validate_entry_hierarchy__show(data_dir):
    structure1_dir = data_dir / "structure1"
    structure1_show_dir = structure1_dir / "show"

    hierarchy = read_hierarchy_from_root(structure1_show_dir)
    errors, warnings = validate_entry_hierarchy(hierarchy)
    assert len(errors) == 1
    assert len(warnings) == 0


def test__validate_entry_hierarchy_recursion(data_dir):

    hierarchy = FrmbFormat("lowest", "", None, tuple(), tuple(), tuple())
    for i in range(16):
        p = tuple() if i < 15 else ("p",)
        hierarchy = FrmbFormat(f"{i}", f"{i}", None, tuple(), p, (hierarchy,))

    errors, warnings = validate_entry_hierarchy([hierarchy])
    assert len(errors) == 1
    assert "16 nested entry" in errors[list(errors.keys())[0]][0]
    assert len(warnings) == 0


def test__resolve_tokens():
    source = "some@DIR @FOO:ex \\@FILE\\"
    expected = f"some/d/dir 45:ex \\{str(Path(__file__))}\\"
    tokens = {"DIR": "/d/dir", "foo": "45", "FILE": str(Path(__file__))}
    result = resolve_tokens(source, **tokens)
    assert result == expected

    source = "some@@DIR @FOO:ex @f"
    expected = f"some@DIR 45:ex @f"
    tokens = {"DIR": "/d/dir", "foo": "45"}
    result = resolve_tokens(source, **tokens)
    assert result == expected

    source = "some@@@@DIR @FOO:ex wha\\@@@DIR"
    expected = f"some@@DIR 45:ex wha\\@/d/dir"
    tokens = {"DIR": "/d/dir", "foo": "45"}
    result = resolve_tokens(source, **tokens)
    assert result == expected


def test_FrmbFormat_hash():

    hierarchy_1 = FrmbFormat("lowest", "", None, tuple(), tuple(), tuple())
    for i in range(13):
        path = tuple() if i < 12 else ("p",)
        hierarchy_1 = FrmbFormat(f"{i}", f"{i}", None, tuple(), path, (hierarchy_1,))

    hierarchy_2 = FrmbFormat("lowest", "", None, tuple(), tuple(), tuple())
    for i in range(12):
        path = tuple() if i < 11 else ("p",)
        hierarchy_2 = FrmbFormat(f"{i}", f"{i}", None, tuple(), path, (hierarchy_2,))

    hierarchy_3 = FrmbFormat("lowest", "", None, tuple(), tuple(), tuple())
    for i in range(12):
        path = tuple() if i < 11 else ("p",)
        hierarchy_3 = FrmbFormat(f"{i}", f"{i}", None, tuple(), path, (hierarchy_3,))

    hierarchy_4 = FrmbFormat("lowest", "", None, tuple(), tuple(), tuple())
    for i in range(12):
        path = tuple() if i < 11 else ("p",)
        hierarchy_4 = FrmbFormat(
            f"{i if i < 11 else 'babz'}", f"{i}", None, tuple(), path, (hierarchy_4,)
        )

    assert hash(hierarchy_1) != hash(hierarchy_2)
    assert hash(hierarchy_2) == hash(hierarchy_3)
    assert hash(hierarchy_3) != hash(hierarchy_4)
