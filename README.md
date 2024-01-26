# frmb

Convert file structures to right-click context menu for Windows.

# design

frmb is a python module that take a file structure represented by a root directory
as input and produce Windows registry files (.reg) as output. Once executed,
those reg file create context-menu entry, or allow to remove them.

The file structure is built out of `.frmb` file (json format) with directories.
Each frmb file represent a context menu entry and its configuration, with directories
allowing for nested context menus entries.

# prerequisites

`frmb` has no dependencies, you just need to add its parent directory to 
your `PYTHONPATH` environment variable, so it can be imported.

It of course assume you have python available on your system. Check the
[pyproject.toml](pyproject.toml) for the minimal supported version.

# usage

At any time you can add have a look the unittests in [tests/](tests) for an
actual example.

## 1. creating the file structure

## 2.a. as a command line tool

```shell
python -m frmb --help
```

## 2.b. as a python module

```python
from pathlib import Path
import frmb

root_dir = Path("D:/some/dir")
hierarchy = frmb.read_hierarchy_from_root(root_dir)
reg_content = frmb.generate_reg_from_hierarchy(hierarchy)

print("\n".join(reg_content))
```