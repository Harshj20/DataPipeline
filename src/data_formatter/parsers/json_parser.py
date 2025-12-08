"""JSON format parser."""

import json
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation, DataSample
from data_formatter.parsers.base import BaseParser
from data_formatter.registry import parser_registry


@parser_registry.register("json")
class JSONParser(BaseParser):
    """Parser for JSON files (single object or array)."""

    def parse(self, file_path: Path) -> IntermediateRepresentation:
        """
        Parse a JSON file.
        
        Handles:
        - Array of objects: [{"a": 1}, {"b": 2}]
        - Single object: {"data": [...]}
        """
        ir = IntermediateRepresentation(source_format="json")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # Array of samples
            for item in data:
                if isinstance(item, dict):
                    ir.add_sample(item)
                else:
                    ir.add_sample({"value": item})
        elif isinstance(data, dict):
            # Could be a single sample or a container with data array
            if "data" in data and isinstance(data["data"], list):
                # Container format: {"data": [...]}
                for item in data["data"]:
                    if isinstance(item, dict):
                        ir.add_sample(item)
                    else:
                        ir.add_sample({"value": item})
            else:
                # Single sample
                ir.add_sample(data)
        else:
            # Primitive value
            ir.add_sample({"value": data})
        
        return ir
