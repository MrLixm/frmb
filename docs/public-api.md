# Public API

Those are the available objects that can be imported :

```python
import frmb
```

```python exec="on"
import os
import sys
root = os.environ["MKDOCS_CONFIG_DIR"]
if root not in sys.path:
  sys.path.insert(0, root)

import frmb
print("```python\n")
for obj in sorted(vars(frmb)):
    if obj.startswith("_") and not obj.startswith("__"):
        continue
    print(f"from frmb import {obj}")
print("```")
```

!!! note

    Is called a "hierarchy" a list of root menu entries. The
    hierarchy is parsed by accessing their children recursively.


## reading

::: frmb.read_menu_hierarchy

::: frmb.read_menu_hierarchy_as_file

## processing

::: frmb.validate_menu_hierarchy

::: frmb.generate_reg_from_hierarchy

::: frmb.get_key_path_for_file_association

## writing

::: frmb.write_menu_item_to_file

## objects

::: frmb.FrmbMenuItem

::: frmb.FrmbFile

## tools

::: frmb.CLI

::: frmb.execute_cli

