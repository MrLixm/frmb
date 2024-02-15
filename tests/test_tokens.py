from pathlib import Path

from frmb._tokens import _resolve_tokens
from frmb._tokens import FrmbTokenResolver


def test__resolve_tokens():
    source = "some@DIR @FOO:ex \\@FILE\\"
    expected = f"some/d/dir 45:ex \\{str(Path(__file__))}\\"
    tokens = {"DIR": "/d/dir", "foo": "45", "FILE": str(Path(__file__))}
    result = _resolve_tokens(source, **tokens)
    assert result == expected

    source = "some@@DIR @FOO:ex @f"
    expected = f"some@DIR 45:ex @f"
    tokens = {"DIR": "/d/dir", "foo": "45"}
    result = _resolve_tokens(source, **tokens)
    assert result == expected

    source = "some@@@@DIR @FOO:ex wha\\@@@DIR"
    expected = f"some@@DIR 45:ex wha\\@/d/dir"
    tokens = {"DIR": "/d/dir", "foo": "45"}
    result = _resolve_tokens(source, **tokens)
    assert result == expected


def test__FrmbTokenResolver():

    resolver = FrmbTokenResolver(CWD="foo", ROOT=__file__)

    source = "some@@CWD @ROOT:ex @f"
    expected = f"some@CWD {__file__}:ex @f"
    result = resolver.resolve(source)
    assert result == expected
