"""Multi-stage reverse parser implementation.

This module implements a PyYAML-inspired pipeline architecture:
    Scanner → MessageParser → MessageComposer → Canonical Messages

The separation of concerns enables:
- Testability: Each stage can be unit tested independently
- Extensibility: Swap components without changing core logic
- Debuggability: Inspect intermediate tokens/blocks
"""

from typing import List, Dict
from dataclasses import dataclass

from .template_spec import ChatTemplateSpec
from .exceptions import (
    UnknownDelimiterError,
    NestedBlockError,
    UnclosedBlockError,
    EmptyContentError,
    MalformedTemplateError,
)


@dataclass
class Token:
    """
    Represents a delimiter token found in rendered text.
    
    Attributes:
        type: 'start' or 'end'
        role: Role this delimiter represents
        position: Character position in source text
        delimiter: The actual delimiter string
    """
    type: str  # 'start' or 'end'
    role: str
    position: int
    delimiter: str


class Scanner:
    """
    Tokenizes rendered text by identifying delimiter boundaries.
    
    First stage in the parsing pipeline. Scans the input text and produces
    a stream of tokens representing delimiter positions.
    """
    
    def __init__(self, template_spec: ChatTemplateSpec):
        """
        Initialize scanner with template specification.
        
        Args:
            template_spec: Template defining delimiters to scan for
        """
        self.template_spec = template_spec
        
    def scan(self, text: str) -> List[Token]:
        """
        Scan text and produce delimiter tokens.
        
        Args:
            text: Rendered chat template text to scan
            
        Returns:
            Ordered list of Token objects sorted by position
        """
        tokens = []
        
        # First, detect if we have shared end delimiters
        # (same end delimiter used by multiple roles)
        end_delimiter_to_roles = {}
        for delimiter_spec in self.template_spec.delimiters:
            if delimiter_spec.end_delimiter:
                if delimiter_spec.end_delimiter not in end_delimiter_to_roles:
                    end_delimiter_to_roles[delimiter_spec.end_delimiter] = []
                end_delimiter_to_roles[delimiter_spec.end_delimiter].append(delimiter_spec.role)
        
        # Track which end delimiters are shared (used by multiple roles)
        shared_end_delimiters = {
            delim: roles for delim, roles in end_delimiter_to_roles.items()
            if len(roles) > 1
        }
        
        for delimiter_spec in self.template_spec.delimiters:
            # Find all occurrences of start delimiter
            start_positions = self._find_all(text, delimiter_spec.start_delimiter)
            for pos in start_positions:
                tokens.append(Token(
                    type='start',
                    role=delimiter_spec.role,
                    position=pos,
                    delimiter=delimiter_spec.start_delimiter
                ))
            
            # Find all occurrences of end delimiter (if present)
            if delimiter_spec.end_delimiter:
                # Only add end tokens once if it's shared across roles
                if delimiter_spec.end_delimiter in shared_end_delimiters:
                    # Skip this - we'll add it separately
                    continue
                    
                end_positions = self._find_all(text, delimiter_spec.end_delimiter)
                for pos in end_positions:
                    tokens.append(Token(
                        type='end',
                        role=delimiter_spec.role,
                        position=pos,
                        delimiter=delimiter_spec.end_delimiter
                    ))
        
        # Add shared end delimiters (not role-specific)
        for shared_delim in shared_end_delimiters:
            end_positions = self._find_all(text, shared_delim)
            for pos in end_positions:
                # Use empty string for role to indicate it's shared
                tokens.append(Token(
                    type='end',
                    role='',  # No specific role - will match any open block
                    position=pos,
                    delimiter=shared_delim
                ))
        
        # Sort by position to maintain document order
        tokens.sort(key=lambda t: t.position)
        return tokens
    
    def _find_all(self, text: str, pattern: str) -> List[int]:
        """
        Find all positions of pattern in text.
        
        Args:
            text: Text to search in
            pattern: Pattern to search for
            
        Returns:
            List of starting positions where pattern was found
        """
        positions = []
        start = 0
        while True:
            pos = text.find(pattern, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1  # Continue searching after this occurrence
        return positions


@dataclass
class MessageBlock:
    """
    Intermediate representation of a message block.
    
    Represents a parsed message block with its content boundaries.
    
    Attributes:
        role: Message role (user, assistant, system, etc.)
        content_start: Start position of message content
        content_end: End position of message content
        start_token: Token that started this block
        end_token: Token that ended this block (None for prefix-only)
    """
    role: str
    content_start: int
    content_end: int
    start_token: Token
    end_token: Token = None


class MessageParser:
    """
    Parses token stream into message blocks.
    
    Second stage in the parsing pipeline. Takes tokens from Scanner
    and validates structure while extracting message boundaries.
    """
    
    def __init__(self, template_spec: ChatTemplateSpec):
        """
        Initialize parser with template specification.
        
        Args:
            template_spec: Template defining parsing rules
        """
        self.template_spec = template_spec
        
    def parse(self, text: str, tokens: List[Token]) -> List[MessageBlock]:
        """
        Parse tokens into message blocks.
        
        Validates:
        - Properly paired delimiters
        - No overlapping blocks (unless nesting allowed)
        - No unexpected nesting
        
        Args:
            text: Original source text (for position validation)
            tokens: Token stream from Scanner
            
        Returns:
            List of MessageBlock objects
            
        Raises:
            NestedBlockError: If nested blocks detected when not allowed
            UnclosedBlockError: If block started but not closed
            MalformedTemplateError: If delimiter pairing is invalid
        """
        blocks = []
        stack = []  # Stack to track open blocks
        
        for token in tokens:
            if token.type == 'start':
                # Check for invalid nesting
                if stack and not self.template_spec.allow_nesting:
                    raise NestedBlockError(
                        f"Nested message blocks detected at position {token.position}. "
                        f"Open block for role '{stack[-1].role}' at position {stack[-1].position}, "
                        f"new block for role '{token.role}' at position {token.position}"
                    )
                stack.append(token)
                
            elif token.type == 'end':
                if not stack:
                    raise UnclosedBlockError(
                        f"Unmatched end delimiter '{token.delimiter}' at position {token.position}. "
                        f"No corresponding start delimiter found."
                    )
                
                start_token = stack.pop()
                
                # For shared end delimiters (like <|im_end|>), role doesn't matter
                # Just verify the delimiter strings match the template spec
                delimiter_spec = self.template_spec.get_delimiter_for_role(start_token.role)
                if delimiter_spec and delimiter_spec.end_delimiter:
                    # If end delimiter is specified for this role, check it matches
                    if token.delimiter != delimiter_spec.end_delimiter:
                        # This end token doesn't match the expected end for this role
                        # Put start token back on stack and skip this end token
                        stack.append(start_token)
                        continue
                
                # Calculate content positions
                content_start = start_token.position + len(start_token.delimiter)
                content_end = token.position
                
                blocks.append(MessageBlock(
                    role=start_token.role,
                    content_start=content_start,
                    content_end=content_end,
                    start_token=start_token,
                    end_token=token
                ))
        
        # Check for unclosed blocks
        if stack:
            unclosed = stack[-1]
            raise UnclosedBlockError(
                f"Unclosed message block for role '{unclosed.role}' "
                f"starting at position {unclosed.position}. "
                f"Expected closing delimiter '{self.template_spec.get_delimiter_for_role(unclosed.role).end_delimiter}'"
            )
        
        return blocks


class MessageComposer:
    """
    Composes canonical messages from message blocks.
    
    Third stage in the parsing pipeline. Takes validated message blocks
    and produces the final canonical message format.
    """
    
    def __init__(self, template_spec: ChatTemplateSpec, 
                 allow_empty_content: bool = False):
        """
        Initialize composer with template specification.
        
        Args:
            template_spec: Template defining composition rules
            allow_empty_content: Whether to allow messages with empty content
        """
        self.template_spec = template_spec
        self.allow_empty_content = allow_empty_content
        
    def compose(self, text: str, blocks: List[MessageBlock]) -> List[Dict[str, str]]:
        """
        Compose canonical message list from blocks.
        
        Args:
            text: Original source text
            blocks: Validated message blocks from MessageParser
            
        Returns:
            List of {"role": str, "content": str} dicts in canonical format
            
        Raises:
            EmptyContentError: If empty content found and not allowed
        """
        messages = []
        
        for block in blocks:
            # Extract content using block boundaries
            content = text[block.content_start:block.content_end]
            
            # Normalize whitespace if configured
            if self.template_spec.normalize_whitespace:
                content = self._normalize_whitespace(content)
            
            # Check empty content policy
            if not content.strip() and not self.allow_empty_content:
                raise EmptyContentError(
                    f"Empty content for role '{block.role}' at position {block.start_token.position}. "
                    f"Set allow_empty_content=True to permit empty messages."
                )
            
            messages.append({
                "role": block.role,
                "content": content
            })
        
        return messages
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace while preserving content structure.
        
        - Strips leading/trailing whitespace
        - Preserves newlines for multi-line content
        - Removes empty lines
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Normalize internal whitespace (preserve newlines for structure)
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines while preserving content structure
        return '\n'.join(line for line in lines if line)


class ReverseParser:
    """
    High-level reverse parser orchestrating the multi-stage pipeline.
    
    Pipeline: Scanner → MessageParser → MessageComposer → Canonical Messages
    
    This class provides the main API for reverse parsing rendered chat
    template text back into canonical message structures.
    
    Example:
        >>> from data_formatter.reverse_parser import ReverseParser
        >>> from data_formatter.reverse_parser.templates.chatml import CHATML_TEMPLATE
        >>> 
        >>> parser = ReverseParser(CHATML_TEMPLATE)
        >>> rendered = "<|im_start|>user\\nHello<|im_end|>"
        >>> messages = parser.parse(rendered)
        >>> print(messages)
        [{"role": "user", "content": "Hello"}]
    """
    
    def __init__(self, template_spec: ChatTemplateSpec, 
                 allow_empty_content: bool = False):
        """
        Initialize reverse parser with template specification.
        
        Args:
            template_spec: Template contract defining delimiters and parsing rules
            allow_empty_content: Whether to allow messages with empty content
        """
        self.template_spec = template_spec
        self.scanner = Scanner(template_spec)
        self.parser = MessageParser(template_spec)
        self.composer = MessageComposer(template_spec, allow_empty_content)
    
    def parse(self, rendered_text: str) -> List[Dict[str, str]]:
        """
        Parse rendered chat template text into canonical messages.
        
        This is the main entry point for reverse parsing. It orchestrates
        the three-stage pipeline:
        1. Scanner: Tokenize delimiters
        2. MessageParser: Extract and validate message blocks
        3. MessageComposer: Build canonical message structures
        
        Args:
            rendered_text: Text rendered by a chat template
            
        Returns:
            List of canonical messages in format [{"role": str, "content": str}, ...]
            Messages are returned in the order they appear in the source text.
            
        Raises:
            UnknownDelimiterError: If no valid delimiters found in text
            NestedBlockError: If nested blocks detected when not allowed
            UnclosedBlockError: If message block started but not closed
            MalformedTemplateError: If template structure is invalid
            EmptyContentError: If empty content found and not allowed
            
        Example:
            >>> parser = ReverseParser(CHATML_TEMPLATE)
            >>> text = '''<|im_start|>user
            ... Hello, how are you?<|im_end|>
            ... <|im_start|>assistant
            ... I'm doing great!<|im_end|>'''
            >>> messages = parser.parse(text)
            >>> len(messages)
            2
            >>> messages[0]["role"]
            'user'
        """
        # Validate input
        if not rendered_text:
            raise ValueError("Cannot parse empty text")
        
        # Stage 1: Scan for delimiter tokens
        tokens = self.scanner.scan(rendered_text)
        
        if not tokens:
            raise UnknownDelimiterError(
                f"No valid delimiters found in rendered text. "
                f"Expected delimiters from template '{self.template_spec.name}': "
                f"{[spec.start_delimiter for spec in self.template_spec.delimiters]}"
            )
        
        # Stage 2: Parse tokens into message blocks
        blocks = self.parser.parse(rendered_text, tokens)
        
        # Stage 3: Compose canonical messages
        messages = self.composer.compose(rendered_text, blocks)
        
        return messages
