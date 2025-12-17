"""Reverse parser for chat templates.

This module provides tools to parse rendered chat template text back into
canonical message structures, enabling conversion between different model-specific
chat formats.

Key components:
- ChatTemplateSpec: Template contract definition
- ReverseParser: Main parser orchestrating the scanning/parsing/composing pipeline
- TemplateAnalyzer: Auto-generate specs from Jinja2 templates (future)
- Built-in templates: Pre-defined specs for common formats
"""

from .template_spec import ChatTemplateSpec, DelimiterSpec
from .parser import ReverseParser, Scanner, MessageParser, MessageComposer
from .exceptions import (
    ReverseParseError,
    UnknownDelimiterError,
    NestedBlockError,
    UnclosedBlockError,
    EmptyContentError,
    MalformedTemplateError,
)
from .templates import CHATML_TEMPLATE, LLAMA2_TEMPLATE

__all__ = [
    # Template specifications
    "ChatTemplateSpec",
    "DelimiterSpec",
    # Parser components
    "ReverseParser",
    "Scanner",
    "MessageParser",
    "MessageComposer",
    # Exceptions
    "ReverseParseError",
    "UnknownDelimiterError",
    "NestedBlockError",
    "UnclosedBlockError",
    "EmptyContentError",
    "MalformedTemplateError",
    # Built-in templates
    "CHATML_TEMPLATE",
    "LLAMA2_TEMPLATE",
]
