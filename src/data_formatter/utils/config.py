"""Configuration handling for data formatter."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal


@dataclass
class DataEntry:
    """Single data entry in data config."""
    data_path: str
    format: Optional[str] = None  # Auto-detect if None
    styling: Optional[str] = None  # Auto-detect if None
    name: Optional[str] = None  # Human-readable name


@dataclass
class DataConfig:
    """
    Data configuration following the schema:
    {
        "data": [
            {"data_path": "..."}
        ]
    }
    """
    data: List[DataEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DataConfig":
        """Create DataConfig from dictionary."""
        if "data" not in config_dict:
            raise ValueError("data_config.json must have 'data' field")
        
        data_list = config_dict["data"]
        if not isinstance(data_list, list):
            raise ValueError("'data' field must be a list")
        
        entries = []
        for item in data_list:
            if not isinstance(item, dict):
                raise ValueError("Each data entry must be a dictionary")
            if "data_path" not in item:
                raise ValueError("Each data entry must have 'data_path' field")
            
            entries.append(DataEntry(
                data_path=item["data_path"],
                format=item.get("format"),
                styling=item.get("styling"),
                name=item.get("name")
            ))
        
        return cls(data=entries)


@dataclass
class ConversionConfig:
    """
    Conversion configuration passed via Python API.
    
    Parameters:
        target_styling: Target styling format (required)
        target_format: Target file format (default: jsonl)
        output_mode: "new_file" or "inplace" (default: new_file)
        transformations: List of transformations to apply
    """
    target_styling: str
    target_format: str = "jsonl"
    output_mode: Literal["new_file", "inplace"] = "new_file"
    transformations: List[Dict[str, Any]] = field(default_factory=list)


def load_data_config(config_path: str) -> DataConfig:
    """
    Load data configuration from JSON file.
    
    Args:
        config_path: Path to data_config.json
        
    Returns:
        DataConfig instance
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
    
    return DataConfig.from_dict(config_dict)
