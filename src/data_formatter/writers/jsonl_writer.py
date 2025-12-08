"""JSONL (JSON Lines) format writer."""

import json
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.writers.base import BaseWriter
from data_formatter.registry import writer_registry


@writer_registry.register("jsonl")
class JSONLWriter(BaseWriter):
    """Writer for JSONL (newline-delimited JSON) files."""

    def write(self, ir: IntermediateRepresentation, output_path: Path) -> None:
        """
        Write IR to JSONL file (one JSON object per line).
        
        Memory-efficient for large datasets.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in ir.samples:
                json.dump(sample.data, f, ensure_ascii=False)
                f.write('\n')
