# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-02-10

### added

- added `FrmbFile` class
- added `read_menu_hierarchy_as_file` function
- added `enabled` attribute to `FrmbFormat`
- test for `FrmbFormat` hashing 
- changelog visible in documentation

### changed

- ! `frmb.read_hierarchy_from_root_` renamed to `frmb.read_menu_hierarchy`
- ! `frmb.validate_entry_hierarchy` renamed to `frmb.validate_menu_hierarchy`
- new logo, using dark variant instead of light

### fixed

- `@ROOT` token not having the correct value for nested menus.

## [1.0.1] - 2024-01-29

### added

- Added this file.

### changed

- Documentation improvement.

## [1.0.0] - 2024-01-29

Initial release.