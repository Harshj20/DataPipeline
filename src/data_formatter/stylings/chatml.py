"""ChatML format styling converter."""

from typing import Dict, Any
from data_formatter.ir import DataSample
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry


@styling_registry.register("chatml")
class ChatMLStyling(BaseStyling):
    """
    ChatML format styling with special tokens.
    
    Format: {
        "text": "<|im_start|>system\\n...\\n<|im_end|>\\n<|im_start|>user\\n...\\n<|im_end|>\\n..."
    }
    
    Uses special tokens: <|im_start|>, <|im_end|>
    """

    def to_ir(self, data: Dict[str, Any]) -> DataSample:
        """Convert from ChatML format to IR."""
        if "text" not in data:
            raise ValueError("ChatML format requires 'text' field")
        
        # Parse ChatML text into messages
        text = data["text"]
        messages = []
        
        # Split by <|im_start|> and process each segment
        segments = text.split("<|im_start|>")[1:]  # Skip first empty segment
        
        for segment in segments:
            if not segment.strip():
                continue
            
            # Split by newline to get role and content
            parts = segment.split("\n", 1)
            if len(parts) < 2:
                continue
            
            role = parts[0].strip()
            # Remove <|im_end|> from content
            content = parts[1].replace("<|im_end|>", "").strip()
            
            messages.append({"role": role, "content": content})
        
        # Store as OpenAI-style messages in IR
        return DataSample(data={"messages": messages})

    def from_ir(self, sample: DataSample) -> Dict[str, Any]:
        """Convert from IR to ChatML format."""
        data = sample.data
        
        # If already in ChatML format, return as-is
        if "text" in data and "<|im_start|>" in str(data["text"]):
            return data
        
        # Convert from message-based formats
        messages = None
        
        if "messages" in data and isinstance(data["messages"], list):
            messages = data["messages"]
        elif "conversations" in data and isinstance(data["conversations"], list):
            # Convert from ShareGPT
            messages = []
            for conv in data["conversations"]:
                role_map = {"human": "user", "gpt": "assistant", "system": "system"}
                role = role_map.get(conv.get("from", ""), "user")
                messages.append({"role": role, "content": conv.get("value", "")})
        elif "instruction" in data or "output" in data:
            # Convert from Alpaca
            messages = []
            if "instruction" in data:
                user_content = data["instruction"]
                if "input" in data and data["input"]:
                    user_content += f"\n{data['input']}"
                messages.append({"role": "user", "content": user_content})
            if "output" in data:
                messages.append({"role": "assistant", "content": data["output"]})
        
        if not messages:
            # Fallback
            messages = [{"role": "user", "content": str(data)}]
        
        # Build ChatML text
        chatml_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            chatml_parts.append(f"<|im_start|>{role}\n{content}<|im_end|>")
        
        return {"text": "\n".join(chatml_parts)}
