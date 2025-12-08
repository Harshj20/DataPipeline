"""Context prompt transformer for injecting/replacing system prompts."""

from copy import deepcopy
from typing import Literal
from data_formatter.ir import IntermediateRepresentation
from data_formatter.transformers.base import BaseTransformer
from data_formatter.registry import transformer_registry


@transformer_registry.register("context_prompt")
class ContextPromptTransformer(BaseTransformer):
    """
    Transformer for adding or replacing context prompts in chat data.
    
    Config options:
        - prompt_text (str): The context prompt to add/replace
        - role (str): Role for the prompt (default: "system")
        - position (str): "prepend" or "append" (default: "prepend")
        - replace_existing (bool): Replace existing prompts with the same marker (default: False)
        - marker (str): Marker to identify module-generated prompts (default: "__data_formatter_v1__")
    """

    def transform(self, ir: IntermediateRepresentation) -> IntermediateRepresentation:
        """Transform IR by injecting/replacing context prompts."""
        # Extract config
        prompt_text = self.config.get("prompt_text", "")
        role = self.config.get("role", "system")
        position = self.config.get("position", "prepend")
        replace_existing = self.config.get ("replace_existing", False)
        marker = self.config.get("marker", "__data_formatter_v1__")
        
        if not prompt_text:
            return ir  # No prompt to add
        
        # Create new IR to avoid modifying original
        new_ir = IntermediateRepresentation(
            source_format=ir.source_format,
            source_styling=ir.source_styling,
            metadata=ir.metadata
        )
        
        for sample in ir.samples:
            new_data = deepcopy(sample.data)
            
            # Handle message-based formats (OpenAI, ShareGPT-converted, ChatML-converted)
            if "messages" in new_data and isinstance(new_data["messages"], list):
                messages = new_data["messages"]
                
                # Create new prompt message with marker
                new_prompt = {
                    "role": role,
                    "content": prompt_text,
                    "_marker": marker  # Internal marker for tracking
                }
                
                if replace_existing:
                    # Remove existing prompts with the same marker
                    messages = [msg for msg in messages 
                               if msg.get("_marker") != marker]
                    new_data["messages"] = messages
                
                # Add new prompt
                if position == "prepend":
                    new_data["messages"].insert(0, new_prompt)
                else:  # append
                    new_data["messages"].append(new_prompt)
            
            # Handle conversations format (ShareGPT)
            elif "conversations" in new_data and isinstance(new_data["conversations"], list):
                conversations = new_data["conversations"]
                
                # Map role to ShareGPT format
                from_who = "system" if role == "system" else role
                new_conv = {
                    "from": from_who,
                    "value": prompt_text,
                    "_marker": marker
                }
                
                if replace_existing:
                    conversations = [conv for conv in conversations 
                                   if conv.get("_marker") != marker]
                    new_data["conversations"] = conversations
                
                if position == "prepend":
                    new_data["conversations"].insert(0, new_conv)
                else:
                    new_data["conversations"].append(new_conv)
            
            # For other formats, add as a new field or wrap
            # This is a fallback - in practice, transformations work best on chat formats
            
            new_ir.add_sample(new_data, metadata=sample.metadata)
        
        return new_ir
