from frmb._read import read_menu_hierarchy
from frmb._write import write_menu_item_to_file


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
