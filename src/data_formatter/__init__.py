"""
Data Formatter - Convert between data formats and chat stylings.

A scalable Python module for converting between different data formats
(CSV, JSON, JSONL, YAML) and chat stylings (OpenAI, Alpaca, ShareGPT, ChatML)
using an intermediate representation approach inspired by compiler design.
"""

import sys
from pathlib import Path

# Import all components to trigger registry registration
from data_formatter.ir import IntermediateRepresentation, DataSample
from data_formatter.registry import (
    parser_registry,
    writer_registry,
    styling_registry,
    transformer_registry
)

# Import parsers (triggers registration)
from data_formatter.parsers import (
    JSONLParser,
    JSONParser,
    CSVParser,
    YAMLParser
)

# Import writers (triggers registration)
from data_formatter.writers import (
    JSONLWriter,
    JSONWriter,
    CSVWriter,
    YAMLWriter
)

# Import stylings (triggers registration)
from data_formatter.stylings import (
    TextLabelStyling,
    OpenAIChatStyling,
    AlpacaStyling,
    ShareGPTStyling,
    ChatMLStyling
)

# Import transformers (triggers registration)
from data_formatter.transformers import ContextPromptTransformer

# Import main API
from data_formatter.converter import DataFormatter
from data_formatter.utils.config import load_data_config


__version__ = "0.1.0"

__all__ = [
    "DataFormatter",
    "load_data_config",
    "IntermediateRepresentation",
    "DataSample",
]


def main():
    """
    CLI entry point (optional convenience wrapper).
    
    Primary usage is via Python API, but this provides basic CLI support.
    """
    if len(sys.argv) < 3:
        print("Usage: data-formatter <data_config.json> <target_styling> [target_format]")
        print("\nExample:")
        print("  data-formatter data_config.json openai_chat jsonl")
        sys.exit(1)
    
    config_path = sys.argv[1]
    target_styling = sys.argv[2]
    target_format = sys.argv[3] if len(sys.argv) > 3 else "jsonl"
    
    try:
        # Load data config
        data_config = load_data_config(config_path)
        
        # Create formatter and convert
        formatter = DataFormatter(data_config)
        output_paths = formatter.convert(
            target_styling=target_styling,
            target_format=target_format
        )
        
        print(f"✓ Converted {len(output_paths)} file(s)")
        for path in output_paths:
            print(f"  → {path}")
    
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
