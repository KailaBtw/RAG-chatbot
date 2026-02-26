"""Minimal wikitext preprocessing for RAG indexing."""

import re


def clean_wikitext(wikitext: str) -> str:
    """
    Clean MediaWiki markup with minimal processing.
    
    Strategy: Remove obvious noise, keep all content (metadata, descriptions, etc.)
    
    Args:
        wikitext: Raw MediaWiki markup text
        
    Returns:
        Cleaned text suitable for embedding
    """
    text = wikitext
    
    # Remove no-content templates (just markers, no actual content)
    text = re.sub(r'\{\{External\|os\}\}', '', text)
    text = re.sub(r'\{\{Disambig\}\}', '', text)
    text = re.sub(r'\{\{Disambiguation\}\}', '', text)
    
    # Convert links: [[link|display]] -> display
    text = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', r'\2', text)
    # Convert simple links: [[link]] -> link
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    
    # Remove file/image references (keep alt text if present)
    text = re.sub(r'\[\[File:[^\]]+\]\]', '', text)
    text = re.sub(r'\[\[Image:[^\]]+\]\]', '', text)
    
    # Remove HTML tags but keep content
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace: multiple newlines/spaces -> single space
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces -> single space
    text = re.sub(r' *\n *', '\n', text)  # Spaces around newlines
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

