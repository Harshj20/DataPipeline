"""JSON format writer."""

import json
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.writers.base import BaseWriter
from data_formatter.registry import writer_registry


@writer_registry.register("json")
class JSONWriter(BaseWriter):
    """Writer for JSON files (array format)."""

    def write(self, ir: IntermediateRepresentation, output_path: Path) -> None:
        """
        Write IR to JSON file as an array of objects.
        
        Format: [{"a": 1}, {"b": 2}, ...]
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [sample.data for sample in ir.samples]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
