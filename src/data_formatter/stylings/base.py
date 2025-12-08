"""Base class for styling converters."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from data_formatter.ir import IntermediateRepresentation, DataSample


class BaseStyling(ABC):
    """Abstract base class for all styling converters."""

    @abstractmethod
    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """
        Convert from this styling to intermediate representation.
        
        Args:
            data: Data in this specific styling format
            
        Returns:
            DataSample in IR format
        """
        pass

    @abstractmethod
    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """
        Convert from intermediate representation to this styling.
        
        Args:
            sample: DataSample in IR format
            
        Returns:
            Data in this specific styling format
        """
        pass
