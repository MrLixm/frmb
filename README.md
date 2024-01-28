# frmb

Convert file structures to right-click context menu for Windows.

`frmb` try to simplify the need of creating context-menu in Windows by representing
the context menu as a file structure. This make it easy to add new entries, or
update existing ones. 

`frmb` works with a simple concept where you give a directory path as input,
and produces 2 `.reg` files as output: one for "installing" the context-menu,
and one for "uninstalling it".