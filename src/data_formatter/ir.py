"""
Intermediate Representation (IR) for data-formatter.

This module defines the core data structures used as an intermediate
representation between different data formats and stylings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal


# Supported formats
FormatType = Literal["csv", "json", "jsonl", "yaml"]

# Supported stylings
StylingType = Literal[
    "text_label",
    "openai_chat",
    "sharegpt",
    "chatml",
    "alpaca",
    "special_tokens",
    "custom",
]


@dataclass
class DataSample:
    """
    A single data sample in the intermediate representation.
    
    This flexible structure can represent various data stylings:
    - text/label: {"text": "...", "label": "..."}
    - chat formats: {"messages": [...]}
    - custom: any dict structure
    
    Attributes:
        data: The actual data content (flexible dict structure)
        metadata: Optional metadata about this sample (source, id, etc.)
    """
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not isinstance(self.data, dict):
            raise ValueError("DataSample.data must be a dictionary")


@dataclass
class IntermediateRepresentation:
    """
    Container for all data samples with metadata.
    
    This represents the complete dataset in a format-agnostic way,
    allowing for lossless conversion between formats.
    
    Attributes:
        samples: List of all data samples
        source_format: Original format of the data
        source_styling: Original styling of the data
        metadata: Optional global metadata (dataset name, description, etc.)
    """
    samples: List[DataSample] = field(default_factory=list)
    source_format: Optional[FormatType] = None
    source_styling: Optional[StylingType] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        # Ensure samples is a list of DataSample objects
        if not all(isinstance(s, DataSample) for s in self.samples):
            raise ValueError("All samples must be DataSample instances")

    def add_sample(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Add a new sample to the IR."""
        self.samples.append(DataSample(data=data, metadata=metadata))

    def __len__(self) -> int:
        """Return number of samples."""
        return len(self.samples)

    def __iter__(self):
        """Iterate over samples."""
        return iter(self.samples)

    def __getitem__(self, index: int) -> DataSample:
        """Get sample by index."""
        return self.samples[index]
