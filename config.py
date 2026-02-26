"""Configuration constants for RAG chatbot."""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data paths
JSON_DATA_PATH = BASE_DIR / "assets" / "runescape_top100.json"
CHROMA_DB_PATH = BASE_DIR / "assets" / "chroma_db"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "llama3.1:8b"

# Retrieval settings
TOP_K = 5  # Number of pages to retrieve per query

# Wiki URL base
WIKI_BASE_URL = "https://runescape.wiki/w"

