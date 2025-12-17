"""Llama2 template specification.

Llama2 uses a different chat format with special tokens and
distinct formatting for instructions and responses.

Format:
    <s>[INST] user message [/INST] assistant response </s>
    
For multi-turn conversations:
    <s>[INST] user message 1 [/INST] assistant response 1 </s>
    <s>[INST] user message 2 [/INST] assistant response 2 </s>

System prompt (optional):
    <s>[INST] <<SYS>>
    system message
    <</SYS>>

    user message [/INST] assistant response </s>
"""

from ..template_spec import ChatTemplateSpec, DelimiterSpec


# Llama2 chat template
# Note: This is a simplified version focusing on the instruction/response pattern
# In real Llama2 templates, system prompts are embedded in the first user message.
# The basic structure is: [INST] instruction [/INST] response </s>
LLAMA2_TEMPLATE = ChatTemplateSpec(
    name="llama2",
    delimiters=[
        DelimiterSpec(
            role="user",
            start_delimiter="[INST] ",
            end_delimiter=" [/INST]"
        ),
        DelimiterSpec(
            role="assistant",
            start_delimiter="[/INST] ",
            end_delimiter=" </s>"
        ),
    ],
    allow_nesting=False,
    normalize_whitespace=True
)

