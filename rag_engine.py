"""RAG engine for querying RuneScape wiki using ChromaDB and Ollama."""

import os
import json
from typing import List

# Suppress CUDA warnings early
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import chromadb
import requests
from chromadb.config import Settings

from config import (
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TOP_K,
)


class RAGEngine:
    """RAG engine for answering questions about RuneScape wiki."""
    
    def __init__(self):
        """Initialize RAG engine with ChromaDB and embedding model."""
        import os
        # Hide GPU warnings
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
        print("Initializing RAG engine...")
        
        # Load embedding model (import here to avoid slow OneDrive filesystem on import)
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Connect to ChromaDB
        print(f"Connecting to ChromaDB at {CHROMA_DB_PATH}")
        if not CHROMA_DB_PATH.exists():
            raise FileNotFoundError(
                f"ChromaDB not found at {CHROMA_DB_PATH}. "
                "Run 'python indexer.py' first to create the index."
            )
        
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection("runescape_wiki")
        except Exception as e:
            raise ValueError(
                f"Collection 'runescape_wiki' not found. "
                "Run 'python indexer.py' first to create the index."
            ) from e
        
        # Check Ollama connection
        print("Checking Ollama connection...")
        self._check_ollama_connection()
        
        print("✓ RAG engine initialized")
    
    def _check_ollama_connection(self):
        """Check if Ollama is running and the model is available."""
        try:
            # Quick health check
            response = requests.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if OLLAMA_MODEL not in model_names:
                print(f"⚠ Warning: Model '{OLLAMA_MODEL}' not found in Ollama.")
                print(f"  Available models: {', '.join(model_names) if model_names else 'None'}")
                print(f"  To install: ollama pull {OLLAMA_MODEL}")
            else:
                print(f"✓ Ollama is running and model '{OLLAMA_MODEL}' is available")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
                "Make sure Ollama is running. On Windows, check Windows Services. "
                "On Linux/WSL, run 'ollama serve' in a separate terminal."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Ollama at {OLLAMA_BASE_URL} did not respond within 5 seconds. "
                "The service may be overloaded or not running properly."
            )
        except Exception as e:
            print(f"⚠ Warning: Could not verify Ollama connection: {e}")
            print("  Continuing anyway, but queries may fail...")
    
    def query(self, question: str, top_k: int = TOP_K, debug: bool = False) -> dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            top_k: Number of pages to retrieve
            debug: If True, print debug information
            
        Returns:
            Dict with 'answer' and 'sources' (list of {title, url})
        """
        if debug:
            print(f"[DEBUG] Query: {question}")
            print(f"[DEBUG] Retrieving top {top_k} documents...")
        
        # Embed question
        query_embedding = self.embedding_model.encode([question], device="cpu")[0]
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Extract results
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [None] * len(documents)
        
        if debug:
            print(f"[DEBUG] Retrieved {len(documents)} documents:")
            for i, (doc, metadata, dist) in enumerate(zip(documents, metadatas, distances)):
                print(f"  [{i+1}] {metadata['title']} (distance: {dist:.4f if dist else 'N/A'})")
                print(f"      Preview: {doc[:100]}...")
        
        # Format context from retrieved pages
        context_parts = []
        sources = []
        
        for doc, metadata in zip(documents, metadatas):
            title = metadata["title"]
            url = metadata["wiki_url"]
            
            context_parts.append(f"=== {title} ===\n{doc}")
            sources.append({"title": title, "url": url})
        
        context = "\n\n".join(context_parts)
        
        if debug:
            print(f"[DEBUG] Context length: {len(context)} characters")
            print(f"[DEBUG] Sending request to Ollama at {OLLAMA_BASE_URL}...")
        else:
            print("Generating answer (this may take 10-30 seconds)...")
        
        # Generate answer using Ollama
        answer = self._generate_answer(context, question, debug=debug)
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def _generate_answer(self, context: str, question: str, debug: bool = False) -> str:
        """
        Generate answer using Ollama LLM.
        
        Args:
            context: Retrieved wiki page content
            question: User's question
            debug: If True, print debug information
            
        Returns:
            Generated answer
        """
        prompt = f"""You are a helpful assistant answering questions about RuneScape based on the wiki content below.

Context from RuneScape Wiki:
{context}

Question: {question}

Answer the question based on the context above. If the answer is not in the context, say so. Be concise and accurate."""

        if debug:
            print(f"[DEBUG] Prompt length: {len(prompt)} characters")
            print(f"[DEBUG] Model: {OLLAMA_MODEL}")
            print(f"[DEBUG] Timeout: 120 seconds")
            print(f"[DEBUG] Making POST request to {OLLAMA_BASE_URL}/api/generate...")
        
        try:
            # Use timeout tuple: (connect_timeout, read_timeout)
            # 10 seconds to connect, 120 seconds to read response
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=(10, 120)  # (connect timeout, read timeout)
            )
            response.raise_for_status()
            result = response.json()
            
            if debug:
                print(f"[DEBUG] Ollama response received")
                if "done" in result:
                    print(f"[DEBUG] Response done: {result.get('done', False)}")
            
            answer = result.get("response", "Sorry, I couldn't generate an answer.")
            if not answer or answer.strip() == "":
                return "Sorry, I received an empty response from Ollama."
            return answer
            
        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"Cannot connect to Ollama at {OLLAMA_BASE_URL}.\n"
                "Possible causes:\n"
                "  1. Ollama is not running (check Windows Services or run 'ollama serve')\n"
                "  2. Ollama is running on a different port\n"
                "  3. Firewall is blocking the connection"
            )
            if debug:
                error_msg += f"\n[DEBUG] Full error: {str(e)}"
            return error_msg
        except requests.exceptions.Timeout as e:
            error_msg = (
                f"Ollama request timed out after 120 seconds.\n"
                "The model might be too slow, the context too large, or Ollama is overloaded.\n"
                "Try:\n"
                "  1. Using a smaller model\n"
                "  2. Reducing TOP_K in config.py\n"
                "  3. Checking if Ollama is processing other requests"
            )
            if debug:
                error_msg += f"\n[DEBUG] Full error: {str(e)}"
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Ollama: {str(e)}\nMake sure Ollama is running at {OLLAMA_BASE_URL}"
            if debug:
                error_msg += f"\n[DEBUG] Full error: {str(e)}"
                import traceback
                error_msg += f"\n[DEBUG] Traceback:\n{traceback.format_exc()}"
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if debug:
                import traceback
                error_msg += f"\n[DEBUG] Traceback:\n{traceback.format_exc()}"
            return error_msg

