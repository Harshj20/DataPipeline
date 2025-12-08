"""Base class for format writers."""

from abc import ABC, abstractmethod
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation


class BaseWriter(ABC):
    """Abstract base class for all format writers."""

    @abstractmethod
    def write(self, ir: IntermediateRepresentation, output_path: Path) -> None:
        """
        Write intermediate representation to a file.
        
        Args:
            ir: IntermediateRepresentation to write
            output_path: Path where the file should be written
        """
        pass
