import shutil

from frmb._read import read_menu_hierarchy
from frmb._read import read_menu_hierarchy_as_file
from frmb._write import write_menu_item_to_file
from frmb._write import delete_menu_file


def test__write_menu_item_to_file(data_dir, tmp_path):
    # ensure to_file use the same logic as from_file
    src_dir = data_dir / "structure1" / "studio"
    hierarchy_src = read_menu_hierarchy(src_dir)

    dst_path = tmp_path / "test1"
    dst_path.mkdir()

    for menu in hierarchy_src:
        write_menu_item_to_file(menu_item=menu, directory=dst_path)

    hierarchy_dst = read_menu_hierarchy(dst_path)
    assert hierarchy_dst == hierarchy_src

    dst_path = tmp_path / "test2"
    dst_path.mkdir()

    for menu in hierarchy_src:
        write_menu_item_to_file(menu, dst_path, write_children=False)

    hierarchy_dst = read_menu_hierarchy(dst_path)
    assert hierarchy_dst != hierarchy_src
    assert not any([path.is_dir() for path in dst_path.glob("*")])


def test__delete_menu_file__dryun(data_dir, tmp_path):
    # ensure to_file use the same logic as from_file
    src_dir = data_dir / "structure1" / "studio"
    new_dir = tmp_path / "hierarchy"
    shutil.copytree(src_dir, new_dir)
    hierarchy_src = read_menu_hierarchy_as_file(new_dir)
    # video-to-gif-presets.frmb
    file = hierarchy_src[0].children[1]
    assert file.path.name == "video-to-gif-presets.frmb"
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))

    result = delete_menu_file(file, dry_run=True)
    assert len(result) == 3
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))

    result = delete_menu_file(file, remove_children_dir=True, dry_run=True)
    assert len(result) == 4
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))


def test__delete_menu_file__1(data_dir, tmp_path):
    # ensure to_file use the same logic as from_file
    src_dir = data_dir / "structure1" / "studio"
    new_dir = tmp_path / "hierarchy"
    shutil.copytree(src_dir, new_dir)
    hierarchy_src = read_menu_hierarchy_as_file(new_dir)
    # video-to-gif-presets.frmb
    file = hierarchy_src[0].children[1]
    assert file.path.name == "video-to-gif-presets.frmb"
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))

    result = delete_menu_file(file)
    assert len(result) == 3
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))


def test__delete_menu_file__2(data_dir, tmp_path):
    # ensure to_file use the same logic as from_file
    src_dir = data_dir / "structure1" / "studio"
    new_dir = tmp_path / "hierarchy"
    shutil.copytree(src_dir, new_dir)
    hierarchy_src = read_menu_hierarchy_as_file(new_dir)
    # video-to-gif-presets.frmb
    file = hierarchy_src[0].children[1]
    assert file.path.name == "video-to-gif-presets.frmb"
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))

    result = delete_menu_file(file, remove_children_dir=True)
    assert len(result) == 4
    assert not file.children_dir.exists()


def test__delete_menu_file__3(data_dir, tmp_path):
    # ensure to_file use the same logic as from_file
    src_dir = data_dir / "structure1" / "studio"
    new_dir = tmp_path / "hierarchy"
    shutil.copytree(src_dir, new_dir)
    hierarchy_src = read_menu_hierarchy_as_file(new_dir)
    # video-to-gif-presets.frmb
    file = hierarchy_src[0].children[1]
    assert file.path.name == "video-to-gif-presets.frmb"
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))

    result = delete_menu_file(file, remove_children=False)
    assert len(result) == 1
    assert file.children_dir.exists()
    assert list(file.children_dir.glob("*"))
