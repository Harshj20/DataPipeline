"""CSV format parser."""

import csv
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.parsers.base import BaseParser
from data_formatter.registry import parser_registry


@parser_registry.register("csv")
class CSVParser(BaseParser):
    """Parser for CSV files."""

    def parse(self, file_path: Path) -> IntermediateRepresentation:
        """
        Parse a CSV file using the csv module.
        
        First row is treated as headers.
        Each subsequent row becomes a dict sample.
        """
        ir = IntermediateRepresentation(source_format="csv")
        
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # DictReader gives OrderedDict, convert to regular dict
                ir.add_sample(dict(row))
        
        return ir
