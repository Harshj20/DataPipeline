"""Example usage of reverse parser for chat templates."""

from data_formatter.reverse_parser import (
    ReverseParser,
    CHATML_TEMPLATE,
    LLAMA2_TEMPLATE,
    ChatTemplateSpec,
    DelimiterSpec,
)


def example_chatml_parsing():
    """Example: Parse ChatML format."""
    print("=" * 60)
    print("Example 1: ChatML Parsing")
    print("=" * 60)
    
    rendered_chatml = """<|im_start|>user
Hello, how are you?<|im_end|>
<|im_start|>assistant
I'm doing great, thanks for asking!<|im_end|>
<|im_start|>user
What can you help me with?<|im_end|>"""
    
    parser = ReverseParser(CHATML_TEMPLATE)
    messages = parser.parse(rendered_chatml)
    
    print(f"\nRendered ChatML text:")
    print(rendered_chatml)
    print(f"\nParsed {len(messages)} messages:")
    for i, msg in enumerate(messages, 1):
        print(f"  Message {i}: [{msg['role']}] {msg['content']}")
    print()


def example_with_system_prompt():
    """Example: Parse ChatML with system prompt."""
    print("=" * 60)
    print("Example 2: ChatML with System Prompt")
    print("=" * 60)
    
    rendered = """<|im_start|>system
You are a helpful AI assistant.<|im_end|>
<|im_start|>user
Tell me a joke<|im_end|>
<|im_start|>assistant
Why did the Python programmer quit his job?
Because he didn't get arrays!<|im_end|>"""
    
    parser = ReverseParser(CHATML_TEMPLATE)
    messages = parser.parse(rendered)
    
    print(f"\nParsed {len(messages)} messages:")
    for msg in messages:
        print(f"  [{msg['role']}]:")
        print(f"    {msg['content']}")
    print()


def example_custom_template():
    """Example: Define and use a custom template."""
    print("=" * 60)
    print("Example 3: Custom Template")
    print("=" * 60)
    
    # Define a simple custom template
    custom_template = ChatTemplateSpec(
        name="simple_bot",
        delimiters=[
            DelimiterSpec(role="user", start_delimiter="User: ", end_delimiter="\n"),
            DelimiterSpec(role="bot", start_delimiter="Bot: ", end_delimiter="\n"),
        ],
        allow_nesting=False,
        normalize_whitespace=True
    )
    
    rendered = """User: What's the weather today?
Bot: I don't have access to real-time weather data.
User: Can you help me with code?
Bot: Yes, I'd be happy to help!
"""
    
    parser = ReverseParser(custom_template)
    messages = parser.parse(rendered)
    
    print(f"\nCustom template: {custom_template.name}")
    print(f"Rendered text:")
    print(rendered)
    print(f"\nParsed {len(messages)} messages:")
    for msg in messages:
        print(f"  [{msg['role']}] {msg['content']}")
    print()


def example_with_styling():
    """Example: Use reverse parsing through styling classes."""
    print("=" * 60)
    print("Example 4: Using ChatMLStyling")
    print("=" * 60)
    
    from data_formatter.stylings.chatml import ChatMLStyling
    from data_formatter.stylings.openai_chat import OpenAIChatStyling
    
    rendered_chatml = """<|im_start|>user
Can you convert this to OpenAI format?<|im_end|>
<|im_start|>assistant
Yes, absolutely!<|im_end|>"""
    
    # Parse ChatML
    chatml_styling = ChatMLStyling()
    sample = chatml_styling.reverse_parse(rendered_chatml)
    
    print(f"Parsed IR sample:")
    print(f"  {sample.data}")
    
    # Convert to OpenAI format
    openai_styling = OpenAIChatStyling()
    openai_data = openai_styling.from_ir(sample)
    
    print(f"\nConverted to OpenAI format:")
    print(f"  {openai_data}")
    print()


def example_error_handling():
    """Example: Error handling."""
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    from data_formatter.reverse_parser import (
        UnclosedBlockError,
        NestedBlockError,
        UnknownDelimiterError,
    )
    
    parser = ReverseParser(CHATML_TEMPLATE)
    
    # Test unclosed block
    print("\nTest 1: Unclosed block")
    try:
        parser.parse("<|im_start|>user\nHello")
    except UnclosedBlockError as e:
        print(f"  ✓ Caught error: {e}")
    
    # Test unknown delimiter
    print("\nTest 2: Unknown delimiter")
    try:
        parser.parse("This is just plain text")
    except UnknownDelimiterError as e:
        print(f"  ✓ Caught error: {e}")
    
    # Test nested blocks (not allowed in ChatML)
    print("\nTest 3: Nested blocks")
    try:
        parser.parse("<|im_start|>user\nOuter<|im_start|>assistant\nInner<|im_end|><|im_end|>")
    except NestedBlockError as e:
        print(f"  ✓ Caught error: {e}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" Reverse Parser Examples")
    print("=" * 60 + "\n")
    
    example_chatml_parsing()
    example_with_system_prompt()
    example_custom_template()
    example_with_styling()
    example_error_handling()
    
    print("=" * 60)
    print(" All examples completed!")
    print("=" * 60)
