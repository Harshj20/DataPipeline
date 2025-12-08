"""Base class for format parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation


class BaseParser(ABC):
    """Abstract base class for all format parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> IntermediateRepresentation:
        """
        Parse a file and convert it to intermediate representation.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            IntermediateRepresentation containing the parsed data
        """
        pass
