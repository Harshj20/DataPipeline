"""ChatML template specification.

ChatML (Chat Markup Language) is a format used by models like GPT-3.5-turbo,
GPT-4, and various open-source models.

Format:
    <|im_start|>role
    content<|im_end|>

Example:
    <|im_start|>user
    Hello, how are you?<|im_end|>
    <|im_start|>assistant
    I'm doing great, thanks!<|im_end|>
"""

from ..template_spec import ChatTemplateSpec, DelimiterSpec


# ChatML template uses <|im_start|> and <|im_end|> special tokens
# Each message block starts with <|im_start|>role\n and ends with <|im_end|>
CHATML_TEMPLATE = ChatTemplateSpec(
    name="chatml",
    delimiters=[
        DelimiterSpec(
            role="system",
            start_delimiter="<|im_start|>system\n",
            end_delimiter="<|im_end|>"
        ),
        DelimiterSpec(
            role="user",
            start_delimiter="<|im_start|>user\n",
            end_delimiter="<|im_end|>"
        ),
        DelimiterSpec(
            role="assistant",
            start_delimiter="<|im_start|>assistant\n",
            end_delimiter="<|im_end|>"
        ),
    ],
    allow_nesting=False,
    normalize_whitespace=True
)
