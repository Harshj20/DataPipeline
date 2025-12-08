"""Output file naming utilities."""

from pathlib import Path
from typing import Literal


def get_output_path(
    input_path: Path,
    target_styling: str,
    target_format: str = "jsonl",
    output_mode: Literal["new_file", "inplace"] = "new_file"
) -> Path:
    """
    Generate output file path based on configuration.
    
    Args:
        input_path: Original input file path
        target_styling: Target styling name
        target_format: Target file format
        output_mode: "new_file" or "inplace"
        
    Returns:
        Path object for output file
    """
    if output_mode == "inplace":
        return input_path
    
    # new_file mode: create filename with pattern {original_name}_{target_styling}.{extension}
    stem = input_path.stem
    new_stem = f"{stem}_{target_styling}"
    
    # Determine extension from format
    format_to_ext = {
        "json": ".json",
        "jsonl": ".jsonl",
        "csv": ".csv",
        "yaml": ".yaml",
    }
    
    extension = format_to_ext.get(target_format, f".{target_format}")
    
    return input_path.parent / f"{new_stem}{extension}"
