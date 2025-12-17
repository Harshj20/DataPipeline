"""Base class for styling converters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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
    
    def get_template_spec(self) -> Optional[Any]:
        """
        Return template specification if styling supports reverse parsing.
        
        Returns:
            ChatTemplateSpec if styling is reversible, None otherwise
        """
        return None
    
    def reverse_parse(self, rendered_text: str) -> DataSample:
        """
        Parse rendered template text back to IR (optional capability).
        
        This method enables parsing text that was rendered using this styling's
        template back into canonical message format. Not all stylings need to
        support this - it's primarily useful for template-based chat formats.
        
        Default implementation uses get_template_spec() if available.
        Subclasses can override for custom parsing logic.
        
        Args:
            rendered_text: Text rendered by this styling's template
            
        Returns:
            DataSample in IR format with parsed messages
            
        Raises:
            NotImplementedError: If styling doesn't support reverse parsing
            
        Example:
            >>> # For ChatML styling
            >>> styling = ChatMLStyling()
            >>> rendered = "<|im_start|>user\\nHello<|im_end|>"
            >>> sample = styling.reverse_parse(rendered)
            >>> sample.data["messages"]
            [{"role": "user", "content": "Hello"}]
        """
        template_spec = self.get_template_spec()
        if template_spec is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not support reverse parsing. "
                f"Override get_template_spec() to enable this feature."
            )
        
        # Import here to avoid circular dependency
        from data_formatter.reverse_parser import ReverseParser
        
        parser = ReverseParser(template_spec)
        messages = parser.parse(rendered_text)
        return DataSample(data={"messages": messages})

