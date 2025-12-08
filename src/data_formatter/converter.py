"""Main converter orchestrating the data formatting pipeline."""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from data_formatter.ir import IntermediateRepresentation
from data_formatter.registry import (
    parser_registry,
    writer_registry,
    styling_registry,
    transformer_registry
)
from data_formatter.utils.config import DataConfig, ConversionConfig, DataEntry
from data_formatter.utils.detector import detect_format, detect_styling
from data_formatter.utils.naming import get_output_path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DataFormatter:
    """
    Main class for data formatting operations.
    
    Orchestrates the pipeline: Parser → IR → Styling → Transformations → Writer
    """

    def __init__(self, data_config: DataConfig):
        """
        Initialize DataFormatter with data configuration.
        
        Args:
            data_config: DataConfig instance with source data information
        """
        self.data_config = data_config

    def convert(
        self,
        target_styling: str,
        target_format: str = "jsonl",
        output_mode: str = "new_file",
        transformations: Optional[List[Dict[str, Any]]] = None
    ) -> List[Path]:
        """
        Convert datasets to target styling and format.
        
        Args:
            target_styling: Target styling (e.g., "openai_chat", "alpaca")
            target_format: Target format (e.g., "jsonl", "json", "csv", "yaml")
            output_mode: "new_file" or "inplace"
            transformations: List of transformation configs
            
        Returns:
            List of output file paths
        """
        conversion_config = ConversionConfig(
            target_styling=target_styling,
            target_format=target_format,
            output_mode=output_mode,
            transformations=transformations or []
        )
        
        output_paths = []
        
        for entry in self.data_config.data:
            try:
                output_path = self._process_entry(entry, conversion_config)
                output_paths.append(output_path)
                logger.info(f"Successfully converted: {entry.data_path} -> {output_path}")
            except Exception as e:
                logger.error(f"Error processing {entry.data_path}: {e}")
                raise
        
        return output_paths

    def _process_entry(
        self,
        entry: DataEntry,
        conversion_config: ConversionConfig
    ) -> Path:
        """
        Process a single data entry through the pipeline.
        
        Pipeline: Parse → Detect Styling → Convert Styling → Transform → Write
        """
        input_path = Path(entry.data_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Step 1: Parse file to IR
        file_format = entry.format or detect_format(input_path)
        if not file_format:
            raise ValueError(f"Could not detect format for {input_path}")
        
        parser_class = parser_registry.get(file_format)
        if not parser_class:
            raise ValueError(f"No parser found for format: {file_format}")
        
        parser = parser_class()
        ir = parser.parse(input_path)
        logger.debug(f"Parsed {len(ir)} samples from {input_path}")
        
        # Step 2: Detect source styling if not specified
        source_styling = entry.styling
        if not source_styling and ir.samples:
            source_styling = detect_styling(ir.samples[0].data)
            logger.debug(f"Detected source styling: {source_styling}")
        
        # Step 3: Convert styling if needed
        if source_styling and source_styling != conversion_config.target_styling:
            ir = self._convert_styling(ir, source_styling, conversion_config.target_styling)
        elif not source_styling:
            # No source styling detected, convert from raw IR
            ir = self._apply_target_styling(ir, conversion_config.target_styling)
        
        # Step 4: Apply transformations
        if conversion_config.transformations:
            ir = self._apply_transformations(ir, conversion_config.transformations)
        
        # Step 5: Write to output file
        output_path = get_output_path(
            input_path,
            conversion_config.target_styling,
            conversion_config.target_format,
            conversion_config.output_mode
        )
        
        writer_class = writer_registry.get(conversion_config.target_format)
        if not writer_class:
            raise ValueError(f"No writer found for format: {conversion_config.target_format}")
        
        writer = writer_class()
        writer.write(ir, output_path)
        
        return output_path

    def _convert_styling(
        self,
        ir: IntermediateRepresentation,
        source_styling: str,
        target_styling: str
    ) -> IntermediateRepresentation:
        """Convert from source styling to target styling."""
        # Get styling converters
        source_converter_class = styling_registry.get(source_styling)
        target_converter_class = styling_registry.get(target_styling)
        
        if not source_converter_class or not target_converter_class:
            logger.warning(f"Missing converter, keeping original styling")
            return ir
        
        source_converter = source_converter_class()
        target_converter = target_converter_class()
        
        # Convert: source styling → IR → target styling
        new_ir = IntermediateRepresentation(
            source_format=ir.source_format,
            source_styling=target_styling,
            metadata=ir.metadata
        )
        
        for sample in ir.samples:
            # Sample is already in IR, but may need styling conversion
            converted_data = target_converter.from_ir(sample)
            new_ir.add_sample(converted_data, metadata=sample.metadata)
        
        return new_ir

    def _apply_target_styling(
        self,
        ir: IntermediateRepresentation,
        target_styling: str
    ) -> IntermediateRepresentation:
        """Apply target styling to raw IR data."""
        target_converter_class = styling_registry.get(target_styling)
        if not target_converter_class:
            raise ValueError(f"No styling converter found for: {target_styling}")
        
        target_converter = target_converter_class()
        
        new_ir = IntermediateRepresentation(
            source_format=ir.source_format,
            source_styling=target_styling,
            metadata=ir.metadata
        )
        
        for sample in ir.samples:
            converted_data = target_converter.from_ir(sample)
            new_ir.add_sample(converted_data, metadata=sample.metadata)
        
        return new_ir

    def _apply_transformations(
        self,
        ir: IntermediateRepresentation,
        transformations: List[Dict[str, Any]]
    ) -> IntermediateRepresentation:
        """Apply a chain of transformations to IR."""
        current_ir = ir
        
        for transform_config in transformations:
            transform_type = transform_config.get("type")
            if not transform_type:
                logger.warning("Transformation missing 'type' field, skipping")
                continue
            
            transformer_class = transformer_registry.get(transform_type)
            if not transformer_class:
                logger.warning(f"No transformer found for type: {transform_type}, skipping")
                continue
            
            config = transform_config.get("config", {})
            transformer = transformer_class(config=config)
            current_ir = transformer.transform(current_ir)
            logger.debug(f"Applied transformation: {transform_type}")
        
        return current_ir
