from __future__ import annotations
import re
from typing import List


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace.
    
    Args:
        text: Raw text input with potential multiple spaces/newlines.
        
    Returns:
        Normalized text with single spaces and no leading/trailing whitespace.
    """
    return re.sub(r"\s+", " ", text.strip())


def contains_any(text: str, terms: List[str]) -> bool:
    """Check if text contains any of the given terms (case-insensitive).
    
    Args:
        text: Text to search.
        terms: List of terms to search for.
        
    Returns:
        True if any term is found (case-insensitive), False otherwise.
    """
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def keyword_hits(text: str, terms: List[str]) -> List[str]:
    """Find all matching terms in text (case-insensitive).
    
    Args:
        text: Text to search.
        terms: List of terms to search for.
        
    Returns:
        List of terms found in the text (case-insensitive).
    """
    lower = text.lower()
    return [term for term in terms if term.lower() in lower]
