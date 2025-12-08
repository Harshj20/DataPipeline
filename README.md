# Data Formatter

A scalable Python module for converting between different data formats and chat stylings using an intermediate representation (IR) approach inspired by compiler design.

## Features

- **Format Support**: CSV, JSON, JSONL, YAML
- **Chat Stylings**: OpenAI, Alpaca, ShareGPT, ChatML, Text/Label
- **Transformations**: Context prompt injection/replacement and more
- **IR-Based Architecture**: Clean separation between formats and stylings
- **Plugin System**: Easy to extend with new formats, stylings, and transformers
- **Auto-Detection**: Automatic format and styling detection
- **Scalable Design**: Add custom components without modifying core code

## Installation

```bash
cd e:/antigravity/data-formatter
uv sync
```

## Quick Start

### Python API (Primary Usage)

```python
from data_formatter import DataFormatter, load_data_config

# Load data configuration
data_config = load_data_config("data_config.json")

# Create formatter
formatter = DataFormatter(data_config)

# Basic conversion
formatter.convert(target_styling="openai_chat")

# With context prompt injection
formatter.convert(
    target_styling="openai_chat",
    transformations=[
        {
            "type": "context_prompt",
            "config": {
                "prompt_text": "You are a helpful assistant.",
                "role": "system"
            }
        }
    ]
)
```

### Data Config Format

The `data_config.json` follows this **non-negotiable** schema:

```json
{
  "data": [
    {
      "data_path": "./data/dataset.jsonl"
    }
  ]
}
```

**Optional fields** per data entry:
- `format`: File format (csv/json/jsonl/yaml) - auto-detected if omitted
- `styling`: Data styling - auto-detected if omitted
- `name`: Human-readable name for logging

## Architecture

```
Parser → IR → Styling Converter → Transformers → Writer
```

### Pipeline Flow

1. **Parse**: Read file using format parser (CSV, JSON, JSONL, YAML)
2. **To IR**: Convert to Intermediate Representation (format-agnostic)
3. **Convert Styling**: Transform between chat stylings
4. **Transform**: Apply data transformations (context prompts, etc.)
5. **Write**: Output in target format

## Supported Stylings

- **openai_chat**: `{"messages": [{"role": "...", "content": "..."}]}`
- **alpaca**: `{"instruction": "...", "input": "...", "output": "..."}`
- **sharegpt**: `{"conversations": [{"from": "...", "value": "..."}]}`
- **chatml**: Text with `<|im_start|>` and `<|im_end|>` tokens
- **text_label**: Simple `{"text": "...", "label": "..."}`

## Transformations

### Context Prompt Injection

Add system/context prompts to chat data:

```python
formatter.convert(
    target_styling="openai_chat",
    transformations=[
        {
            "type": "context_prompt",
            "config": {
                "prompt_text": "You are a helpful assistant.",
                "position": "prepend",  # or "append"
                "role": "system",
                "replace_existing": False,  # or True to replace
                "marker": "__data_formatter_v1__"  # for tracking
            }
        }
    ]
)
```

## Extending the Module

### Adding a New Format Parser

1. Create `src/data_formatter/parsers/my_format_parser.py`:

```python
from data_formatter.parsers.base import BaseParser
from data_formatter.registry import parser_registry

@parser_registry.register("my_format")
class MyFormatParser(BaseParser):
    def parse(self, file_path):
        # Implementation
        pass
```

2. Import in `src/data_formatter/parsers/__init__.py`

### Adding a New Styling

1. Create `src/data_formatter/stylings/my_styling.py`:

```python
from data_formatter.stylings.base import BaseStyling
from data_formatter.registry import styling_registry

@styling_registry.register("my_styling")
class MyStyling(BaseStyling):
    def to_ir(self, data):
        # Convert to IR
        pass
    
    def from_ir(self, sample):
        # Convert from IR
        pass
```

2. Import in `src/data_formatter/stylings/__init__.py`

### Adding a New Transformer

1. Create `src/data_formatter/transformers/my_transformer.py`:

```python
from data_formatter.transformers.base import BaseTransformer
from data_formatter.registry import transformer_registry

@transformer_registry.register("my_transformer")
class MyTransformer(BaseTransformer):
    def transform(self, ir):
        # Transform IR
        return ir
```

2. Import in `src/data_formatter/transformers/__init__.py`

## Examples

See `examples/usage.py` for comprehensive usage examples.

```bash
uv run python examples/usage.py
```

## Optional CLI

```bash
uv run data-formatter data_config.json openai_chat jsonl
```

## License

MIT

## Contributing

Contributions welcome! The modular design makes it easy to add new formats, stylings, and transformers.
