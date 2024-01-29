# Introduction

Frmb is a python library and CLI to convert file structures to right-click 
context menu for Windows.

![demo video of creating the context-menu](img/demo.gif)

You can find an example of file-structure here: 
[https://github.com/MrLixm/lxm-frmb-projects](https://github.com/MrLixm/lxm-frmb-projects)

## :material-palette: design

frmb is a python module that take a file structure represented by a root directory
as input and produce Windows registry files (.reg) as output. Once executed,
those reg file create or remove context-menus.

The file structure is built out of `.frmb` file (json format) with directories.
Each frmb file represent a context menu entry and its configuration, with directories
allowing for nested context menus entries.

Note the approach is not dynamic, every modification to the file structure
need to be "baked" again as a reg file on each update.

## :material-file-download: installation

`frmb` has no dependencies, simply check the `pyproject.toml` for the minimal
python version required.

### with `pip`

Assuming you are already in the venv you want to install to:

```powershell
pip install git+https://github.com/MrLixm/frmb.git@main
```

### with `poetry`

Add the following to your existing project :

```toml title="pyproject.toml"
[tool.poetry.dependencies]
frmb = { git = "https://github.com/MrLixm/frmb.git", branch = "main"}
```

### manually

Assuming `git` is installed on your system, you just need to add its parent
directory to your `PYTHONPATH`.

```powershell title="powershell"
cd myenv/
git clone https://github.com/MrLixm/frmb.git
# only set for the current session
$env:PYTHONPATH += ";$((Get-Item .).FullName)"
```