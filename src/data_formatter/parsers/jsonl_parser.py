"""JSONL (JSON Lines) format parser."""

import json
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation, DataSample
from data_formatter.parsers.base import BaseParser
from data_formatter.registry import parser_registry


@parser_registry.register("jsonl")
class JSONLParser(BaseParser):
    """Parser for JSONL (newline-delimited JSON) files."""

    def parse(self, file_path: Path) -> IntermediateRepresentation:
        """
        Parse a JSONL file line by line.
        
        Each line should be a valid JSON object.
        Memory-efficient for large files.
        """
        ir = IntermediateRepresentation(source_format="jsonl")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                try:
                    data = json.loads(line)
                    if not isinstance(data, dict):
                        data = {"value": data}  # Wrap non-dict values
                    ir.add_sample(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_num} in {file_path}: {e}")
        
        return ir
