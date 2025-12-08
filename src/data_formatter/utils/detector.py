"""Auto-detection utilities for format and styling."""

import json
from pathlib import Path
from typing import Optional


def detect_format(file_path: Path) -> Optional[str]:
    """
    Auto-detect file format from extension or content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected format ("csv", "json", "jsonl", "yaml") or None
    """
    # Try extension first
    ext = file_path.suffix.lower()
    extension_map = {
        ".csv": "csv",
        ".json": "json",
        ".jsonl": "jsonl",
        ".yaml": "yaml",
        ".yml": "yaml",
    }
    
    if ext in extension_map:
        return extension_map[ext]
    
    # Try content-based detection
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            
            # Check for JSONL (each line is valid JSON)
            try:
                json.loads(first_line)
                # Check second line if exists
                second_line = f.readline().strip()
                if second_line:
                    json.loads(second_line)
                    return "jsonl"
                return "json"  # Single line JSON
            except json.JSONDecodeError:
                pass
            
            # Check for YAML (starts with --- or has ': ' pattern)
            if first_line.startswith("---") or ": " in first_line:
                return "yaml"
            
            # Check for CSV (has commas)
            if "," in first_line:
                return "csv"
    except Exception:
        pass
    
    return None


def detect_styling(data: dict) -> Optional[str]:
    """
    Auto-detect data styling from structure.
    
    Args:
        data: A data sample (dict)
        
    Returns:
        Detected styling or None
    """
    if not isinstance(data, dict):
        return None
    
    # Check for OpenAI chat format
    if "messages" in data and isinstance(data.get("messages"), list):
        messages = data["messages"]
        if messages and all(isinstance(m, dict) and "role" in m and "content" in m for m in messages):
            return "openai_chat"
    
    # Check for ShareGPT format
    if "conversations" in data and isinstance(data.get("conversations"), list):
        convs = data["conversations"]
        if convs and all(isinstance(c, dict) and "from" in c and "value" in c for c in convs):
            return "sharegpt"
    
    # Check for Alpaca format
    if "instruction" in data or ("output" in data and "input" in data):
        return "alpaca"
    
    # Check for ChatML format
    if "text" in data and isinstance(data.get("text"), str):
        text = data["text"]
        if "<|im_start|>" in text and "<|im_end|>" in text:
            return "chatml"
    
    # Check for simple text/label
    if "text" in data and "label" in data:
        return "text_label"
    
    return None
