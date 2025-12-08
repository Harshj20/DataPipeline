"""OpenAI chat format styling converter."""

from typing import Dict, Any, List
from data_formatter.ir import DataSample
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry


@styling_registry.register("openai_chat")
class OpenAIChatStyling(BaseStyling):
    """
    OpenAI chat format styling.
    
    Format: {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """

    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """Convert from OpenAI chat format to IR."""
        # Validate format
        if "messages" not in data:
            raise ValueError("OpenAI chat format requires 'messages' field")
        
        messages = data["messages"]
        if not isinstance(messages, list):
            raise ValueError("'messages' must be a list")
        
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have 'role' and 'content' fields")
        
        return DataSample(data=data)

    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """Convert from IR to OpenAI chat format."""
        data = sample.data
        
        # If already in OpenAI format, return as-is
        if "messages" in data and isinstance(data["messages"], list):
            return data
        
        # Try to convert from other formats
        # If it has conversations (ShareGPT style), convert it
        if "conversations" in data:
            messages = []
            for conv in data["conversations"]:
                role_map = {"human": "user", "gpt": "assistant", "system": "system"}
                role = role_map.get(conv.get("from", ""), conv.get("from", "user"))
                messages.append({
                    "role": role,
                    "content": conv.get("value", "")
                })
            return {"messages": messages}
        
        # If it has instruction/output (Alpaca style), convert it
        if "instruction" in data or "output" in data:
            messages = []
            if "instruction" in data:
                # Combine instruction and input if present
                user_content = data["instruction"]
                if "input" in data and data["input"]:
                    user_content += f"\n{data['input']}"
                messages.append({"role": "user", "content": user_content})
            if "output" in data:
                messages.append({"role": "assistant", "content": data["output"]})
            return {"messages": messages}
        
        # Fallback: treat entire data as a single user message
        return {
            "messages": [
                {"role": "user", "content": str(data)}
            ]
        }
