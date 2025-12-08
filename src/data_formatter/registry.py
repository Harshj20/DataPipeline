"""
Plugin registry system for parsers, writers, stylings, and transformers.

This module provides registry classes that allow for dynamic registration
and retrieval of different components, enabling easy extensibility.
"""

from typing import Dict, Type, Callable, Any, Optional


class Registry:
    """Base registry class for managing plugins."""

    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Type] = {}

    def register(self, key: str):
        """
        Decorator for registering a class in the registry.
        
        Usage:
            @registry.register("my_parser")
            class MyParser(BaseParser):
                ...
        """
        def decorator(cls: Type) -> Type:
            if key in self._registry:
                raise ValueError(f"{key} is already registered in {self.name}")
            self._registry[key] = cls
            return cls
        return decorator

    def get(self, key: str) -> Optional[Type]:
        """Get a registered class by key."""
        return self._registry.get(key)

    def list_keys(self) -> list:
        """List all registered keys."""
        return list(self._registry.keys())

    def __contains__(self, key: str) -> bool:
        """Check if a key is registered."""
        return key in self._registry


class ParserRegistry(Registry):
    """Registry for format parsers (CSV, JSON, JSONL, YAML, etc.)."""

    def __init__(self):
        super().__init__("ParserRegistry")


class WriterRegistry(Registry):
    """Registry for format writers (CSV, JSON, JSONL, YAML, etc.)."""

    def __init__(self):
        super().__init__("WriterRegistry")


class StylingRegistry(Registry):
    """Registry for styling converters (OpenAI, Alpaca, ShareGPT, etc.)."""

    def __init__(self):
        super().__init__("StylingRegistry")


class TransformerRegistry(Registry):
    """Registry for data transformers (context prompt, filter, augment, etc.)."""

    def __init__(self):
        super().__init__("TransformerRegistry")


# Global registry instances
parser_registry = ParserRegistry()
writer_registry = WriterRegistry()
styling_registry = StylingRegistry()
transformer_registry = TransformerRegistry()
