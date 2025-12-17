"""Exception hierarchy for reverse parser errors."""


class ReverseParseError(Exception):
    """Base exception for all reverse parsing errors."""
    pass


class UnknownDelimiterError(ReverseParseError):
    """Raised when no valid delimiters are found in the rendered text."""
    pass


class NestedBlockError(ReverseParseError):
    """Raised when overlapping or nested message blocks are detected."""
    pass


class UnclosedBlockError(ReverseParseError):
    """Raised when a message block is started but not properly closed."""
    pass


class EmptyContentError(ReverseParseError):
    """Raised when a message has empty content (depending on policy)."""
    pass


class MalformedTemplateError(ReverseParseError):
    """Raised when the template structure is invalid or ambiguous."""
    pass
