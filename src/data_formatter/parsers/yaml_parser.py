"""YAML format parser."""

import yaml
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.parsers.base import BaseParser
from data_formatter.registry import parser_registry


@parser_registry.register("yaml")
class YAMLParser(BaseParser):
    """Parser for YAML files."""

    def parse(self, file_path: Path) -> IntermediateRepresentation:
        """
        Parse a YAML file.
        
        Handles:
        - Multi-document YAML (separated by ---)
        - Single document (object or array)
        """
        ir = IntermediateRepresentation(source_format="yaml")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Use safe_load_all to handle multi-document YAML
            documents = list(yaml.safe_load_all(f))
        
        for doc in documents:
            if doc is None:
                continue
                
            if isinstance(doc, list):
                # Array of samples
                for item in doc:
                    if isinstance(item, dict):
                        ir.add_sample(item)
                    else:
                        ir.add_sample({"value": item})
            elif isinstance(doc, dict):
                # Single sample or container
                if "data" in doc and isinstance(doc["data"], list):
                    for item in doc["data"]:
                        if isinstance(item, dict):
                            ir.add_sample(item)
                        else:
                            ir.add_sample({"value": item})
                else:
                    ir.add_sample(doc)
            else:
                # Primitive value
                ir.add_sample({"value": doc})
        
        return ir
