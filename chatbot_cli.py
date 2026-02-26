"""Simple command-line RAG chatbot for RuneScape Wiki."""

import os
import sys
import argparse
os.environ["CUDA_VISIBLE_DEVICES"] = ""

def main():
    parser = argparse.ArgumentParser(description="RuneScape Wiki RAG Chatbot")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (show retrieved context, Ollama details)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("RuneScape Wiki Chatbot")
    if args.debug:
        print("DEBUG MODE ENABLED")
    print("=" * 60)
    print("Loading RAG engine (this may take 10-30 seconds)...")
    print("(Note: First import may be slow on OneDrive/WSL filesystem)")
    
    try:
        # Import here to defer slow imports until needed
        from rag_engine import RAGEngine
        engine = RAGEngine()
        print("✓ RAG engine loaded!\n")
    except Exception as e:
        print(f"✗ Error loading RAG engine: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you've run: python indexer.py")
        print("2. Check that ChromaDB exists at: assets/chroma_db")
        print("3. Verify Ollama is running: ollama list")
        return
    
    print("Ask questions about RuneScape! Type 'quit' or 'exit' to stop.")
    if args.debug:
        print("Debug mode: Will show retrieved context and Ollama request details.\n")
    else:
        print()
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            result = engine.query(question, debug=args.debug)
            
            print(f"\nBot: {result['answer']}\n")
            
            if result['sources']:
                print("Sources:")
                for source in result['sources']:
                    print(f"  - {source['title']}: {source['url']}")
                print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")
            if args.debug:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()

