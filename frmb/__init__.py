__version__ = "2.0.0"

from ._parsing import FrmbFormat
from ._parsing import FrmbFile
from ._parsing import read_menu_hierarchy_as_file
from ._parsing import read_menu_hierarchy
from ._parsing import validate_menu_hierarchy
from ._windows import generate_reg_from_hierarchy
from ._cli import CLI
from .__main__ import execute_cli

__all__ = [
    "FrmbFormat",
    "FrmbFile",
    "read_menu_hierarchy_as_file",
    "read_menu_hierarchy",
    "validate_menu_hierarchy",
    "generate_reg_from_hierarchy",
    "CLI",
    "execute_cli",
]
