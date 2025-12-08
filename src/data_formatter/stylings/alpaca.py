"""Alpaca format styling converter."""

from typing import Dict, Any
from data_formatter.ir import DataSample
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry


@styling_registry.register("alpaca")
class AlpacaStyling(BaseStyling):
    """
    Alpaca format styling.
    
    Format: {
        "instruction": "...",
        "input": "...",  # optional
        "output": "..."
    }
    """

    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """Convert from Alpaca format to IR."""
        # Validate format
        if "instruction" not in data and "output" not in data:
            raise ValueError("Alpaca format requires at least 'instruction' or 'output' field")
        
        return DataSample(data=data)

    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """Convert from IR to Alpaca format."""
        data = sample.data
        
        # If already in Alpaca format, return as-is
        if "instruction" in data or "output" in data:
            result = {}
            if "instruction" in data:
                result["instruction"] = data["instruction"]
            if "input" in data:
                result["input"] = data["input"]
            if "output" in data:
                result["output"] = data["output"]
            return result
        
        # Convert from OpenAI chat format
        if "messages" in data and isinstance(data["messages"], list):
            messages = data["messages"]
            result = {"instruction": "", "input": "", "output": ""}
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "system":
                    # System message becomes part of instruction
                    result["instruction"] = content
                elif role == "user":
                    # User message is the instruction (or input if instruction exists)
                    if not result["instruction"]:
                        result["instruction"] = content
                    else:
                        result["input"] = content
                elif role == "assistant":
                    # Assistant message is the output
                    result["output"] = content
            
            # Remove empty input field
            if not result["input"]:
                del result["input"]
            
            return result
        
        # Convert from ShareGPT format
        if "conversations" in data:
            result = {"instruction": "", "input": "", "output": ""}
            
            for conv in data["conversations"]:
                from_who = conv.get("from", "")
                value = conv.get("value", "")
                
                if from_who == "system":
                    result["instruction"] = value
                elif from_who == "human":
                    if not result["instruction"]:
                        result["instruction"] = value
                    else:
                        result["input"] = value
                elif from_who == "gpt":
                    result["output"] = value
            
            if not result["input"]:
                del result["input"]
            
            return result
        
        # Fallback
        return {
            "instruction": str(data),
            "output": ""
        }
