"""ShareGPT format styling converter."""

from typing import Dict, Any
from data_formatter.ir import DataSample
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry


@styling_registry.register("sharegpt")
class ShareGPTStyling(BaseStyling):
    """
    ShareGPT format styling.
    
    Format: {
        "conversations": [
            {"from": "human", "value": "..."},
            {"from": "gpt", "value": "..."}
        ]
    }
    """

    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """Convert from ShareGPT format to IR."""
        # Validate format
        if "conversations" not in data:
            raise ValueError("ShareGPT format requires 'conversations' field")
        
        conversations = data["conversations"]
        if not isinstance(conversations, list):
            raise ValueError("'conversations' must be a list")
        
        for conv in conversations:
            if not isinstance(conv, dict) or "from" not in conv or "value" not in conv:
                raise ValueError("Each conversation must have 'from' and 'value' fields")
        
        return DataSample(data=data)

    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """Convert from IR to ShareGPT format."""
        data = sample.data
        
        # If already in ShareGPT format, return as-is
        if "conversations" in data and isinstance(data["conversations"], list):
            return data
        
        # Convert from OpenAI chat format
        if "messages" in data and isinstance(data["messages"], list):
            conversations = []
            for msg in data["messages"]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                # Map OpenAI roles to ShareGPT roles
                role_map = {"user": "human", "assistant": "gpt", "system": "system"}
                from_who = role_map.get(role, "human")
                
                conversations.append({
                    "from": from_who,
                    "value": content
                })
            
            return {"conversations": conversations}
        
        # Convert from Alpaca format
        if "instruction" in data or "output" in data:
            conversations = []
            
            # Instruction + input becomes human message
            human_msg = data.get("instruction", "")
            if "input" in data and data["input"]:
                human_msg += f"\n{data['input']}"
            
            if human_msg:
                conversations.append({"from": "human", "value": human_msg})
            
            # Output becomes gpt message
            if "output" in data:
                conversations.append({"from": "gpt", "value": data["output"]})
            
            return {"conversations": conversations}
        
        # Fallback
        return {
            "conversations": [
                {"from": "human", "value": str(data)}
            ]
        }
