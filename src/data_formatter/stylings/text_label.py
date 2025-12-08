"""Text/Label styling converter."""

from typing import Dict, Any
from data_formatter.ir import DataSample
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry


@styling_registry.register("text_label")
class TextLabelStyling(BaseStyling):
    """
    Simple text/label styling.
    
    Format: {"text": "...", "label": "..."}
    """

    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """Convert from text/label format to IR."""
        # Already in simple format, just wrap in DataSample
        return DataSample(data=data)

    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """Convert from IR to text/label format."""
        # If data has text and label, return as-is
        if "text" in sample.data and "label" in sample.data:
            return sample.data
        
        # Try to extract text/label from other formats
        data = sample.data.copy()
        
        # If it's already compatible, return it
        return data
