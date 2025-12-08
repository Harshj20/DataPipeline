"""CSV format writer."""

import csv
from pathlib import Path
from data_formatter.ir import IntermediateRepresentation
from data_formatter.writers.base import BaseWriter
from data_formatter.registry import writer_registry


@writer_registry.register("csv")
class CSVWriter(BaseWriter):
    """Writer for CSV files."""

    def write(self, ir: IntermediateRepresentation, output_path: Path) -> None:
        """
        Write IR to CSV file.
        
        All samples must have the same keys (columns).
        Nested structures are flattened or converted to strings.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not ir.samples:
            # Create empty file
            open(output_path, 'w').close()
            return
        
        # Collect all unique keys across all samples
        all_keys = set()
        for sample in ir.samples:
            all_keys.update(sample.data.keys())
        
        fieldnames = sorted(all_keys)  # Consistent ordering
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for sample in ir.samples:
                # Flatten nested structures
                row = {}
                for key in fieldnames:
                    value = sample.data.get(key, '')
                    # Convert non-string values to strings
                    if isinstance(value, (list, dict)):
                        import json
                        row[key] = json.dumps(value, ensure_ascii=False)
                    else:
                        row[key] = str(value) if value is not None else ''
                writer.writerow(row)
