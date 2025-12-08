"""YAML format writer."""

import yaml
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.writers.base import BaseWriter
from data_formatter.registry import writer_registry


@writer_registry.register("yaml")
class YAMLWriter(BaseWriter):
    """Writer for YAML files."""

    def write(self, ir: IntermediateRepresentation, output_path: Path) -> None:
        """
        Write IR to YAML file as an array of objects.
        
        Uses safe_dump for security.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [sample.data for sample in ir.samples]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
