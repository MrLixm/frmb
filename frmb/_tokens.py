import dataclasses
import logging
import re

LOGGER = logging.getLogger(__name__)


def _resolve_tokens(source: str, **kwargs) -> str:
    """
    Replace all tokens in the given string with their intended value.

    tokens starts with a ``@`` and are followed by the token name. Example: ``@FILE``.

    Args:
        source: a string that might contains tokens
        **kwargs:
            dict of token with their associated values.
            tokens name can be uppercase or lowercase.

    Returns:
        source string with token replaced
    """
    resolved = source.replace("@@", "%%TMP%%")

    for token_name, token_value in kwargs.items():
        resolved = re.sub(
            rf"@{token_name.upper()}",
            # avoid re to interpret replacement tokens
            token_value.replace("\\", "\\\\"),
            resolved,
        )

    resolved = resolved.replace("%%TMP%%", "@")
    return resolved


@dataclasses.dataclass()
class FrmbTokenResolver:
    """
    List all the tokens that can be found in a Frmb file and allow to resolve them in any string.
    """

    CWD: str
    """
    The parent directory of the `frmb` file (with escaped backslashes).
    """

    ROOT: str
    """
    The top-level directory of the context-menu hierarchy (with escaped backslashes).
    """

    def resolve(self, source: str) -> str:
        """
        Replace all tokens in the given string with their intended value.

        tokens starts with a ``@`` and are followed by the token name. Example: ``@FILE``.

        Args:
            source: a string that might contain tokens

        Returns:
            source string with token replaced
        """

        kwargs = {}
        for item_name, item_value in vars(self).items():
            kwargs[item_name] = str(item_value)

        return _resolve_tokens(source, **kwargs)
