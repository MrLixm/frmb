# Contribution guidelines

Thanks for taking in some of your time to invest in this project !

To make the development process better for everyone, please read and apply the
following guidelines.

As much as it is appreciated you contribute to this project, it is possible
we don't agree on your contribution, even how good or proved it is. In that
case please remember that the owners have the right to decide in which direction
their project should go. You are free to create your own fork !

## what to contribute

You have found a bug/issue or wish to submit an enhancement suggestion ?

> Open a [new issue](https://github.com/MrLixm/frmb/issues).

You have already read the code and found how to modify it to apply you
changes ?

> Still open an issue first please ! Even if it's a simple change it might not
> be wanted for the project and that would be sad to work on a pull-request
> that will never be merged.

## working on the code

You have opened an issue OR found an issue that **have been approved**, you
can start by forking this repository.

Clone your fork locally and start working on your changes.

Once satisfied you can open a pull-request to merge the desired branch of your
fork, to the `main` branch of this repository.

### requirements

- Ensure the [Black formatter](https://black.readthedocs.io/en/stable/) is
  enabled (triggered on each save) and all section of code you wrote have been
  formatted.
- Ensure you have successfully run unittests before creating the PR.
- Ensure you have some of your favorite hot beverage available for drinking to
  ensure maximum confort during development.

## code style

Try to keep things simple (avoiding overengineering), and most importantly
easily understandable.

### black

For black it is recommended to enforce use of trailling comma when necessary. Example :
```python
class Foo:
    def some_really_really_long_method(self, myparam: str, some_other_param: dict[str, str]) -> int:
        pass
```
Would be formatted by black as 

```python
class Foo:
    def some_really_really_long_method(
        self, myparam: str, some_other_param: dict[str, str]
    ) -> int:
        pass
```

But it is recommended to add a tailling comma after `dict[str, str]` to force line breaks :

```python
class Foo:
    def some_really_really_long_method(
        self,
        myparam: str,
        some_other_param: dict[str, str],
    ) -> int:
        pass
```

### naming conventions

Follow PEP8 conventions.

- variables, functions and methods are `snake_case`
- classes are `PascalCase`
- global variables are usually `UPPERCASE`/`UPPER_CASE` but MIGHT be `snake_case`

#### functions and methods:

- should start with a verb
- `has...` and `is...` must return a `bool`-like object (ex: can return a str or None)

#### modules :

Extensive use of private modules, prefixed by a `_`. Anything private is not
considered to be part of the public API, this means that major changes to them
are not considered "breaking".

As an example, user cannot do this :

```python
from my_module._window import MainWindow
```

The useful `MainWindow` object is exposed in the `my_module`'s `__init__` :

```python
from my_module import MainWindow
```

this allow us to freely rename/move `_window.py` without being considered a breaking
change as it is not supposed to be accessed outside the package.

**The logic is also applied similarly to functions/methods/...**

## version control

Using `git` as you have probably noticed. 

### commits

To ensure a clean commit history please try to apply the following rules :

- separate the commit title and body with a blanck line
- the commit title must be around 72 characters max (80max)
- commits try to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) specification :
  - `<type>(<optional scope>): <description>`
  - where `<type>` is usually `fix` or `feat` (see linked spec for others)