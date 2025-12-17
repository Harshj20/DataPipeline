"""Template specification for reversible chat templates."""

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class DelimiterSpec:
    """
    Specification for a role-specific delimiter pair.
    
    Attributes:
        role: The role this delimiter represents (e.g., "user", "assistant", "system")
        start_delimiter: The starting delimiter string
        end_delimiter: Optional ending delimiter. If None, delimiter is prefix-only
    
    Examples:
        >>> # ChatML style with paired delimiters
        >>> DelimiterSpec(role="user", start_delimiter="<|im_start|>user\\n", 
        ...               end_delimiter="<|im_end|>")
        
        >>> # Prefix-only delimiter
        >>> DelimiterSpec(role="user", start_delimiter="User: ", end_delimiter=None)
    """
    role: str
    start_delimiter: str
    end_delimiter: Optional[str] = None
    
    def __post_init__(self):
        """Validate delimiter specification."""
        if not self.role:
            raise ValueError("Role cannot be empty")
        if not self.start_delimiter:
            raise ValueError("Start delimiter cannot be empty")


@dataclass
class ChatTemplateSpec:
    """
    Contract for a reversible chat template.
    
    A reversible template must declare:
    - Start delimiter per role
    - Optional end delimiter per role
    - Whether delimiters are paired or prefix-only
    - Whether nested messages are allowed (default: false)
    
    Attributes:
        name: Template name (e.g., "chatml", "llama2")
        delimiters: List of delimiter specifications for each role
        allow_nesting: Whether nested message blocks are permitted
        normalize_whitespace: Whether to normalize whitespace in content
    
    Examples:
        >>> # ChatML template
        >>> ChatTemplateSpec(
        ...     name="chatml",
        ...     delimiters=[
        ...         DelimiterSpec(role="user", start_delimiter="<|im_start|>user\\n",
        ...                      end_delimiter="<|im_end|>"),
        ...         DelimiterSpec(role="assistant", start_delimiter="<|im_start|>assistant\\n",
        ...                      end_delimiter="<|im_end|>"),
        ...     ]
        ... )
    """
    name: str
    delimiters: List[DelimiterSpec]
    allow_nesting: bool = False
    normalize_whitespace: bool = True
    
    def __post_init__(self):
        """Validate template specification."""
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.delimiters:
            raise ValueError("Template must have at least one delimiter specification")
        
        # Validate template is reversible
        self.validate()
    
    def validate(self) -> None:
        """
        Validate that the template is reversible.
        
        Checks:
        - Start delimiters are unique (critical for disambiguation)
        - Start/end delimiters don't overlap in ambiguous ways
        - Role names are consistent
        
        Note: End delimiters CAN be shared (e.g., ChatML uses <|im_end|> for all roles)
        because role is determined by the start delimiter.
        
        Raises:
            ValueError: If template violates reversibility constraints
        """
        # Check for unique start delimiters (CRITICAL)
        start_delimiters: Set[str] = set()
        for spec in self.delimiters:
            if spec.start_delimiter in start_delimiters:
                raise ValueError(
                    f"Duplicate start delimiter '{spec.start_delimiter}' "
                    f"in template '{self.name}'. Start delimiters must be unique."
                )
            start_delimiters.add(spec.start_delimiter)
        
        # Check for delimiter substring conflicts that would cause ambiguity
        # Only check start delimiters against each other, and start vs end
        all_delimiters = list(start_delimiters)
        
        # Add unique end delimiters to check
        seen_end_delims = set()
        for spec in self.delimiters:
            if spec.end_delimiter and spec.end_delimiter not in seen_end_delims:
                all_delimiters.append(spec.end_delimiter)
                seen_end_delims.add(spec.end_delimiter)
        
        # Check for substring conflicts between different delimiter types
        for i, delim1 in enumerate(all_delimiters):
            for delim2 in all_delimiters[i+1:]:
                # Only flag if one delimiter is a substring of another
                # This would make parsing ambiguous
                if delim1 != delim2 and (delim1 in delim2 or delim2 in delim1):
                    raise ValueError(
                        f"Delimiter conflict: '{delim1}' and '{delim2}' overlap "
                        f"in template '{self.name}'. One delimiter contains the other, "
                        f"which makes parsing ambiguous."
                    )
    
    def get_delimiter_for_role(self, role: str) -> Optional[DelimiterSpec]:
        """
        Get the delimiter specification for a given role.
        
        Args:
            role: The role to look up
            
        Returns:
            DelimiterSpec if found, None otherwise
        """
        for spec in self.delimiters:
            if spec.role == role:
                return spec
        return None
    
    def get_all_roles(self) -> List[str]:
        """Get list of all supported roles in this template."""
        return [spec.role for spec in self.delimiters]
