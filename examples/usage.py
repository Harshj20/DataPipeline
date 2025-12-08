"""
Example usage of the data-formatter Python API.

This script demonstrates various conversion scenarios.
"""

from data_formatter import DataFormatter, load_data_config


def main():
    print("=" * 60)
    print("Data Formatter - Example Usage")
    print("=" * 60)
    
    # Load data configuration
    print("\n1. Loading data configuration...")
    data_config = load_data_config("examples/data_config.json")
    print(f"   Loaded {len(data_config.data)} dataset(s)")
    
    # Create formatter instance
    formatter = DataFormatter(data_config)
    
    # Example 1: Basic conversion to Alpaca format
    print("\n2. Converting to Alpaca format...")
    output_paths = formatter.convert(target_styling="alpaca")
    print(f"   ✓ Output: {output_paths[0]}")
    
    # Example 2: Convert to ShareGPT format
    print("\n3. Converting to ShareGPT format...")
    output_paths = formatter.convert(target_styling="sharegpt")
    print(f"   ✓ Output: {output_paths[0]}")
    
    # Example 3: Convert with context prompt injection
    print("\n4. Converting with context prompt injection...")
    output_paths = formatter.convert(
        target_styling="openai_chat",
        transformations=[
            {
                "type": "context_prompt",
                "config": {
                    "prompt_text": "You are a helpful AI assistant specialized in explaining technical concepts.",
                    "position": "prepend",
                    "role": "system",
                    "marker": "__data_formatter_v1__"
                }
            }
        ]
    )
    print(f"   ✓ Output: {output_paths[0]}")
    
    # Example 4: Convert to ChatML format
    print("\n5. Converting to ChatML format...")
    output_paths = formatter.convert(
        target_styling="chatml",
        target_format="json"
    )
    print(f"   ✓ Output: {output_paths[0]}")
    
    # Example 5: Multiple transformations
    print("\n6. Converting with prompt replacement...")
    output_paths = formatter.convert(
        target_styling="openai_chat",
        transformations=[
            {
                "type": "context_prompt",
                "config": {
                    "prompt_text": "UPDATED: You are an expert AI tutor.",
                    "position": "prepend",
                    "role": "system",
                    "replace_existing": True,
                    "marker": "__data_formatter_v1__"
                }
            }
        ]
    )
    print(f"   ✓ Output: {output_paths[0]}")
    
    print("\n" + "=" * 60)
    print("All conversions completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
