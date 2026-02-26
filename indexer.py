"""Index RuneScape wiki pages into ChromaDB for RAG retrieval."""

import json
import urllib.parse
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    JSON_DATA_PATH,
    WIKI_BASE_URL,
)
from preprocess import clean_wikitext


def load_wiki_pages(json_path: Path) -> list[dict]:
    """Load wiki pages from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_wiki_url(title: str) -> str:
    """Create wiki URL from page title."""
    # URL encode the title (spaces -> underscores, special chars encoded)
    encoded_title = urllib.parse.quote(title.replace(" ", "_"), safe="")
    return f"{WIKI_BASE_URL}/{encoded_title}"


def index_pages(pages: list[dict], chroma_path: Path, embedding_model_name: str):
    """
    Index wiki pages into ChromaDB.
    
    Uses full-page chunks: one chunk = one page.
    """
    print(f"Loading embedding model: {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)
    
    print(f"Initializing ChromaDB at {chroma_path}")
    chroma_path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="runescape_wiki",
        metadata={"description": "RuneScape Wiki pages for RAG"}
    )
    
    # Process pages
    print(f"Processing {len(pages)} pages...")
    documents = []
    metadatas = []
    ids = []
    
    for i, page in enumerate(pages):
        title = page["title"]
        wikitext = page["wikitext"]
        
        # Clean wikitext
        cleaned_text = clean_wikitext(wikitext)
        
        # Full-page chunk (no splitting)
        documents.append(cleaned_text)
        metadatas.append({
            "title": title,
            "wiki_url": create_wiki_url(title),
        })
        ids.append(f"page_{i}")
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(pages)} pages...")
    
    print("Generating embeddings...")
    embeddings = embedding_model.encode(documents, show_progress_bar=True, device="cpu")
    
    print("Storing in ChromaDB...")
    collection.add(
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✓ Indexed {len(pages)} pages into ChromaDB")
    print(f"  Collection: {collection.name}")
    print(f"  Location: {chroma_path}")


def main():
    """Main entry point for indexing."""
    print("=" * 60)
    print("RuneScape Wiki RAG Indexer")
    print("=" * 60)
    
    # Load pages
    print(f"Loading pages from {JSON_DATA_PATH}...")
    pages = load_wiki_pages(JSON_DATA_PATH)
    print(f"Loaded {len(pages)} pages")
    
    # Index pages
    index_pages(pages, CHROMA_DB_PATH, EMBEDDING_MODEL)
    
    print("\nIndexing complete!")


if __name__ == "__main__":
    main()

