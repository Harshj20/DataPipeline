"""Base class for data transformers."""

from abc import ABC, abstractmethod
from data_formatter.ir import IntermediateRepresentation


class BaseTransformer(ABC):
    """Abstract base class for all data transformers."""

    def __init__(self, config: dict = None):
        """
        Initialize transformer with configuration.
        
        Args:
            config: Configuration dictionary for the transformer
        """
        self.config = config or {}

    @abstractmethod
    def transform(self, ir: IntermediateRepresentation) -> IntermediateRepresentation:
        """
        Transform the intermediate representation.
        
        Args:
            ir: IntermediateRepresentation to transform
            
        Returns:
            Transformed IntermediateRepresentation
        """
        pass
